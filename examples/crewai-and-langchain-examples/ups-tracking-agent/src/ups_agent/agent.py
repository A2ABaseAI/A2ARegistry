"""CrewAI agent for UPS shipment tracking."""

import asyncio
import json
import logging
import re
from typing import List, Optional

from crewai import Agent, Crew, Task
from crewai.tools import BaseTool

from .client import UPSClient, UPSCredentialsError, UPSTrackingError
from .models import ShipmentStatus
from .normalizer import UPSNormalizer

logger = logging.getLogger(__name__)


class UPSTrackingTool(BaseTool):
    """CrewAI tool for tracking UPS shipments."""
    
    name: str = "track_ups"
    description: str = "Track UPS shipments by tracking number(s). Returns normalized shipment status information."
    
    def __init__(self, client: UPSClient, normalizer: UPSNormalizer):
        """Initialize UPS tracking tool."""
        super().__init__()
        self.client = client
        self.normalizer = normalizer
    
    def _run(self, tracking_numbers: List[str]) -> str:
        """Synchronous wrapper for async tracking."""
        return asyncio.run(self._arun(tracking_numbers))
    
    async def _arun(self, tracking_numbers: List[str]) -> str:
        """Track UPS shipments asynchronously."""
        try:
            if not tracking_numbers:
                return "No tracking numbers provided."
            
            # Track shipments
            ups_responses = await self.client.track_multiple(tracking_numbers)
            
            # Normalize responses
            shipment_statuses = self.normalizer.normalize_multiple(ups_responses)
            
            # Format response
            if len(shipment_statuses) == 1:
                status = shipment_statuses[0]
                return f"Tracking {status.tracking_number}: {status.explain()}"
            else:
                results = []
                for status in shipment_statuses:
                    results.append(f"• {status.tracking_number}: {status.status_text}")
                    if status.estimated_delivery:
                        results.append(f"  ETA: {status.estimated_delivery.strftime('%Y-%m-%d at %I:%M %p')}")
                    elif status.delivered_at:
                        results.append(f"  Delivered: {status.delivered_at.strftime('%Y-%m-%d at %I:%M %p')}")
                
                return "\\n".join(results)
                
        except UPSCredentialsError as e:
            logger.error(f"UPS credentials error: {e}")
            return f"UPS API authentication failed: {str(e)}"
        except UPSTrackingError as e:
            logger.error(f"UPS tracking error: {e}")
            return f"UPS tracking failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in UPS tracking: {e}")
            return f"Error tracking shipments: {str(e)}"


