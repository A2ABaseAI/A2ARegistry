#!/usr/bin/env python3
"""
A2A Agent Publisher Example

This example demonstrates using the high-level AgentPublisher class for:
- Creating sample agent configurations
- Loading agents from configuration files
- Publishing and managing agents with validation
"""

import os
from pathlib import Path
from a2a_sdk import A2AClient, AgentPublisher


def main():
    # Create client and publisher
    client = A2AClient(
        registry_url="http://localhost:8000",
        client_id=os.getenv("A2A_CLIENT_ID"),
        client_secret=os.getenv("A2A_CLIENT_SECRET"),
    )

    try:
        client.authenticate()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return

    publisher = AgentPublisher(client)

    # Create a sample agent configuration
    sample_agent = publisher.create_sample_agent(
        name="sample-chatbot",
        description="A sample AI chatbot agent",
        version="1.2.0",
        provider="demo-corp",
        api_url="https://demo-corp.com/api",
    )

    print(f"✓ Created sample agent: {sample_agent.name}")

    # Save the configuration to a file
    config_path = Path("sample_agent.yaml")
    publisher.save_agent_config(sample_agent, config_path, format="yaml")
    print(f"✓ Saved agent configuration to {config_path}")

    try:
        # Validate the agent
        validation_errors = publisher.validate_agent(sample_agent)
        if validation_errors:
            print(f"✗ Validation errors: {validation_errors}")
            return
        else:
            print("✓ Agent configuration is valid")

        # Publish the agent
        published_agent = publisher.publish(sample_agent, validate=True)
        print(f"✓ Agent published with ID: {published_agent.id}")

        # Load and publish from file
        loaded_agent = publisher.load_agent_from_file(config_path)
        loaded_agent.name = "sample-chatbot-from-file"  # Change name to avoid conflict

        published_from_file = publisher.publish(loaded_agent, validate=True)
        print(f"✓ Agent from file published with ID: {published_from_file.id}")

        # Update the agent
        published_agent.description = "Updated sample AI chatbot with new features"
        updated_agent = publisher.update(
            published_agent.id, published_agent, validate=True
        )
        print(f"✓ Agent updated successfully")

        # Clean up
        client.delete_agent(published_agent.id)
        client.delete_agent(published_from_file.id)
        print("✓ Cleanup completed")

    except Exception as e:
        print(f"✗ Operation failed: {e}")

    finally:
        # Clean up the config file
        if config_path.exists():
            config_path.unlink()
        client.close()


if __name__ == "__main__":
    main()
