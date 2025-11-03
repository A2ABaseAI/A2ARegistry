import asyncio
import logging
from contextlib import asynccontextmanager

from a2a_reg_sdk import A2ARegClient
from a2a_reg_sdk.models import Agent
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .a2a_executor import A2ARemoteExecutor
from .agent_registry import AgentRegistry
from .config import settings
from .host_agent import HostAgent
from .memory import SessionMemory
from .models import HostRunRequest, HostRunResponse
from .skill_selector import SkillSelector
from .utils import agent_to_card

logger = logging.getLogger(__name__)

memory = SessionMemory()
executor = A2ARemoteExecutor()
registry = AgentRegistry()
selector = SkillSelector()
host = HostAgent(memory, registry, executor, selector, max_hops=3)

# Registry client for loading agents
registry_client: A2ARegClient | None = None


async def load_agents_from_registry():
    """Load agents from the A2A registry using the Python SDK."""
    global registry_client

    try:
        # Initialize registry client with authentication
        # Authentication is required to get full agent details (including endpoints)
        if settings.registry_api_key:
            registry_client = A2ARegClient(
                registry_url=settings.registry_url,
                api_key=settings.registry_api_key,
            )
            logger.info("Using API key authentication for registry")
        elif settings.registry_client_id and settings.registry_client_secret:
            registry_client = A2ARegClient(
                registry_url=settings.registry_url,
                client_id=settings.registry_client_id,
                client_secret=settings.registry_client_secret,
            )
            registry_client.authenticate()
            logger.info("Using OAuth authentication for registry")
        else:
            # No auth - log warning but try anyway (will likely fail to get full details)
            logger.warning("No authentication configured for registry. " "Set REGISTRY_API_KEY or REGISTRY_CLIENT_ID/SECRET to load agents with endpoints.")
            registry_client = A2ARegClient(registry_url=settings.registry_url)

        # Load agents
        logger.info(f"Loading agents from registry at {settings.registry_url}")

        # Fetch agents in pages
        page = 1
        limit = 50  # Fetch 50 at a time
        total_loaded = 0

        # Clear existing registry
        registry._agents.clear()

        while True:
            try:
                agents_response = registry_client.list_agents(public_only=True, page=page, limit=limit)

                agents_list = agents_response.get("items", [])
                if not agents_list:
                    break

                # Convert and register agents
                for agent_item in agents_list:
                    try:
                        # Get agent ID from item
                        agent_id = agent_item.get("id") or agent_item.get("agent_id") or agent_item.get("agentId")
                        if not agent_id:
                            logger.warning(f"Skipping agent item with no ID: {agent_item}")
                            continue

                        # Try to fetch full agent details
                        agent = None

                        try:
                            # Use SDK to get full agent details
                            agent = registry_client.get_agent(agent_id)

                            # Always try to get agent card for endpoint info
                            if not agent.location_url or not agent.agent_card:
                                try:
                                    agent_card = registry_client.get_agent_card(agent_id)
                                    # Update agent with card data if missing
                                    if not agent.agent_card:
                                        agent.agent_card = agent_card
                                    # Update location_url if missing but card has endpoint
                                    if not agent.location_url and agent_card:
                                        # Try to get endpoint from card
                                        endpoint = agent_card.url if agent_card.url else ""
                                        if not endpoint and agent_card.interface and agent_card.interface.additionalInterfaces:
                                            for iface in agent_card.interface.additionalInterfaces:
                                                if isinstance(iface, dict):
                                                    if iface.get("transport") == "http" and iface.get("url"):
                                                        endpoint = iface["url"]
                                                        break
                                                else:
                                                    if getattr(iface, "transport", None) == "http" and getattr(iface, "url", None):
                                                        endpoint = getattr(iface, "url")
                                                        break
                                        if endpoint:
                                            agent.location_url = endpoint
                                except Exception as card_error:
                                    logger.debug(f"Could not get agent card for {agent_id}: {card_error}")

                        except Exception as auth_error:
                            # If get_agent fails, try to use SDK's get_agent_card method directly
                            logger.debug(f"Could not get agent {agent_id} with auth, trying agent card: {auth_error}")

                            try:
                                # Use SDK's get_agent_card method
                                agent_card = registry_client.get_agent_card(agent_id)

                                # Extract endpoint from agent card
                                endpoint = agent_card.url if agent_card.url else ""

                                # Try to get endpoint from interface additionalInterfaces
                                if not endpoint and agent_card.interface and agent_card.interface.additionalInterfaces:
                                    for iface in agent_card.interface.additionalInterfaces:
                                        if isinstance(iface, dict):
                                            transport = iface.get("transport")
                                            url = iface.get("url")
                                        else:
                                            transport = getattr(iface, "transport", None)
                                            url = getattr(iface, "url", None)

                                        if transport == "http" and url:
                                            endpoint = url
                                            break

                                if endpoint:
                                    agent = Agent(
                                        id=agent_id,
                                        name=agent_card.name,
                                        description=agent_card.description or "",
                                        version=agent_card.version or "1.0.0",
                                        provider=agent_card.provider.organization if agent_card.provider else "unknown",
                                        location_url=endpoint,
                                        agent_card=agent_card,
                                    )
                                else:
                                    logger.warning(f"No endpoint found in agent card for {agent_id}")
                                    continue
                            except Exception as card_error:
                                logger.debug(f"Could not get agent card for {agent_id} via SDK: {card_error}")
                                # Skip agent if we can't get details
                                logger.warning(f"Skipping agent {agent_id}: unable to get agent details or endpoint")
                                continue

                        if not agent:
                            logger.warning(f"Could not create agent for {agent_id}")
                            continue

                        # Skip if agent doesn't have a valid endpoint
                        if not agent.location_url and not (agent.agent_card and agent.agent_card.url):
                            logger.warning(f"Skipping agent {agent.id or agent.name}: no endpoint found")
                            continue

                        # Convert to A2AAgentCard and register
                        card = agent_to_card(agent)
                        if not card:
                            logger.warning(f"Skipping agent {agent.id or agent.name}: no endpoint found")
                            continue
                        registry.register(card)
                        total_loaded += 1
                        logger.info(f"Registered agent: {card.id} ({card.name}) at {card.endpoint}")
                    except Exception as e:
                        logger.error(f"Failed to register agent {agent_item.get('id', 'unknown')}: {e}")
                        continue

                # Check if there are more pages
                # The API might return a "next" field or we can check if we got fewer than limit
                if len(agents_list) < limit:
                    break

                page += 1

                # Safety limit - don't load more than 500 agents
                if total_loaded >= 500:
                    logger.info("Reached maximum agent limit (500), stopping")
                    break

            except Exception as e:
                logger.error(f"Error loading page {page}: {e}")
                break

        logger.info(f"Loaded {total_loaded} agents from registry")

    except Exception as e:
        logger.error(f"Failed to load agents from registry: {e}")
        # Don't raise - allow service to start even if registry is unavailable


