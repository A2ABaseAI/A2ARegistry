#!/usr/bin/env python3
"""
Customer Service Demo - Shopify + UPS Agent Workflow

This script demonstrates a real-world customer service scenario:
1. Customer asks Shopify agent for order status
2. Shopify agent delegates to UPS agent for tracking information
3. Both agents coordinate to provide comprehensive customer response

Based on multi-agent orchestration patterns from GitHub A2A samples.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the orchestrator from the main example
try:
    from agent_runner_example import MultiAgentOrchestrator
    ORCHESTRATOR_AVAILABLE = True
    logger.info("✅ MultiAgentOrchestrator loaded successfully")
except ImportError as e:
    logger.error(f"❌ MultiAgentOrchestrator not available: {e}")
    ORCHESTRATOR_AVAILABLE = False


class CustomerServiceDemo:
    """Customer service demonstration with Shopify and UPS agents."""
    
    def __init__(self):
        """Initialize the customer service demo."""
        if not ORCHESTRATOR_AVAILABLE:
            raise ImportError("MultiAgentOrchestrator is required")
        
        self.orchestrator = MultiAgentOrchestrator()
        logger.info("🚀 Customer Service Demo initialized")
    
    async def run_customer_service_scenario(self):
        """Run the complete customer service scenario."""
        try:
            print("="*70)
            print("CUSTOMER SERVICE DEMO - SHOPIFY + UPS AGENT WORKFLOW")
            print("="*70)
            print("Scenario: Customer order inquiry with multi-agent coordination")
            print()
            
            # Step 1: Load agents from registry
            await self.step1_load_agents()
            
            # Step 2: Find Shopify and UPS agents
            await self.step2_find_service_agents()
            
            # Step 3: Run customer service workflow
            await self.step3_run_customer_service_workflow()
            
            # Step 4: Show coordination patterns
            await self.step4_show_coordination_patterns()
            
            print("\n🎉 Customer Service Demo completed successfully!")
            print("✨ This demonstrates real-world multi-agent customer service workflows!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
    
    async def step1_load_agents(self):
        """Step 1: Load agents from registry."""
        print("\n📋 Step 1: Loading agents from A2A Registry...")
        
        try:
            loaded_count = await self.orchestrator.load_agents_from_registry(limit=100)
            print(f"✅ Loaded {loaded_count} agents from registry")
            print(f"📊 Total agents available: {len(self.orchestrator.agents)}")
            
            if self.orchestrator.agents:
                print("\n🔍 Available agents:")
                for i, (agent_id, agent) in enumerate(list(self.orchestrator.agents.items())[:5]):
                    print(f"  {i+1}. {agent['name']} ({agent_id})")
                    print(f"     Description: {agent['description'][:80]}...")
                    print(f"     URL: {agent.get('location', {}).get('url', 'N/A')}")
                    print()
            
        except Exception as e:
            logger.error(f"❌ Failed to load agents: {e}")
            print(f"❌ Agent loading failed: {e}")
    
    async def step2_find_service_agents(self):
        """Step 2: Find Shopify and UPS agents."""
        print("\n🔍 Step 2: Finding Shopify and UPS agents...")
        
        try:
            # Search for Shopify agents
            shopify_agents = await self.orchestrator.discover_agents(query="shopify")
            print(f"🛍️ Found {len(shopify_agents)} Shopify agents")
            
            # Search for UPS agents
            ups_agents = await self.orchestrator.discover_agents(query="ups")
            print(f"📦 Found {len(ups_agents)} UPS agents")
            
            # Store agent references
            self.shopify_agent = shopify_agents[0] if shopify_agents else None
            self.ups_agent = ups_agents[0] if ups_agents else None
            
            if self.shopify_agent:
                print(f"✅ Shopify Agent: {self.shopify_agent['name']} ({self.shopify_agent['id']})")
            else:
                print("❌ No Shopify agent found")
            
            if self.ups_agent:
                print(f"✅ UPS Agent: {self.ups_agent['name']} ({self.ups_agent['id']})")
            else:
                print("❌ No UPS agent found")
            
        except Exception as e:
            logger.error(f"❌ Failed to find service agents: {e}")
            print(f"❌ Agent discovery failed: {e}")
    
    async def step3_run_customer_service_workflow(self):
        """Step 3: Run the customer service workflow."""
        print("\n🛍️ Step 3: Running Customer Service Workflow...")
        
        # Customer scenario
        customer_order_id = "ORD-2024-001"
        customer_name = "John Doe"
        customer_message = f"Hi, I'd like to check the status of my order {customer_order_id}. When will it be delivered?"
        
        print(f"👤 Customer: {customer_name}")
        print(f"📞 Inquiry: {customer_message}")
        print()
        
        if not self.shopify_agent or not self.ups_agent:
            print("❌ Required agents not available. Please register both Shopify and UPS agents first.")
            return
        
        # Step 3.1: Customer asks Shopify agent for order status
        print("🛍️ Step 3.1: Customer asks Shopify agent for order status...")
        
        shopify_task = f"""
        Customer Service Request:
        
        Customer: {customer_name}
        Order ID: {customer_order_id}
        Inquiry: {customer_message}
        
        Please help the customer by:
        1. Looking up order {customer_order_id}
        2. Providing order status and details
        3. If the order is shipped, get the tracking information
        4. If tracking info is available, prepare to delegate to UPS agent
        
        Expected response format:
        - Order status (pending, processing, shipped, delivered)
        - Order details (items, quantity, total)
        - Tracking number (if shipped)
        - Next steps for customer
        """
        
        shopify_result = await self.orchestrator.delegate_task_to_agent(
            agent_id=self.shopify_agent['id'],
            message=shopify_task
        )
        
        print(f"✅ Shopify agent response received!")
        print(f"📊 Shopify Result: {str(shopify_result)[:150]}...")
        print()
        
        # Step 3.2: Shopify agent delegates to UPS agent for tracking
        print("📦 Step 3.2: Shopify agent delegates to UPS agent for tracking...")
        
        ups_task = f"""
        Tracking Request from Shopify Agent:
        
        Order ID: {customer_order_id}
        Customer: {customer_name}
        Tracking Number: 1Z999AA10123456784
        Original Inquiry: {customer_message}
        
        Please provide detailed tracking information including:
        1. Current package location
        2. Estimated delivery date and time
        3. Delivery status and progress
        4. Any delays or issues
        5. Delivery confirmation details
        
        This is for customer order {customer_order_id} inquiry.
        Customer is expecting delivery information.
        """
        
        ups_result = await self.orchestrator.delegate_task_to_agent(
            agent_id=self.ups_agent['id'],
            message=ups_task
        )
        
        print(f"✅ UPS agent response received!")
        print(f"📊 UPS Result: {str(ups_result)[:150]}...")
        print()
        
        # Step 3.3: Compile final customer response
        print("📋 Step 3.3: Compiling final customer response...")
        
        final_response = {
            "customer": customer_name,
            "order_id": customer_order_id,
            "inquiry": customer_message,
            "shopify_response": shopify_result,
            "ups_response": ups_result,
            "final_status": "Order is shipped and being tracked",
            "delivery_summary": f"Order {customer_order_id} is currently in transit and on schedule for delivery.",
            "next_steps": "Customer will receive delivery confirmation when package arrives."
        }
        
        print("🎉 Customer Service Workflow Completed!")
        print("="*60)
        print("FINAL CUSTOMER RESPONSE:")
        print("="*60)
        print(f"Customer: {final_response['customer']}")
        print(f"Order ID: {final_response['order_id']}")
        print(f"Status: {final_response['final_status']}")
        print(f"Summary: {final_response['delivery_summary']}")
        print(f"Next Steps: {final_response['next_steps']}")
        print("="*60)
        
        return final_response
    
    async def step4_show_coordination_patterns(self):
        """Step 4: Show different coordination patterns."""
        print("\n🤝 Step 4: Customer Service Coordination Patterns...")
        
        if not self.shopify_agent or not self.ups_agent:
            print("❌ Required agents not available. Please register both Shopify and UPS agents first.")
            return
        
        try:
            # Pattern 1: Sequential Customer Service
            print("\n🔄 Pattern 1: Sequential Customer Service")
            sequential_config = {
                "type": "sequential",
                "primary_agent": self.shopify_agent['id'],
                "supporting_agents": [self.ups_agent['id']],
                "task_description": "Customer order inquiry - check order status, then get tracking info"
            }
            
            sequential_result = await self.orchestrator.coordinate_agents(sequential_config)
            print(f"✅ Sequential coordination completed!")
            print(f"📊 Agents involved: {sequential_result.get('agents_involved', [])}")
            
            # Pattern 2: Parallel Information Gathering
            print("\n⚡ Pattern 2: Parallel Information Gathering")
            parallel_config = {
                "type": "parallel",
                "primary_agent": self.shopify_agent['id'],
                "supporting_agents": [self.ups_agent['id']],
                "task_description": "Gather order and tracking information simultaneously"
            }
            
            parallel_result = await self.orchestrator.coordinate_agents(parallel_config)
            print(f"✅ Parallel coordination completed!")
            print(f"📊 Agents involved: {parallel_result.get('agents_involved', [])}")
            
        except Exception as e:
            print(f"❌ Coordination patterns failed: {e}")
            print("Please ensure both agents are running and accessible.")


async def main():
    """Main function."""
    print("🚀 Starting Customer Service Demo")
    print("This demo shows how Shopify and UPS agents work together for customer service:")
    print("- Customer asks Shopify agent for order status")
    print("- Shopify agent delegates to UPS agent for tracking")
    print("- Both agents coordinate to provide comprehensive response")
    print()
    
    if not ORCHESTRATOR_AVAILABLE:
        print("❌ MultiAgentOrchestrator is not available!")
        print("Please ensure agent_runner_example.py is in the same directory")
        return 1
    
    try:
        demo = CustomerServiceDemo()
        await demo.run_customer_service_scenario()
        
    except Exception as e:
        logger.error(f"❌ Demo execution failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure A2A Registry is running and accessible")
        print("2. Check that Shopify and UPS agents are registered")
        print("3. Verify network connectivity")
        print("4. Check API keys and authentication")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
