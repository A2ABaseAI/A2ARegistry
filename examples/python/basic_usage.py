#!/usr/bin/env python3
"""
Basic A2A SDK Usage Example

This example demonstrates basic usage of the A2A Python SDK for:
- Connecting to the registry
- Publishing an agent
- Searching for agents
- Updating and deleting agents
"""

import os
from a2a_sdk import A2AClient, AgentBuilder, AgentCapabilities, AuthScheme

def main():
    # Initialize the client
    client = A2AClient(
        registry_url="http://localhost:8000",
        client_id=os.getenv("A2A_CLIENT_ID"),
        client_secret=os.getenv("A2A_CLIENT_SECRET")
    )
    
    # Authenticate (required for publishing)
    try:
        client.authenticate()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    # Create a simple agent
    capabilities = AgentCapabilities(
        protocols=["http"],
        supported_formats=["json"],
        max_concurrent_requests=5
    )
    
    auth_scheme = AuthScheme(
        type="api_key",
        description="Simple API key authentication",
        required=True,
        header_name="X-API-Key"
    )
    
    agent = AgentBuilder("my-test-agent", "A test agent for demonstration", "1.0.0", "my-org") \
        .with_tags(["test", "demo", "ai"]) \
        .with_location("https://my-org.com/api/agent") \
        .with_capabilities(capabilities) \
        .with_auth_schemes([auth_scheme]) \
        .public(True) \
        .active(True) \
        .build()
    
    try:
        # Publish the agent
        published_agent = client.publish_agent(agent)
        print(f"✓ Agent published successfully with ID: {published_agent.id}")
        
        # List public agents
        agents_response = client.list_agents(page=1, limit=10)
        print(f"✓ Found {len(agents_response.get('agents', []))} public agents")
        
        # Search for agents
        search_results = client.search_agents(
            query="test",
            filters={"tags": ["demo"]},
            page=1,
            limit=5
        )
        print(f"✓ Search found {len(search_results.get('agents', []))} matching agents")
        
        # Get agent details
        agent_details = client.get_agent(published_agent.id)
        print(f"✓ Retrieved agent details: {agent_details.name}")
        
        # Update the agent
        agent_details.description = "Updated description for my test agent"
        updated_agent = client.update_agent(published_agent.id, agent_details)
        print(f"✓ Agent updated successfully")
        
        # Clean up - delete the agent
        client.delete_agent(published_agent.id)
        print(f"✓ Agent deleted successfully")
        
    except Exception as e:
        print(f"✗ Operation failed: {e}")
    
    finally:
        # Close the client
        client.close()

if __name__ == "__main__":
    main()