class UPSStatusAgent:
    """CrewAI agent for UPS shipment status checking."""
    
    def __init__(
        self,
        client: UPSClient,
        normalizer: UPSNormalizer,
        model: Optional[str] = None,
        temperature: float = 0.1,
    ):
        """Initialize UPS status agent."""
        self.client = client
        self.normalizer = normalizer
        self.model = model
        self.temperature = temperature
        
        # Create tracking tool
        self.tracking_tool = UPSTrackingTool(client, normalizer)
        
        # Create CrewAI agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create CrewAI agent with UPS expertise."""
        return Agent(
            role="UPS Shipping Expert",
            goal="Provide accurate, helpful information about UPS shipment status and tracking",
            backstory="""You are an expert in UPS parcel logistics and shipping operations. 
            You understand UPS terminology, tracking processes, and common shipping scenarios.
            You provide clear, factual answers about shipment status and helpful guidance for next steps.
            You always prioritize accuracy and customer service.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.tracking_tool],
            llm_kwargs={
                "model": self.model or "gpt-4o-mini",
                "temperature": self.temperature,
            } if self.model else {"temperature": self.temperature},
        )
    
    def _extract_tracking_numbers(self, text: str) -> List[str]:
        """Extract UPS tracking numbers from text."""
        # UPS tracking number patterns
        patterns = [
            r'\\b1Z[A-Z0-9]{16}\\b',  # Standard 1Z format
            r'\\b1M[A-Z0-9]{16}\\b',  # 1M format
            r'\\b[A-Z0-9]{18}\\b',     # General 18-char alphanumeric
            r'\\b[A-Z0-9]{10,30}\\b', # Flexible length
        ]
        
        tracking_numbers = []
        text_upper = text.upper()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_upper)
            tracking_numbers.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_numbers = []
        for tn in tracking_numbers:
            if tn not in seen:
                seen.add(tn)
                unique_numbers.append(tn)
        
        return unique_numbers
    
    def _is_pure_tracking_numbers(self, text: str) -> bool:
        """Check if text contains only tracking numbers."""
        tracking_numbers = self._extract_tracking_numbers(text)
        if not tracking_numbers:
            return False
        
        # Remove tracking numbers from text and check if anything remains
        remaining_text = text
        for tn in tracking_numbers:
            remaining_text = remaining_text.replace(tn, "").replace(tn.lower(), "")
        
        # Clean up whitespace and common separators
        remaining_text = re.sub(r'[\\s,\\n]+', ' ', remaining_text).strip()
        
        # If only separators remain, it's pure tracking numbers
        return len(remaining_text) < 10  # Allow some flexibility
    
    async def track_shipments(self, tracking_numbers: List[str], json_output: bool = False) -> str:
        """Track shipments directly (bypass LLM for speed)."""
        try:
            # Track shipments
            ups_responses = await self.client.track_multiple(tracking_numbers)
            
            # Normalize responses
            shipment_statuses = self.normalizer.normalize_multiple(ups_responses)
            
            if json_output:
                # Return JSON format
                return json.dumps([status.dict() for status in shipment_statuses], indent=2, default=str)
            else:
                # Return formatted text
                if len(shipment_statuses) == 1:
                    status = shipment_statuses[0]
                    return status.explain()
                else:
                    results = []
                    for status in shipment_statuses:
                        results.append(f"**{status.tracking_number}**: {status.explain()}")
                    return "\\n\\n".join(results)
                    
        except Exception as e:
            logger.error(f"Error tracking shipments directly: {e}")
            return f"Error tracking shipments: {str(e)}"
    
    async def process_query(self, query: str, json_output: bool = False) -> str:
        """Process a natural language query about UPS shipments."""
        try:
            # Extract tracking numbers from query
            tracking_numbers = self._extract_tracking_numbers(query)
            
            # If pure tracking numbers, use direct tracking for speed
            if self._is_pure_tracking_numbers(query) and tracking_numbers:
                return await self.track_shipments(tracking_numbers, json_output)
            
            # Otherwise, use CrewAI agent for natural language processing
            task = Task(
                description=f"""Process this UPS shipment query: "{query}"
                
                Instructions:
                1. Extract any UPS tracking numbers from the query
                2. Use the track_ups tool to get shipment status
                3. Provide a clear, helpful response about the shipment(s)
                4. Include estimated delivery times if available
                5. If multiple shipments, summarize each one
                6. If status is stale (>48h without movement), mention contacting UPS
                7. Be concise but informative
                
                If no tracking numbers are found, ask the user to provide them.""",
                agent=self.agent,
                expected_output="A clear, helpful response about UPS shipment status with actionable guidance.",
            )
            
            # Create crew and execute task
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True,
            )
            
            result = crew.kickoff()
            
            if json_output and tracking_numbers:
                # If JSON output requested and we have tracking numbers, get structured data
                shipment_statuses = await self._get_shipment_statuses(tracking_numbers)
                return json.dumps([status.dict() for status in shipment_statuses], indent=2, default=str)
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing query: {str(e)}"
    
    async def _get_shipment_statuses(self, tracking_numbers: List[str]) -> List[ShipmentStatus]:
        """Get structured shipment statuses for JSON output."""
        try:
            ups_responses = await self.client.track_multiple(tracking_numbers)
            return self.normalizer.normalize_multiple(ups_responses)
        except Exception as e:
            logger.error(f"Error getting shipment statuses: {e}")
            return []