async def refresh_agents_periodically():
    """Periodically refresh agents from the registry."""
    while True:
        await asyncio.sleep(settings.agents_refresh_interval)
        try:
            await load_agents_from_registry()
        except Exception as e:
            logger.error(f"Error refreshing agents: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    if settings.load_agents_on_startup:
        await load_agents_from_registry()
        # Start background task to refresh agents
        asyncio.create_task(refresh_agents_periodically())

    yield

    # Shutdown
    if registry_client:
        registry_client.close()


app = FastAPI(
    title="A2A Host Orchestrator (Remote, Delegation)",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    agent_count = len(registry.list_agents())
    return {
        "status": "healthy",
        "agents_loaded": agent_count,
        "registry_url": settings.registry_url,
    }


@app.post("/host/run", response_model=HostRunResponse)
async def host_run(req: HostRunRequest):
    """Main entry point for running an agent."""
    return await host.handle(req)


@app.post("/agents/refresh")
async def refresh_agents():
    """Manually refresh agents from the registry."""
    try:
        await load_agents_from_registry()
        agents_count = len(registry.list_agents())
        return {
            "status": "success",
            "agents_count": agents_count,
            "message": f"Loaded {agents_count} agents from registry",
            "registry_url": settings.registry_url,
            "authenticated": settings.registry_api_key is not None or settings.registry_client_id is not None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh agents: {str(e)}")
