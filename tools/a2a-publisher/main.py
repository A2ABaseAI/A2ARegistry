#!/usr/bin/env python3
"""
A2A Agent Publisher CLI Tool

A command-line interface for publishing and managing agents in the A2A Agent Registry.
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

console = Console()

class A2APublisher:
    """A2A Agent Publisher client."""
    
    def __init__(self, registry_url: str = None, client_id: str = None, client_secret: str = None):
        self.registry_url = registry_url or os.getenv('A2A_REGISTRY_URL', 'http://localhost:8000')
        self.client_id = client_id or os.getenv('A2A_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('A2A_CLIENT_SECRET')
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with the A2A registry."""
        if not self.client_id or not self.client_secret:
            console.print("[red]Error: Client ID and secret required for authentication[/red]")
            console.print("Set A2A_CLIENT_ID and A2A_CLIENT_SECRET environment variables or use --client-id and --client-secret flags")
            return False
            
        try:
            response = requests.post(
                f"{self.registry_url}/oauth/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            if self.access_token:
                console.print("[green]✓ Authentication successful[/green]")
                return True
            else:
                console.print("[red]✗ Authentication failed: No access token received[/red]")
                return False
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Authentication failed: {e}[/red]")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for authenticated requests."""
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def validate_agent_card(self, agent_card: Dict[str, Any]) -> List[str]:
        """Validate an agent card structure."""
        errors = []
        
        # Required fields
        required_fields = ['name', 'description', 'version', 'author']
        for field in required_fields:
            if not agent_card.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate capabilities if present
        if 'capabilities' in agent_card:
            capabilities = agent_card['capabilities']
            if not isinstance(capabilities.get('protocols', []), list):
                errors.append("capabilities.protocols must be a list")
            if not isinstance(capabilities.get('supported_formats', []), list):
                errors.append("capabilities.supported_formats must be a list")
        
        # Validate auth schemes if present
        if 'auth_schemes' in agent_card:
            auth_schemes = agent_card['auth_schemes']
            if not isinstance(auth_schemes, list):
                errors.append("auth_schemes must be a list")
            else:
                for i, scheme in enumerate(auth_schemes):
                    if not scheme.get('type'):
                        errors.append(f"auth_schemes[{i}] missing required field: type")
        
        return errors
    
    def publish_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Publish an agent to the registry."""
        try:
            response = requests.post(
                f"{self.registry_url}/agents",
                json=agent_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            agent_response = response.json()
            console.print(f"[green]✓ Agent '{agent_response['name']}' published successfully[/green]")
            console.print(f"  Agent ID: {agent_response['id']}")
            console.print(f"  Version: {agent_response['version']}")
            return True
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Failed to publish agent: {e}[/red]")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    console.print(f"  Error details: {error_data.get('detail', 'Unknown error')}")
                except:
                    pass
            return False
    
    def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """Update an existing agent."""
        try:
            response = requests.put(
                f"{self.registry_url}/agents/{agent_id}",
                json=agent_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            agent_response = response.json()
            console.print(f"[green]✓ Agent '{agent_response['name']}' updated successfully[/green]")
            return True
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Failed to update agent: {e}[/red]")
            return False
    
    def list_agents(self, page: int = 1, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """List published agents."""
        try:
            response = requests.get(
                f"{self.registry_url}/agents/public",
                params={'page': page, 'limit': limit}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('agents', [])
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Failed to list agents: {e}[/red]")
            return None
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        try:
            response = requests.delete(
                f"{self.registry_url}/agents/{agent_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            console.print(f"[green]✓ Agent {agent_id} deleted successfully[/green]")
            return True
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Failed to delete agent: {e}[/red]")
            return False

def load_agent_config(config_path: Path) -> Dict[str, Any]:
    """Load agent configuration from file."""
    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)

def create_sample_config(output_path: Path):
    """Create a sample agent configuration file."""
    sample_config = {
        "name": "my-awesome-agent",
        "description": "A sample AI agent that demonstrates A2A capabilities",
        "version": "1.0.0",
        "author": "Your Name",
        "provider": "your-org",
        "tags": ["ai", "assistant", "sample"],
        "is_public": True,
        "is_active": True,
        "location_url": "https://your-domain.com/api/agent",
        "location_type": "api_endpoint",
        "agent_card": {
            "name": "my-awesome-agent",
            "description": "A sample AI agent that demonstrates A2A capabilities",
            "version": "1.0.0",
            "author": "Your Name",
            "api_base_url": "https://your-domain.com/api",
            "capabilities": {
                "protocols": ["http", "websocket"],
                "supported_formats": ["json", "xml"],
                "max_request_size": 1048576,
                "max_concurrent_requests": 10
            },
            "auth_schemes": [
                {
                    "type": "api_key",
                    "description": "API key authentication",
                    "required": True,
                    "header_name": "X-API-Key"
                }
            ],
            "endpoints": {
                "chat": "/chat",
                "status": "/status",
                "capabilities": "/capabilities"
            }
        },
        "capabilities": {
            "protocols": ["http", "websocket"],
            "supported_formats": ["json", "xml"],
            "max_request_size": 1048576,
            "max_concurrent_requests": 10
        },
        "auth_schemes": [
            {
                "type": "api_key",
                "description": "API key authentication",
                "required": True
            }
        ]
    }
    
    try:
        with open(output_path, 'w') as f:
            if output_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(sample_config, f, default_flow_style=False, indent=2)
            else:
                json.dump(sample_config, f, indent=2)
        
        console.print(f"[green]✓ Sample configuration created: {output_path}[/green]")
        console.print("Edit this file with your agent details and use 'a2a-publisher publish' to publish it.")
        
    except Exception as e:
        console.print(f"[red]Error creating sample configuration: {e}[/red]")

def cmd_init(args):
    """Initialize a new agent configuration."""
    output_path = Path(args.output or "agent.yaml")
    
    if output_path.exists() and not Confirm.ask(f"File {output_path} already exists. Overwrite?"):
        return
    
    create_sample_config(output_path)

def cmd_publish(args):
    """Publish an agent to the registry."""
    config_path = Path(args.config)
    agent_data = load_agent_config(config_path)
    
    publisher = A2APublisher(args.registry_url, args.client_id, args.client_secret)
    
    # Authenticate
    if not publisher.authenticate():
        sys.exit(1)
    
    # Validate agent card
    if 'agent_card' in agent_data:
        errors = publisher.validate_agent_card(agent_data['agent_card'])
        if errors:
            console.print("[red]Agent card validation errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            if not Confirm.ask("Continue with publication despite validation errors?"):
                sys.exit(1)
    
    # Publish
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Publishing agent...", total=None)
        success = publisher.publish_agent(agent_data)
        progress.stop()
    
    sys.exit(0 if success else 1)

def cmd_update(args):
    """Update an existing agent."""
    config_path = Path(args.config)
    agent_data = load_agent_config(config_path)
    
    publisher = A2APublisher(args.registry_url, args.client_id, args.client_secret)
    
    if not publisher.authenticate():
        sys.exit(1)
    
    success = publisher.update_agent(args.agent_id, agent_data)
    sys.exit(0 if success else 1)

def cmd_list(args):
    """List published agents."""
    publisher = A2APublisher(args.registry_url)
    agents = publisher.list_agents(args.page, args.limit)
    
    if agents is None:
        sys.exit(1)
    
    if not agents:
        console.print("No agents found.")
        return
    
    table = Table(title="Published Agents")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Provider", style="blue")
    table.add_column("Public", style="magenta")
    table.add_column("Active", style="red")
    
    for agent in agents:
        table.add_row(
            agent.get('id', 'N/A')[:8] + '...' if len(agent.get('id', '')) > 8 else agent.get('id', 'N/A'),
            agent.get('name', 'N/A'),
            agent.get('version', 'N/A'),
            agent.get('provider', 'N/A'),
            "✓" if agent.get('is_public') else "✗",
            "✓" if agent.get('is_active') else "✗"
        )
    
    console.print(table)

def cmd_delete(args):
    """Delete an agent."""
    if not Confirm.ask(f"Are you sure you want to delete agent {args.agent_id}?"):
        return
    
    publisher = A2APublisher(args.registry_url, args.client_id, args.client_secret)
    
    if not publisher.authenticate():
        sys.exit(1)
    
    success = publisher.delete_agent(args.agent_id)
    sys.exit(0 if success else 1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="A2A Agent Publisher - Publish and manage agents in the A2A Agent Registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize a new agent configuration
  a2a-publisher init

  # Publish an agent
  a2a-publisher publish agent.yaml

  # List published agents
  a2a-publisher list

  # Update an agent
  a2a-publisher update my-agent-id agent.yaml

  # Delete an agent
  a2a-publisher delete my-agent-id

Environment Variables:
  A2A_REGISTRY_URL    Registry URL (default: http://localhost:8000)
  A2A_CLIENT_ID       OAuth client ID for authentication
  A2A_CLIENT_SECRET   OAuth client secret for authentication
        """
    )
    
    parser.add_argument('--registry-url', help='A2A registry URL')
    parser.add_argument('--client-id', help='OAuth client ID')
    parser.add_argument('--client-secret', help='OAuth client secret')
    parser.add_argument('--version', action='version', version='a2a-publisher 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new agent configuration')
    init_parser.add_argument('-o', '--output', help='Output file path (default: agent.yaml)')
    init_parser.set_defaults(func=cmd_init)
    
    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish an agent')
    publish_parser.add_argument('config', help='Agent configuration file (JSON or YAML)')
    publish_parser.set_defaults(func=cmd_publish)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update an existing agent')
    update_parser.add_argument('agent_id', help='Agent ID to update')
    update_parser.add_argument('config', help='Agent configuration file (JSON or YAML)')
    update_parser.set_defaults(func=cmd_update)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List published agents')
    list_parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    list_parser.add_argument('--limit', type=int, default=20, help='Results per page (default: 20)')
    list_parser.set_defaults(func=cmd_list)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an agent')
    delete_parser.add_argument('agent_id', help='Agent ID to delete')
    delete_parser.set_defaults(func=cmd_delete)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
