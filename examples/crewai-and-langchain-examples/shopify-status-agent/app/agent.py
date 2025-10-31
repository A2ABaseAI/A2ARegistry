"""LangChain agent for Shopify order tracking."""

import uuid
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools import BaseTool

from .llm import get_llm, get_system_prompt
from .tools.shopify import ShopifyOrderTool, ShopifyStatusTool, ShopifyTrackingTool


class ShopifyAgent:
    """Shopify order tracking agent with conversation memory."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = get_llm()
        self.tools = self._get_tools()
        self.memory_store: Dict[str, ConversationBufferMemory] = {}
        self.agent_executor = self._create_agent()
    
    def _get_tools(self) -> List[BaseTool]:
        """Get available tools."""
        return [
            ShopifyOrderTool(),
            ShopifyStatusTool(),
            ShopifyTrackingTool(),
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor."""
        prompt = get_system_prompt()
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            system_message=SystemMessage(content=prompt)
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )
    
    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        """Get or create memory for a session."""
        if session_id not in self.memory_store:
            self.memory_store[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
        return self.memory_store[session_id]
    
    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a chat message."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        memory = self.get_memory(session_id)
        
        try:
            # Run the agent with memory
            result = await self.agent_executor.ainvoke(
                {"input": message},
                config={"configurable": {"session_id": session_id}}
            )
            
            # Extract order information if found
            order_info = self._extract_order_info(result.get("output", ""))
            
            return {
                "response": result.get("output", ""),
                "session_id": session_id,
                "order_info": order_info,
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id,
                "order_info": None,
            }
    
    async def stream_chat(self, message: str, session_id: Optional[str] = None):
        """Stream chat response."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        memory = self.get_memory(session_id)
        
        try:
            # Stream the agent response
            async for chunk in self.agent_executor.astream(
                {"input": message},
                config={"configurable": {"session_id": session_id}}
            ):
                if "output" in chunk:
                    yield {
                        "type": "content",
                        "content": chunk["output"],
                        "session_id": session_id,
                    }
                elif "intermediate_steps" in chunk:
                    # Handle tool calls
                    for step in chunk["intermediate_steps"]:
                        if len(step) >= 2:
                            tool_name = step[0].tool
                            tool_result = step[1]
                            yield {
                                "type": "tool_call",
                                "tool": tool_name,
                                "result": tool_result,
                                "session_id": session_id,
                            }
            
            # Final response with order info
            final_response = await self.chat(message, session_id)
            yield {
                "type": "order_info",
                "order_info": final_response.get("order_info"),
                "session_id": session_id,
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id,
            }
    
    def _extract_order_info(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract order information from agent response."""
        # Simple extraction - in a real implementation, you might want more sophisticated parsing
        if "Found order:" in response:
            try:
                # This is a simplified extraction - in practice, you'd want more robust parsing
                import json
                import re
                
                # Look for JSON-like structure in the response
                json_match = re.search(r'Found order: ({.*})', response)
                if json_match:
                    order_data = json.loads(json_match.group(1))
                    return {
                        "order_id": order_data.get("id"),
                        "order_number": order_data.get("name"),
                        "status": order_data.get("fulfillment_status"),
                        "financial_status": order_data.get("financial_status"),
                        "tracking_number": None,  # Would need to extract from fulfillments
                    }
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return None
    
    def clear_memory(self, session_id: str) -> bool:
        """Clear memory for a session."""
        if session_id in self.memory_store:
            del self.memory_store[session_id]
            return True
        return False
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self.memory_store)


# Global agent instance
agent = ShopifyAgent()
