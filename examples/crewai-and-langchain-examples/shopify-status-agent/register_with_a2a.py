#!/usr/bin/env python3
"""
Shopify Status Agent - A2A Registry Registration Script

This script demonstrates how to register the Shopify Status Agent with the A2A Registry
using the official Python SDK builder pattern.

Usage:
    python register_with_a2a.py

Environment Variables:
    A2A_REGISTRY_URL: URL of the A2A Registry (default: http://localhost:8000)
    A2A_REGISTRY_API_KEY: API key for authentication (default: dev-admin-api-key)
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import A2A Registry SDK
try:
    from a2a_reg_sdk import (
        A2ARegClient,
        AgentBuilder,
        AgentCapabilitiesBuilder,
        SecuritySchemeBuilder,
        AgentSkillBuilder,
        AgentCardSpecBuilder,
        AgentInterfaceBuilder,
    )
    SDK_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import A2A Registry SDK: {e}")
    logger.error("Please install the SDK: pip install -e ../sdk/python")
    SDK_AVAILABLE = False


def create_shopify_agent_card():
    """Create Shopify Status Agent card using SDK builder pattern."""
    
    if not SDK_AVAILABLE:
        raise ImportError("A2A Registry SDK not available. Please install: pip install -e ../../sdk/python")
    
    # Build capabilities using SDK builder
    capabilities = (
        AgentCapabilitiesBuilder()
        .streaming(False)
        .push_notifications(False)
        .state_transition_history(True)
        .build()
    )
    
    # Build security scheme using SDK builder
    security_scheme = (
        SecuritySchemeBuilder("apiKey")
        .location("header")
        .name("X-API-Key")
        .build()
    )
    
    # Build agent skill using SDK builder
    skill = (
        AgentSkillBuilder(
            skill_id="shopify_order_tracking",
            name="Shopify Order Tracking",
            description="Track and provide status updates for Shopify orders",
            tags=["ecommerce", "shopify", "orders", "tracking"]
        )
        .examples([
            "Check order status: 'What's the status of order #1001?'",
            "Track order: 'Track order 1001'",
            "Order details: 'Show me details for order #1001'",
            "Customer orders: 'Show all orders for customer john@example.com'",
            "Natural language: 'Where is my Shopify order going to New York?'"
        ])
        .input_modes(["text/plain"])
        .output_modes(["text/plain"])
        .build()
    )
    
    # Build interface using SDK builder
    interface = (
        AgentInterfaceBuilder(
            preferred_transport="jsonrpc",
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"]
        )
        .additional_interface("http", "http://localhost:8005/api/agent")
        .build()
    )
    
    # Build agent card spec using SDK builder
    agent_card_spec = (
        AgentCardSpecBuilder(
            name="Shopify Status Agent",
            description="AI agent for tracking Shopify orders and providing status updates using LangChain",
            url="http://localhost:8005/api/agent",
            version="1.0.0"
        )
        .with_provider("A2A Registry Team", "http://localhost:8005")
        .with_capabilities(capabilities)
        .add_security_scheme(security_scheme)
        .add_skill(skill)
        .with_interface(interface)
        .build()
    )
    
    # Build agent using SDK builder
    agent = (
        AgentBuilder(
            "Shopify Status Agent",
            "AI agent for tracking Shopify orders and providing status updates using LangChain",
            "1.0.0",
            "A2A Registry Team"
        )
        .with_tags(["ecommerce", "shopify", "orders", "tracking", "langchain"])
        .with_location("http://localhost:8005/api/agent", "api_endpoint")
        .with_capabilities(capabilities)
        .with_auth_schemes([security_scheme])
        .with_skills([skill])
        .with_agent_card(agent_card_spec)
        .public(True)
        .active(True)
        .build()
    )
    
    return agent


async def register_shopify_agent():
    """Register Shopify Status Agent with A2A Registry."""
    
    if not SDK_AVAILABLE:
        raise ImportError("A2A Registry SDK not available. Please install: pip install -e ../../sdk/python")
    
    # Configuration
    registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    api_key = os.getenv("A2A_REGISTRY_API_KEY", "dev-admin-api-key")
    
    logger.info(f"Registering Shopify Status Agent with A2A Registry at {registry_url}")
    
    try:
        # Create SDK client with API key authentication
        client = A2ARegClient(registry_url=registry_url, api_key=api_key)
        
        # Create agent using builder pattern
        agent = create_shopify_agent_card()
        
        logger.info("Publishing agent to A2A Registry using SDK...")
        # Publish agent (validate=False to skip validation, set to True for validation)
        result = client.publish_agent(agent, validate=False)
        
        logger.info("✅ Shopify Status Agent registered successfully!")
        logger.info(f"Agent ID: {result.id}")
        agent_url = f'{registry_url}/agents/{result.id}/card'
        logger.info(f"Agent URL: {agent_url}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to register Shopify Status Agent: {e}")
        raise


def print_agent_card_info():
    """Print agent card information for verification."""
    if not SDK_AVAILABLE:
        print("⚠️  SDK not available - cannot print agent card info")
        return
    
    agent = create_shopify_agent_card()
    
    print("\n" + "="*60)
    print("SHOPIFY STATUS AGENT CARD")
    print("="*60)
    print(f"Name: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Version: {agent.version}")
    print(f"Provider: {agent.provider}")
    print(f"Location URL: {agent.location_url}")
    print(f"Public: {agent.is_public}")
    print(f"Active: {agent.is_active}")
    
    if agent.capabilities:
        print(f"\nCapabilities:")
        print(f"  Streaming: {agent.capabilities.streaming}")
        print(f"  Push Notifications: {agent.capabilities.pushNotifications}")
        print(f"  State Transition History: {agent.capabilities.stateTransitionHistory}")
        print(f"  Supports Authenticated Extended Card: {agent.capabilities.supportsAuthenticatedExtendedCard}")
    
    if agent.skills:
        print(f"\nSkills:")
        for skill in agent.skills:
            print(f"  ID: {skill.id}")
            print(f"  Name: {skill.name}")
            print(f"  Description: {skill.description}")
            print(f"  Tags: {skill.tags}")
            if skill.examples:
                print(f"  Examples:")
                for example in skill.examples:
                    print(f"    - {example}")
    
    if agent.auth_schemes:
        print(f"\nAuthentication:")
        for auth in agent.auth_schemes:
            print(f"  Type: {auth.type}")
            print(f"  Location: {auth.location}")
            print(f"  Name: {auth.name}")
    
    print(f"\nTags: {agent.tags}")
    
    if agent.agent_card:
        print(f"\nAgent Card Spec:")
        print(f"  Name: {agent.agent_card.name}")
        print(f"  URL: {agent.agent_card.url}")
        if agent.agent_card.provider:
            print(f"  Provider: {agent.agent_card.provider.organization}")
        if agent.agent_card.interface:
            print(f"  Preferred Transport: {agent.agent_card.interface.preferredTransport}")
    
    print("="*60)


async def main():
    """Main function."""
    print("🚀 Shopify Status Agent - A2A Registry Registration")
    print("="*60)
    
    if not SDK_AVAILABLE:
        print("⚠️  A2A Registry SDK not available")
        print("   Install the SDK with: pip install -e ../../sdk/python")
        print()
        return 1
    
    # Print agent card information
    try:
        print_agent_card_info()
    except Exception as e:
        logger.error(f"Failed to create agent card: {e}")
        return 1
    
    # Register agent
    try:
        result = await register_shopify_agent()
        
        print("\n🎉 Registration completed successfully!")
        print(f"Agent ID: {result.id}")
        registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
        print(f"Agent Card URL: {registry_url}/agents/{result.id}/card")
        
        print("\n📋 Next Steps:")
        print("1. Start the Shopify Status Agent service")
        print("2. Test the agent using the A2A Registry API")
        print("3. Verify agent discovery and communication")
        
    except Exception as e:
        logger.exception("Registration failed")
        print(f"\n❌ Registration failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
