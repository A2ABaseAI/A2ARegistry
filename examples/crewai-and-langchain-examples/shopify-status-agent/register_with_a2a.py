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

try:
    # Import A2A Registry SDK
    from a2a_reg_sdk import A2AClient, AgentBuilder, AgentCapabilitiesBuilder, AuthSchemeBuilder, AgentSkillsBuilder
    SDK_AVAILABLE = True
except ImportError:
    logger.warning("A2A Registry SDK not available. Using mock implementation.")
    SDK_AVAILABLE = False
    
    # Mock classes for demonstration
    class A2AClient:
        def __init__(self, registry_url: str, api_key: str):
            self.registry_url = registry_url
            self.api_key = api_key
        
        def publish_agent(self, agent_card):
            logger.info(f"Mock: Would publish agent to {self.registry_url}")
            return {"id": "mock-shopify-agent-id", "url": f"{self.registry_url}/agents/mock-shopify-agent-id"}
    
    class AgentBuilder:
        def __init__(self, name: str, description: str, version: str, organization: str):
            self._name = name
            self._description = description
            self._version = version
            self._organization = organization
            self._tags = []
            self._location = None
            self._capabilities = None
            self._auth_schemes = []
            self._skills = None
            self._public = True
            self._active = True
        
        def with_tags(self, tags):
            self._tags = tags
            return self
        
        def with_location(self, url, endpoint_type):
            self._location_url = url
            self._location = {"url": url, "type": endpoint_type}
            return self
        
        def with_capabilities(self, capabilities):
            self._capabilities = capabilities
            return self
        
        def with_auth_schemes(self, schemes):
            self._auth_schemes = schemes
            return self
        
        def with_skills(self, skills):
            self._skills = skills
            return self
        
        def public(self, is_public):
            self._public = is_public
            return self
        
        def active(self, is_active):
            self._active = is_active
            return self
        
        def build(self):
            return {
                "name": self._name,
                "description": self._description,
                "version": self._version,
                "provider": {"organization": self._organization},
                "tags": self._tags,
                "location": self._location,
                "location_url": self._location_url,
                "capabilities": self._capabilities,
                "auth_schemes": self._auth_schemes,
                "skills": self._skills,
                "public": self._public,
                "active": self._active
            }
    
    class AgentCapabilitiesBuilder:
        def __init__(self):
            self._protocols = []
            self._supported_formats = []
            self._max_request_size = None
            self._max_concurrent_requests = None
            self._a2a_version = None
            self._streaming = False
            self._push_notifications = False
            self._state_transition_history = False
        
        def protocols(self, protocols):
            self._protocols = protocols
            return self
        
        def supported_formats(self, formats):
            self._supported_formats = formats
            return self
        
        def max_request_size(self, size):
            self._max_request_size = size
            return self
        
        def max_concurrent_requests(self, count):
            self._max_concurrent_requests = count
            return self
        
        def a2a_version(self, version):
            self._a2a_version = version
            return self
        
        def streaming(self, enabled):
            self._streaming = enabled
            return self
        
        def push_notifications(self, enabled):
            self._push_notifications = enabled
            return self
        
        def state_transition_history(self, enabled):
            self._state_transition_history = enabled
            return self
        
        def build(self):
            return {
                "protocols": self._protocols,
                "supported_formats": self._supported_formats,
                "max_request_size": self._max_request_size,
                "max_concurrent_requests": self._max_concurrent_requests,
                "a2a_version": self._a2a_version,
                "streaming": self._streaming,
                "push_notifications": self._push_notifications,
                "state_transition_history": self._state_transition_history
            }
    
    class AuthSchemeBuilder:
        def __init__(self, scheme_type: str):
            self._type = scheme_type
            self._description = ""
            self._required = False
            self._header_name = None
        
        def description(self, desc):
            self._description = desc
            return self
        
        def required(self, is_required):
            self._required = is_required
            return self
        
        def header_name(self, name):
            self._header_name = name
            return self
        
        def build(self):
            return {
                "type": self._type,
                "description": self._description,
                "required": self._required,
                "header_name": self._header_name
            }
    
    class AgentSkillsBuilder:
        def __init__(self):
            self._examples = []
            self._tags = []
        
        def examples(self, examples):
            self._examples = examples
            return self
        
        def tags(self, tags):
            self._tags = tags
            return self
        
        def build(self):
            return {
                "examples": self._examples,
                "tags": self._tags
            }


