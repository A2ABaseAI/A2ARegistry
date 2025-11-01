#!/usr/bin/env python3
"""
Delete All Agents Script

This script deletes all agents from the A2A Registry using the Python SDK.
"""

import os
import sys
import logging
import requests
from pathlib import Path
from urllib.parse import urljoin

# Add SDK to path if needed
sdk_path = Path(__file__).parent.parent / "sdk" / "python"
if sdk_path.exists():
    sys.path.insert(0, str(sdk_path.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from a2a_reg_sdk import A2ARegClient, NotFoundError
    SDK_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import A2A Registry SDK: {e}")
    logger.error("Please install the SDK: pip install -e sdk/python")
    SDK_AVAILABLE = False
    sys.exit(1)


def delete_all_agents():
    """Delete all agents from the registry."""
    
    if not SDK_AVAILABLE:
        raise ImportError("A2A Registry SDK not available")
    
    # Configuration
    registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000").rstrip("/")
    api_key = os.getenv("A2A_REGISTRY_API_KEY", "dev-admin-api-key")
    
    logger.info(f"Connecting to A2A Registry at {registry_url}")
    
    # Create SDK client
    client = A2ARegClient(registry_url=registry_url, api_key=api_key)
    
    deleted_count = 0
    error_count = 0
    seen_ids = set()
    
    # Create a session for direct API calls (backend uses top/skip, not page/limit)
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })
    
    # Get all entitled agents
    logger.info("Fetching entitled agents...")
    try:
        skip = 0
        top = 100
        while True:
            response = session.get(
                urljoin(registry_url, "/agents/entitled"),
                params={"top": top, "skip": skip},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            agents = data.get("items", [])
            
            if not agents:
                break
            
            logger.info(f"Found {len(agents)} entitled agents (skip={skip})")
            
            for agent_data in agents:
                agent_id = agent_data.get("id") or agent_data.get("agentId")
                if not agent_id or agent_id in seen_ids:
                    continue
                
                seen_ids.add(agent_id)
                
                try:
                    logger.info(f"Deleting agent: {agent_id}")
                    client.delete_agent(agent_id)
                    deleted_count += 1
                    logger.info(f"✅ Deleted agent: {agent_id}")
                except NotFoundError:
                    logger.warning(f"Agent {agent_id} not found (may have been already deleted)")
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Failed to delete agent {agent_id}: {e}")
            
            if len(agents) < top:
                break
            skip += top
            
    except Exception as e:
        logger.error(f"Error fetching entitled agents: {e}")
    
    # Also get all public agents
    logger.info("Fetching public agents...")
    try:
        skip = 0
        top = 100
        while True:
            response = session.get(
                urljoin(registry_url, "/agents/public"),
                params={"top": top, "skip": skip},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            agents = data.get("items", [])
            
            if not agents:
                break
            
            logger.info(f"Found {len(agents)} public agents (skip={skip})")
            
            for agent_data in agents:
                agent_id = agent_data.get("id") or agent_data.get("agentId")
                if not agent_id or agent_id in seen_ids:
                    continue
                
                seen_ids.add(agent_id)
                
                try:
                    logger.info(f"Deleting agent: {agent_id}")
                    client.delete_agent(agent_id)
                    deleted_count += 1
                    logger.info(f"✅ Deleted agent: {agent_id}")
                except NotFoundError:
                    logger.warning(f"Agent {agent_id} not found (may have been already deleted)")
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Failed to delete agent {agent_id}: {e}")
            
            if len(agents) < top:
                break
            skip += top
            
    except Exception as e:
        logger.error(f"Error fetching public agents: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Deletion Summary:")
    logger.info(f"  Deleted: {deleted_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info(f"{'='*60}")
    
    return deleted_count, error_count


def main():
    """Main function."""
    print("🗑️  Delete All Agents from A2A Registry")
    print("="*60)
    
    if not SDK_AVAILABLE:
        print("⚠️  A2A Registry SDK not available")
        print("   Install the SDK with: pip install -e sdk/python")
        return 1
    
    try:
        deleted, errors = delete_all_agents()
        
        if errors == 0:
            print(f"\n✅ Successfully deleted {deleted} agent(s)")
        else:
            print(f"\n⚠️  Deleted {deleted} agent(s) with {errors} error(s)")
        
        return 0 if errors == 0 else 1
        
    except Exception as e:
        logger.exception("Failed to delete agents")
        print(f"\n❌ Failed to delete agents: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
