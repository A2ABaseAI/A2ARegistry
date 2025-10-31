"""CLI interface for UPS Tracking Agent."""

import asyncio
import json
import logging
import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

from .agent import UPSStatusAgent
from .client import UPSClient, UPSCredentialsError, UPSTrackingError
from .config import settings
from .normalizer import UPSNormalizer

# Initialize Typer app
app = typer.Typer(
    name="ups-agent",
    help="CrewAI agent for UPS shipment tracking and status checking",
    add_completion=False,
)

# Initialize Rich console
console = Console()


def setup_logging(debug: bool = False) -> None:
    """Setup Rich logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("crewai").setLevel(logging.WARNING)


def validate_credentials() -> None:
    """Validate required credentials."""
    try:
        settings.validate_ups_credentials()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set UPS_CLIENT_ID and UPS_CLIENT_SECRET in your .env file[/yellow]")
        sys.exit(1)
    
    try:
        settings.validate_openai_credentials()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set OPENAI_API_KEY in your .env file[/yellow]")
        sys.exit(1)


@app.command()
def main(
    query: str = typer.Argument(..., help="Tracking number(s) or natural language query"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    sandbox: bool = typer.Option(False, "--sandbox", "-s", help="Use UPS sandbox environment"),
) -> None:
    """Track UPS shipments using CrewAI agent."""
    
    # Setup logging
    setup_logging(debug)
    
    # Override sandbox setting if requested
    if sandbox:
        settings.ups_use_sandbox = True
        settings.ups_api_base = "https://wwwcie.ups.com"
    
    # Validate credentials
    validate_credentials()
    
    # Run async main function
    asyncio.run(async_main(query, json_output))


async def async_main(query: str, json_output: bool) -> None:
    """Async main function."""
    try:
        # Initialize components
        client = UPSClient(
            client_id=settings.ups_client_id,
            client_secret=settings.ups_client_secret,
            account_number=settings.ups_account_number,
            api_base=settings.ups_api_base,
        )
        
        normalizer = UPSNormalizer()
        
        agent = UPSStatusAgent(
            client=client,
            normalizer=normalizer,
            model=settings.crewai_model,
            temperature=settings.crewai_temperature,
        )
        
        # Process query
        async with client:
            result = await agent.process_query(query, json_output)
        
        # Output result
        if json_output:
            console.print(result)
        else:
            # Format output nicely
            if "Error" in result or "Failed" in result:
                console.print(f"[red]{result}[/red]")
            else:
                panel = Panel(
                    Text(result, style="green"),
                    title="[bold blue]UPS Tracking Result[/bold blue]",
                    border_style="blue",
                )
                console.print(panel)
    
    except UPSCredentialsError as e:
        console.print(f"[red]UPS Authentication Error: {e}[/red]")
        console.print("[yellow]Please check your UPS credentials in the .env file[/yellow]")
        sys.exit(1)
    
    except UPSTrackingError as e:
        console.print(f"[red]UPS Tracking Error: {e}[/red]")
        sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if settings.debug:
            console.print_exception()
        sys.exit(1)


@app.command()
def health() -> None:
    """Check UPS API connectivity and credentials."""
    console.print("[bold blue]UPS Tracking Agent Health Check[/bold blue]")
    
    # Check credentials
    try:
        settings.validate_ups_credentials()
        console.print("[green]✓[/green] UPS credentials configured")
    except ValueError as e:
        console.print(f"[red]✗[/red] UPS credentials error: {e}")
        return
    
    try:
        settings.validate_openai_credentials()
        console.print("[green]✓[/green] OpenAI credentials configured")
    except ValueError as e:
        console.print(f"[red]✗[/red] OpenAI credentials error: {e}")
        return
    
    # Check API connectivity
    console.print(f"[blue]API Base URL:[/blue] {settings.ups_api_base}")
    console.print(f"[blue]Sandbox Mode:[/blue] {settings.ups_use_sandbox}")
    
    # Test API connection
    async def test_connection():
        try:
            client = UPSClient(
                client_id=settings.ups_client_id,
                client_secret=settings.ups_client_secret,
                account_number=settings.ups_account_number,
                api_base=settings.ups_api_base,
            )
            
            async with client:
                # Try to get access token
                await client._get_access_token()
                console.print("[green]✓[/green] UPS API connection successful")
                
        except Exception as e:
            console.print(f"[red]✗[/red] UPS API connection failed: {e}")
    
    asyncio.run(test_connection())


if __name__ == "__main__":
    app()