def create_shopify_agent_card():
    """Create Shopify Status Agent card using SDK builder pattern."""
    
    # Build agent using SDK builder pattern
    agent_card = (
        AgentBuilder(
            "Shopify Status Agent v2",
            "AI agent for tracking Shopify orders and providing status updates using LangChain",
            "1.0.0",
            "A2A Registry Team"
        )
        .with_tags(["ecommerce", "shopify", "orders", "tracking", "langchain"])
        .with_location("http://localhost:8005", "api_endpoint")
        .with_capabilities(
            AgentCapabilitiesBuilder()
            .protocols(["http", "websocket"])
            .supported_formats(["json", "text"])
            .max_request_size(1048576)  # 1MB
            .max_concurrent_requests(10)
            .a2a_version("1.0")
            .build()
        )
        .with_auth_schemes([
            AuthSchemeBuilder("api_key")
            .description("API key authentication")
            .required(True)
            .header_name("X-API-Key")
            .build()
        ])
        .with_skills(
            AgentSkillsBuilder()
            .examples([
                "Check order status: 'What's the status of order #1001?'",
                "Track order: 'Track order 1001'",
                "Order details: 'Show me details for order #1001'",
                "Customer orders: 'Show all orders for customer john@example.com'",
                "Natural language: 'Where is my Shopify order going to New York?'"
            ])
            .build()
        )
        .public(True)
        .active(True)
        .build()
    )
    
    return agent_card


async def register_shopify_agent():
    """Register Shopify Status Agent with A2A Registry."""
    
    # Configuration
    registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
    api_key = os.getenv("A2A_REGISTRY_API_KEY", "dev-admin-api-key")
    
    logger.info(f"Registering Shopify Status Agent with A2A Registry at {registry_url}")
    
    try:
        if SDK_AVAILABLE:
            # Use SDK client
            client = A2AClient(registry_url=registry_url, api_key=api_key)
            agent_card = create_shopify_agent_card()
            logger.info("Publishing agent to A2A Registry using SDK...")
            result = client.publish_agent(agent_card)
        else:
            # Use mock client
            client = A2AClient(registry_url=registry_url, api_key=api_key)
            agent_card = create_shopify_agent_card()
            logger.info("Publishing agent to A2A Registry using mock...")
            result = client.publish_agent(agent_card)
        
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
    agent = create_shopify_agent_card()
    
    print("\n" + "="*60)
    print("SHOPIFY STATUS AGENT CARD")
    print("="*60)
    print(f"Name: {agent.name}")
    print(f"Description: {agent.description}")
    print(f"Version: {agent.version}")
    print(f"Provider: {agent.provider}")
    print(f"URL: {agent.location_url}")
    print(f"Public: {agent.is_public}")
    print(f"Active: {agent.is_active}")
    
    if agent.capabilities:
        print(f"\nCapabilities:")
        print(f"  Protocols: {agent.capabilities.protocols}")
        print(f"  Formats: {agent.capabilities.supported_formats}")
        print(f"  Max Request Size: {agent.capabilities.max_request_size}")
        print(f"  Max Concurrent Requests: {agent.capabilities.max_concurrent_requests}")
        print(f"  A2A Version: {agent.capabilities.a2a_version}")
    
    if agent.skills:
        print(f"\nSkills:")
        print(f"  Examples:")
        for example in agent.skills.examples:
            print(f"    - {example}")
    
    if agent.auth_schemes:
        print(f"\nAuthentication:")
        for auth in agent.auth_schemes:
            print(f"  Type: {auth.type}")
            print(f"  Description: {auth.description}")
            print(f"  Required: {auth.required}")
            if auth.header_name:
                print(f"  Header: {auth.header_name}")
    
    print(f"\nTags: {agent.tags}")
    print("="*60)


async def main():
    """Main function."""
    print("🚀 Shopify Status Agent - A2A Registry Registration")
    print("="*60)
    
    if not SDK_AVAILABLE:
        print("⚠️  A2A Registry SDK not available - using mock implementation")
        print("   Install the SDK with: pip install a2a-registry")
        print()
    
    # Print agent card information
    print_agent_card_info()
    
    # Register agent
    try:
        result = await register_shopify_agent()
        
        print("\n🎉 Registration completed successfully!")
        print(f"Agent ID: {result.id}")
        registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
        print(f"Agent URL: {result.location_url or f'{registry_url}/agents/{result.id}/card'}")
        
        print("\n📋 Next Steps:")
        print("1. Start the Shopify Status Agent service")
        print("2. Test the agent using the A2A Registry API")
        print("3. Verify agent discovery and communication")
        
    except Exception as e:
        print(f"\n❌ Registration failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
