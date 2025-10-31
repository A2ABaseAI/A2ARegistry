#!/usr/bin/env python3
"""
Multi-Agent Orchestration Example - Using A2A SDK Framework Classes

This script demonstrates multi-agent orchestration patterns inspired by:
https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent

Key features:
1. Load agents from the A2A Registry using A2ACardResolver
2. Implement multi-agent orchestration and task delegation
3. Manage agent communication and workflow execution
4. Support for complex multi-agent workflows and coordination

Based on A2A SDK framework patterns and GitHub multi-agent samples.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Multi-Agent Orchestration Enums and Data Classes
class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStatus(Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    task_id: str
    agent_id: str
    message: str
    context_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class WorkflowStep:
    """Represents a step in a multi-agent workflow."""
    step_id: str
    agent_id: str
    task: AgentTask
    dependencies: List[str] = field(default_factory=list)
    parallel_execution: bool = False

@dataclass
class MultiAgentWorkflow:
    """Represents a multi-agent workflow."""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

# Import A2A SDK framework classes
try:
    from a2a.client import A2ACardResolver
    from a2a.server.agent_execution import AgentExecutor, RequestContext
    from a2a_reg_sdk import A2AClient
    import httpx
    SDK_AVAILABLE = True
    logger.info("✅ A2A SDK framework classes loaded successfully")
except ImportError as e:
    logger.error(f"❌ A2A SDK not available: {e}")
    logger.error("Please install the A2A SDK with: pip install a2a-sdk")
    SDK_AVAILABLE = False

# Import our SDK-based services
try:
    from app.services.agent_runner import A2AAgentRunner
    APP_SERVICE_AVAILABLE = True
    logger.info("✅ A2A Agent Runner service loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ App service not available (using standalone): {e}")
    APP_SERVICE_AVAILABLE = False


class MultiAgentOrchestrator(AgentExecutor):
    """
    Multi-agent orchestrator inspired by GitHub A2A samples multiagent patterns.
    Loads agents from registry and provides advanced orchestration capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.agents = {}
        self.execution_count = 0
        self.cancel_count = 0
        
        # Multi-agent orchestration state
        self.active_workflows: Dict[str, MultiAgentWorkflow] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.workflow_count = 0
        self.task_queue: List[AgentTask] = []
        
        # Agent coordination
        self.agent_connections: Dict[str, httpx.AsyncClient] = {}
        self.agent_capabilities: Dict[str, Dict[str, Any]] = {}
        
        # Initialize A2A SDK components
        registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
        api_key = os.getenv("A2A_REGISTRY_API_KEY", "dev-admin-api-key")
        
        self.client = A2AClient(registry_url=registry_url, api_key=api_key)
        
        # Initialize httpx client for A2ACardResolver with authentication
        self.httpx_client = httpx.AsyncClient()
        self.card_resolver = A2ACardResolver(base_url=registry_url, httpx_client=self.httpx_client)
        
        # Set up authentication headers for httpx client
        self.httpx_client.headers.update({
            "Authorization": f"Bearer {api_key}",
            "X-API-Key": api_key
        })
        
        logger.info("🚀 Multi-Agent Orchestrator initialized with SDK framework")
    
    async def create_workflow(self, name: str, steps_config: List[Dict[str, Any]]) -> MultiAgentWorkflow:
        """Create a multi-agent workflow."""
        workflow_id = str(uuid.uuid4())
        context_id = str(uuid.uuid4())
        
        steps = []
        for i, step_config in enumerate(steps_config):
            step_id = f"step_{i+1}"
            task_id = str(uuid.uuid4())
            
            task = AgentTask(
                task_id=task_id,
                agent_id=step_config["agent_id"],
                message=step_config["message"],
                context_id=context_id,
                metadata=step_config.get("metadata", {})
            )
            
            step = WorkflowStep(
                step_id=step_id,
                agent_id=step_config["agent_id"],
                task=task,
                dependencies=step_config.get("dependencies", []),
                parallel_execution=step_config.get("parallel", False)
            )
            steps.append(step)
        
        workflow = MultiAgentWorkflow(
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            context={"context_id": context_id}
        )
        
        self.active_workflows[workflow_id] = workflow
        self.workflow_count += 1
        
        logger.info(f"📋 Created workflow '{name}' with {len(steps)} steps")
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a multi-agent workflow."""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        logger.info(f"🚀 Starting workflow '{workflow.name}' ({workflow_id})")
        
        try:
            # Execute steps based on dependencies
            completed_steps = set()
            results = {}
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps that can be executed (dependencies satisfied)
                ready_steps = []
                for step in workflow.steps:
                    if step.step_id not in completed_steps:
                        if all(dep in completed_steps for dep in step.dependencies):
                            ready_steps.append(step)
                
                if not ready_steps:
                    raise Exception("No ready steps found - possible circular dependency")
                
                # Execute ready steps (parallel if specified)
                if any(step.parallel_execution for step in ready_steps):
                    # Execute parallel steps
                    tasks = [self._execute_step(step) for step in ready_steps]
                    step_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for step, result in zip(ready_steps, step_results):
                        if isinstance(result, Exception):
                            logger.error(f"❌ Step {step.step_id} failed: {result}")
                            workflow.status = WorkflowStatus.FAILED
                            return {"error": str(result), "failed_step": step.step_id}
                        
                        results[step.step_id] = result
                        completed_steps.add(step.step_id)
                        logger.info(f"✅ Completed step {step.step_id}")
                else:
                    # Execute sequential steps
                    for step in ready_steps:
                        try:
                            result = await self._execute_step(step)
                            results[step.step_id] = result
                            completed_steps.add(step.step_id)
                            logger.info(f"✅ Completed step {step.step_id}")
                        except Exception as e:
                            logger.error(f"❌ Step {step.step_id} failed: {e}")
                            workflow.status = WorkflowStatus.FAILED
                            return {"error": str(e), "failed_step": step.step_id}
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.results = results
            
            logger.info(f"🎉 Workflow '{workflow.name}' completed successfully")
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "execution_time": (workflow.completed_at - workflow.started_at).total_seconds()
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            logger.error(f"❌ Workflow '{workflow.name}' failed: {e}")
            return {"error": str(e), "workflow_id": workflow_id}
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step.task.status = TaskStatus.IN_PROGRESS
        step.task.started_at = datetime.now()
        
        try:
            # Get the agent information
            agent = self.agents.get(step.task.agent_id)
            if not agent:
                raise ValueError(f"Agent {step.task.agent_id} not found")
            
            # Call the agent directly using HTTP REST API
            result = await self._call_agent_directly(agent, step.task.message)
            
            step.task.status = TaskStatus.COMPLETED
            step.task.completed_at = datetime.now()
            step.task.result = result
            
            return result
            
        except Exception as e:
            step.task.status = TaskStatus.FAILED
            step.task.error = str(e)
            raise
    
    async def delegate_task_to_agent(self, agent_id: str, message: str, context_id: str = None) -> Dict[str, Any]:
        """Delegate a task to a specific agent (multi-agent coordination pattern)."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        task_id = str(uuid.uuid4())
        if not context_id:
            context_id = str(uuid.uuid4())
        
        task = AgentTask(
            task_id=task_id,
            agent_id=agent_id,
            message=message,
            context_id=context_id
        )
        
        self.active_tasks[task_id] = task
        self.task_queue.append(task)
        
        logger.info(f"📤 Delegating task to agent {agent_id}: {message[:50]}...")
        
        try:
            result = await self._execute_task(task)
            return result
        except Exception as e:
            logger.error(f"❌ Task delegation failed: {e}")
            raise
    
    async def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single task."""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        try:
            # Get the agent information
            agent = self.agents.get(task.agent_id)
            if not agent:
                raise ValueError(f"Agent {task.agent_id} not found")
            
            # Call the agent directly using HTTP REST API
            result = await self._call_agent_directly(agent, task.message)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            raise
    
    async def _call_agent_directly(self, agent: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Call an agent directly using HTTP REST API."""
        agent_url = agent["location"]["url"]
        chat_url = f"{agent_url}/chat"
        
        payload = {
            "message": message,
            "session_id": f"session_{uuid.uuid4().hex[:8]}"
        }
        
        logger.info(f"📡 Calling agent {agent['name']} at {chat_url}")
        logger.info(f"📦 Payload: {payload}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    chat_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Agent {agent['name']} responded successfully")
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to call agent {agent['name']}: {e}")
            raise
    
    async def coordinate_agents(self, coordination_config: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for a complex task (inspired by GitHub samples)."""
        logger.info("🤝 Starting multi-agent coordination")
        
        # Extract coordination parameters
        primary_agent = coordination_config.get("primary_agent")
        supporting_agents = coordination_config.get("supporting_agents", [])
        task_description = coordination_config.get("task_description", "")
        coordination_type = coordination_config.get("type", "sequential")
        
        results = {}
        context_id = str(uuid.uuid4())
        
        try:
            if coordination_type == "sequential":
                # Sequential coordination: agents work one after another
                logger.info("🔄 Executing sequential coordination")
                
                # Start with primary agent
                if primary_agent:
                    result = await self.delegate_task_to_agent(
                        primary_agent, 
                        task_description, 
                        context_id
                    )
                    results["primary"] = result
                
                # Then supporting agents
                for i, agent_id in enumerate(supporting_agents):
                    result = await self.delegate_task_to_agent(
                        agent_id,
                        f"Support task {i+1}: {task_description}",
                        context_id
                    )
                    results[f"supporting_{i+1}"] = result
            
            elif coordination_type == "parallel":
                # Parallel coordination: agents work simultaneously
                logger.info("⚡ Executing parallel coordination")
                
                tasks = []
                if primary_agent:
                    tasks.append(self.delegate_task_to_agent(
                        primary_agent, 
                        task_description, 
                        context_id
                    ))
                
                for i, agent_id in enumerate(supporting_agents):
                    tasks.append(self.delegate_task_to_agent(
                        agent_id,
                        f"Parallel task {i+1}: {task_description}",
                        context_id
                    ))
                
                parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                if primary_agent:
                    results["primary"] = parallel_results[0]
                    for i, result in enumerate(parallel_results[1:]):
                        results[f"parallel_{i+1}"] = result
            
            elif coordination_type == "workflow":
                # Workflow coordination: complex multi-step process
                logger.info("📋 Executing workflow coordination")
                
                workflow_steps = coordination_config.get("workflow_steps", [])
                workflow = await self.create_workflow(
                    f"Coordination Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    workflow_steps
                )
                
                workflow_result = await self.execute_workflow(workflow.workflow_id)
                results["workflow"] = workflow_result
            
            logger.info("✅ Multi-agent coordination completed")
            return {
                "coordination_type": coordination_type,
                "context_id": context_id,
                "results": results,
                "agents_involved": [primary_agent] + supporting_agents if primary_agent else supporting_agents
            }
            
        except Exception as e:
            logger.error(f"❌ Multi-agent coordination failed: {e}")
            return {"error": str(e), "coordination_type": coordination_type}
    
    async def execute(self, context: RequestContext):
        """Execute a task using the actual A2A SDK AgentExecutor interface."""
        try:
            self.execution_count += 1
            
            logger.info(f"📋 Executing task:")
            logger.info(f"  - Context ID: {context.context_id}")
            logger.info(f"  - Task ID: {context.task_id}")
            logger.info(f"  - Message: {context.message}")
            logger.info(f"  - Metadata: {context.metadata}")
            
            # Get agent ID from context metadata or use first available agent
            agent_id = context.metadata.get("agent_id") if context.metadata else None
            if not agent_id and self.agents:
                agent_id = list(self.agents.keys())[0]
            
            if not agent_id or agent_id not in self.agents:
                raise ValueError(f"No agent available for execution. Available agents: {list(self.agents.keys())}")
            
            agent = self.agents[agent_id]
            agent_url = agent.get("location", {}).get("url")
            
            if not agent_url:
                raise ValueError(f"Agent {agent_id} has no service URL")
            
            logger.info(f"🎯 Executing task with agent: {agent['name']} ({agent_id})")
            logger.info(f"🔗 Agent URL: {agent_url}")
            
            # Make actual API call to the agent
            result = await self._call_agent_api(agent_url, context, agent)
            
            logger.info(f"✅ Task executed successfully with agent {agent_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            raise
    
    async def _call_agent_api(self, agent_url: str, context: RequestContext, agent: dict):
        """Make actual API call to the agent service."""
        try:
            # Prepare the request payload
            payload = {
                "message": context.message or "Hello from A2A Agent Runner",
                "context_id": context.context_id,
                "task_id": context.task_id,
                "metadata": context.metadata or {}
            }
            
            # Add agent-specific headers if needed
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "A2A-Agent-Runner/1.0"
            }
            
            logger.info(f"📡 Making API call to: {agent_url}")
            logger.info(f"📦 Payload: {payload}")
            
            # Make the actual HTTP request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    agent_url,
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result_data = response.json()
                    logger.info(f"✅ Agent response: {result_data}")
                    
                    return {
                        "status": "completed",
                        "context_id": context.context_id,
                        "task_id": context.task_id,
                        "message": context.message,
                        "agent_id": agent.get("id"),
                        "agent_name": agent.get("name"),
                        "agent_response": result_data,
                        "execution_count": self.execution_count
                    }
                else:
                    error_msg = f"Agent returned status {response.status_code}: {response.text}"
                    logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout calling agent at {agent_url}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request error calling agent at {agent_url}: {e}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error calling agent at {agent_url}: {e}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    async def cancel(self, context: RequestContext):
        """Cancel a task using the actual A2A SDK AgentExecutor interface."""
        try:
            self.cancel_count += 1
            
            logger.info(f"🛑 Cancelling task:")
            logger.info(f"  - Context ID: {context.context_id}")
            logger.info(f"  - Task ID: {context.task_id}")
            
            # Get agent ID from context metadata or use first available agent
            agent_id = context.metadata.get("agent_id") if context.metadata else None
            if not agent_id and self.agents:
                agent_id = list(self.agents.keys())[0]
            
            if not agent_id or agent_id not in self.agents:
                logger.warning(f"No agent available for cancellation. Available agents: {list(self.agents.keys())}")
                return
            
            agent = self.agents[agent_id]
            agent_url = agent.get("location", {}).get("url")
            
            if not agent_url:
                logger.warning(f"Agent {agent_id} has no service URL for cancellation")
                return
            
            logger.info(f"🎯 Cancelling task with agent: {agent['name']} ({agent_id})")
            logger.info(f"🔗 Agent URL: {agent_url}")
            
            # Make actual cancellation call to the agent
            await self._cancel_agent_task(agent_url, context, agent)
            
            logger.info(f"✅ Task cancelled successfully with agent {agent_id} (cancel count: {self.cancel_count})")
            
        except Exception as e:
            logger.error(f"❌ Task cancellation failed: {e}")
            raise
    
    async def _cancel_agent_task(self, agent_url: str, context: RequestContext, agent: dict):
        """Make actual cancellation call to the agent service."""
        try:
            # Prepare the cancellation payload
            payload = {
                "action": "cancel",
                "context_id": context.context_id,
                "task_id": context.task_id,
                "metadata": context.metadata or {}
            }
            
            # Add agent-specific headers if needed
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "A2A-Agent-Runner/1.0"
            }
            
            logger.info(f"📡 Making cancellation call to: {agent_url}")
            logger.info(f"📦 Cancellation payload: {payload}")
            
            # Make the actual HTTP request for cancellation
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    agent_url,
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"📊 Cancellation response status: {response.status_code}")
                
                if response.status_code in [200, 202, 204]:
                    logger.info(f"✅ Task cancellation request sent successfully")
                else:
                    logger.warning(f"⚠️ Agent returned status {response.status_code} for cancellation: {response.text}")
                    
        except httpx.TimeoutException:
            logger.warning(f"⚠️ Timeout sending cancellation to agent at {agent_url}")
        except httpx.RequestError as e:
            logger.warning(f"⚠️ Request error sending cancellation to agent at {agent_url}: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Error sending cancellation to agent at {agent_url}: {e}")
    
    async def load_agents_from_registry(self, limit: int = 100) -> int:
        """Load agents from the A2A Registry using SDK components."""
        logger.info(f"🔍 Loading agents from registry using A2A SDK...")
        
        try:
            # Authenticate with the registry
            self.client.authenticate()
            
            # Get agents from registry using SDK
            agents_response = self.client.list_agents(page=1, limit=limit, public_only=True)
            agents = agents_response.get("items", [])
            
            logger.info(f"📋 Found {len(agents)} agents in registry")
            
            # Process each agent using direct API calls
            loaded_count = 0
            for agent_summary in agents:
                try:
                    agent_id = agent_summary.get("id")
                    if agent_id:
                        # Get agent card directly using authenticated API
                        agent_card = await self._get_agent_card_directly(agent_id)
                        if agent_card:
                            await self._load_agent_from_card(agent_id, agent_card)
                            loaded_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to load agent {agent_summary.get('id', 'unknown')}: {e}")
            
            logger.info(f"✅ Loaded {loaded_count} agents using A2A SDK")
            return loaded_count
            
        except Exception as e:
            logger.error(f"❌ Failed to load agents from registry: {e}")
            return 0
    
    async def _load_agent_from_card(self, agent_id: str, agent_card: dict):
        """Load an individual agent from its card using SDK."""
        try:
            # Use the SDK's convert_to_card_spec function to properly parse the card
            card_spec = self.client._convert_to_card_spec(agent_card)
            
            # Extract agent information from converted card spec
            agent_name = card_spec.get("name", "Unknown Agent")
            description = card_spec.get("description", "")
            
            # Get service URL from agent card - check multiple locations
            service_url = None
            registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
            
            # First try the main URL field
            service_url = agent_card.get("url")
            
            # If main URL is registry URL, try additionalInterfaces
            if not service_url or service_url.startswith(registry_url):
                interface = agent_card.get("interface", {})
                if interface.get("additionalInterfaces"):
                    for additional_interface in interface["additionalInterfaces"]:
                        if additional_interface.get("transport") == "http":
                            url = additional_interface.get("url")
                            if url and not url.startswith(registry_url):
                                service_url = url
                                break
            
            # If still no good URL, try card spec
            if not service_url or service_url.startswith(registry_url):
                service_url = card_spec.get("url")
                if service_url and service_url.startswith(registry_url):
                    service_url = None
                
                if not service_url:
                    interface = card_spec.get("interface", {})
                    if interface.get("additionalInterfaces"):
                        for additional_interface in interface["additionalInterfaces"]:
                            if additional_interface.get("transport") == "http":
                                url = additional_interface.get("url")
                                if url and not url.startswith(registry_url):
                                    service_url = url
                                    break
            
            if not service_url:
                logger.warning(f"⚠️ No valid service URL found for agent {agent_id}")
                return
            
            # Store agent information using the converted card spec
            self.agents[agent_id] = {
                "id": agent_id,
                "name": agent_name,
                "description": description,
                "location": {"url": service_url, "type": "api_endpoint"},
                "tags": agent_card.get("tags", []),  # Keep original tags
                "capabilities": card_spec.get("capabilities", {}),
                "auth_schemes": card_spec.get("securitySchemes", []),
                "skills": card_spec.get("skills", {}),
                "agent_card": card_spec,  # Store the converted card spec
                "status": "loaded",
                "loaded_at": "2024-01-01T00:00:00Z"
            }
            
            logger.info(f"✅ Loaded agent: {agent_name} ({agent_id}) -> {service_url}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load agent {agent_id}: {e}")
    
    async def _get_agent_card_directly(self, agent_id: str) -> dict:
        """Get agent card directly using the registry API with authentication."""
        try:
            # Use the authenticated httpx client to get agent card
            registry_url = os.getenv("A2A_REGISTRY_URL", "http://localhost:8000")
            response = await self.httpx_client.get(f"{registry_url}/agents/{agent_id}/card")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get agent card for {agent_id}: {e}")
            return {}
    
    
    async def discover_agents(self, query: str = None, tags: List[str] = None) -> List[Dict]:
        """Discover agents using SDK components."""
        logger.info(f"🔍 Discovering agents using SDK framework...")
        
        try:
            discovered_agents = []
            
            # Search by query
            if query:
                for agent_id, agent in self.agents.items():
                    if (query.lower() in agent.get("name", "").lower() or 
                        query.lower() in agent.get("description", "").lower()):
                        discovered_agents.append(agent)
            
            # Search by tags
            if tags:
                for agent_id, agent in self.agents.items():
                    agent_tags = agent.get("tags", [])
                    if any(tag in agent_tags for tag in tags):
                        if agent not in discovered_agents:
                            discovered_agents.append(agent)
            
            logger.info(f"✅ Found {len(discovered_agents)} agents using SDK discovery")
            return discovered_agents
            
        except Exception as e:
            logger.error(f"❌ Failed to discover agents: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get orchestrator statistics including multi-agent capabilities."""
        return {
            "agents_loaded": len(self.agents),
            "execution_count": self.execution_count,
            "cancel_count": self.cancel_count,
            "sdk_available": SDK_AVAILABLE,
            "active_sessions": 0,
            "workflows_created": self.workflow_count,
            "active_workflows": len(self.active_workflows),
            "active_tasks": len(self.active_tasks),
            "tasks_queued": len(self.task_queue),
            "multi_agent_capabilities": {
                "workflow_orchestration": True,
                "task_delegation": True,
                "agent_coordination": True,
                "parallel_execution": True,
                "sequential_execution": True
            }
        }


class MultiAgentOrchestrationExample:
    """Example demonstrating multi-agent orchestration capabilities inspired by GitHub A2A samples."""
    
    def __init__(self):
        """Initialize the example."""
        if not SDK_AVAILABLE:
            raise ImportError("A2A SDK is required. Install with: pip install a2a-sdk")
        
        # Use the new MultiAgentOrchestrator
        self.orchestrator = MultiAgentOrchestrator()
        logger.info("🚀 Multi-Agent Orchestration Example initialized")
    
    async def run_example(self):
        """Run the complete multi-agent orchestration example."""
        try:
            print("="*70)
            print("MULTI-AGENT ORCHESTRATION EXAMPLE - INSPIRED BY GITHUB A2A SAMPLES")
            print()
            
            # Step 1: Load agents from registry using SDK
            await self.step1_load_agents_with_sdk()
            
            # Step 2: Discover agents using SDK components
            await self.step2_discover_agents_with_sdk()
            
            # Step 3: Demonstrate multi-agent task delegation
            await self.step3_demonstrate_task_delegation()
            
            # Step 4: Demonstrate multi-agent coordination
            await self.step4_demonstrate_agent_coordination()
            
            # Step 5: Demonstrate customer service workflow (Shopify + UPS)
            await self.step5_demonstrate_customer_service_workflow()
            
            # Step 6: Demonstrate advanced coordination patterns
            await self.step6_demonstrate_advanced_coordination_patterns()
            
            # Step 7: Show multi-agent statistics
            await self.step7_show_multi_agent_stats()
            
            print("\n🎉 Multi-Agent Orchestration Example completed successfully!")
            print("✨ This implementation combines GitHub A2A samples patterns with registry-based agent loading!")
            
        except Exception as e:
            logger.error(f"❌ Example failed: {e}")
            raise
    
    async def step1_load_agents_with_sdk(self):
        """Step 1: Load agents using A2A SDK framework."""
        print("\n📋 Step 1: Loading agents using A2A SDK framework...")
        
        try:
            loaded_count = await self.orchestrator.load_agents_from_registry(limit=50)
            
            print(f"✅ Loaded {loaded_count} agents using A2A SDK")
            print(f"📊 Total agents available: {len(self.orchestrator.agents)}")
            print(f"🔧 SDK Components:")
            print(f"  - A2AClient: {type(self.orchestrator.client).__name__}")
            print(f"  - A2ACardResolver: {type(self.orchestrator.card_resolver).__name__}")
            print(f"  - MultiAgentOrchestrator: {type(self.orchestrator).__name__}")
            
            # Show some agent details
            if self.orchestrator.agents:
                print("\n🔍 Sample agents loaded with SDK:")
                for i, (agent_id, agent) in enumerate(list(self.orchestrator.agents.items())[:3]):
                    print(f"  {i+1}. {agent['name']} ({agent_id})")
                    print(f"     Description: {agent['description'][:100]}...")
                    print(f"     URL: {agent.get('location', {}).get('url', 'N/A')}")
                    print(f"     Agent Card: {'Available' if agent.get('agent_card') else 'Not available'}")
                    print()
            
        except Exception as e:
            logger.error(f"❌ Failed to load agents with SDK: {e}")
            print(f"⚠️ No agents loaded: {e}")
    
    async def step2_discover_agents_with_sdk(self):
        """Step 2: Discover agents using SDK components."""
        print("\n🔍 Step 2: Discovering agents using SDK framework...")
        
        try:
            # Discover agents by query using SDK-based discovery
            print("Searching for agents with 'shopify' in name or description...")
            shopify_agents = await self.orchestrator.discover_agents(query="shopify")
            print(f"Found {len(shopify_agents)} agents matching 'shopify'")
            
            # Discover agents by tags using SDK-based discovery
            print("\nSearching for agents with 'ecommerce' tag...")
            ecommerce_agents = await self.orchestrator.discover_agents(tags=["ecommerce"])
            print(f"Found {len(ecommerce_agents)} agents with 'ecommerce' tag")
            
            # Show discovered agents
            if shopify_agents:
                print("\n🛍️ Shopify-related agents (SDK-loaded):")
                for agent in shopify_agents[:2]:
                    print(f"  - {agent['name']}: {agent['description'][:80]}...")
                    print(f"    Agent Card: {'Available' if agent.get('agent_card') else 'Not available'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to discover agents with SDK: {e}")
            print(f"⚠️ Agent discovery failed: {e}")
    
    async def step3_demonstrate_task_delegation(self):
        """Step 3: Demonstrate multi-agent task delegation (GitHub samples pattern)."""
        print("\n📤 Step 3: Demonstrating multi-agent task delegation...")
        
        try:
            if not self.orchestrator.agents:
                print("⚠️ No agents available for task delegation demonstration")
                return
            
            # Get first available agent for demonstration
            agent_id = list(self.orchestrator.agents.keys())[0]
            agent = self.orchestrator.agents[agent_id]
            
            print(f"🎯 Delegating task to agent: {agent['name']} ({agent_id})")
            
            # Demonstrate task delegation
            task_message = "Please help me with a sample task to demonstrate multi-agent coordination"
            
            try:
                result = await self.orchestrator.delegate_task_to_agent(
                    agent_id=agent_id,
                    message=task_message
                )
                
                print(f"✅ Task delegation successful!")
                print(f"📊 Result: {str(result)[:100]}..." if result else "No result returned")
                
            except Exception as e:
                print(f"⚠️ Task delegation failed: {e}")
                print("This is expected if no actual agent services are running")
            
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate task delegation: {e}")
            print(f"⚠️ Task delegation demonstration failed: {e}")
    
    async def step4_demonstrate_agent_coordination(self):
        """Step 4: Demonstrate multi-agent coordination (GitHub samples pattern)."""
        print("\n🤝 Step 4: Demonstrating multi-agent coordination...")
        
        try:
            if len(self.orchestrator.agents) < 2:
                print("⚠️ Need at least 2 agents for coordination demonstration")
                return
            
            # Get available agents
            agent_ids = list(self.orchestrator.agents.keys())
            primary_agent = agent_ids[0]
            supporting_agents = agent_ids[1:min(3, len(agent_ids))]  # Use up to 2 supporting agents
            
            print(f"🎯 Primary agent: {self.orchestrator.agents[primary_agent]['name']}")
            print(f"🤖 Supporting agents: {[self.orchestrator.agents[aid]['name'] for aid in supporting_agents]}")
            
            # Demonstrate sequential coordination
            print("\n🔄 Demonstrating sequential coordination...")
            sequential_config = {
                "type": "sequential",
                "primary_agent": primary_agent,
                "supporting_agents": supporting_agents,
                "task_description": "Demonstrate sequential multi-agent coordination"
            }
            
            try:
                sequential_result = await self.orchestrator.coordinate_agents(sequential_config)
                print(f"✅ Sequential coordination completed!")
                print(f"📊 Agents involved: {sequential_result.get('agents_involved', [])}")
                
            except Exception as e:
                print(f"⚠️ Sequential coordination failed: {e}")
                print("This is expected if no actual agent services are running")
            
            # Demonstrate parallel coordination
            print("\n⚡ Demonstrating parallel coordination...")
            parallel_config = {
                "type": "parallel",
                "primary_agent": primary_agent,
                "supporting_agents": supporting_agents,
                "task_description": "Demonstrate parallel multi-agent coordination"
            }
            
            try:
                parallel_result = await self.orchestrator.coordinate_agents(parallel_config)
                print(f"✅ Parallel coordination completed!")
                print(f"📊 Agents involved: {parallel_result.get('agents_involved', [])}")
                
            except Exception as e:
                print(f"⚠️ Parallel coordination failed: {e}")
                print("This is expected if no actual agent services are running")
            
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate agent coordination: {e}")
            print(f"⚠️ Agent coordination demonstration failed: {e}")
    
    async def step5_demonstrate_customer_service_workflow(self):
        """Step 5: Demonstrate customer service workflow with Shopify and UPS agents."""
        print("\n🛍️ Step 5: Demonstrating Customer Service Workflow...")
        print("Scenario: Customer asks Shopify agent for order status, then delegates to UPS agent for tracking")
        
        try:
            # Find Shopify and UPS agents
            shopify_agents = await self.orchestrator.discover_agents(query="shopify")
            ups_agents = await self.orchestrator.discover_agents(query="ups")
            
            if not shopify_agents:
                print("❌ No Shopify agents found. Please register a Shopify agent first.")
                return
            
            if not ups_agents:
                print("❌ No UPS agents found. Please register a UPS agent first.")
                return
            
            # Get the first available agents
            shopify_agent = shopify_agents[0]
            ups_agent = ups_agents[0]
            
            print(f"🎯 Shopify Agent: {shopify_agent['name']} ({shopify_agent['id']})")
            print(f"📦 UPS Agent: {ups_agent['name']} ({ups_agent['id']})")
            
            # Create customer service workflow
            await self._create_customer_service_workflow(shopify_agent['id'], ups_agent['id'])
            
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate customer service workflow: {e}")
            print(f"❌ Customer service workflow demonstration failed: {e}")
            print("Please ensure both Shopify and UPS agents are registered and running.")
    
    async def _create_customer_service_workflow(self, shopify_agent_id: str, ups_agent_id: str):
        """Create and execute a customer service workflow."""
        print("\n📋 Creating Customer Service Workflow...")
        
        # Customer inquiry scenario
        customer_order_id = "ORD-2024-001"
        customer_message = f"What is the status of my order {customer_order_id}?"
        
        print(f"👤 Customer Inquiry: {customer_message}")
        
        # Step 1: Customer asks Shopify agent for order status
        print("\n🛍️ Step 1: Customer asks Shopify agent for order status...")
        
        shopify_task_message = f"""
        Customer Inquiry: {customer_message}
        
        Please help the customer by:
        1. Looking up order {customer_order_id}
        2. Providing order status and details
        3. If the order is shipped, get the tracking information
        4. If tracking info is available, delegate to UPS agent for detailed tracking
        
        Order ID: {customer_order_id}
        Customer: John Doe
        Expected delivery: Within 3-5 business days
        """
        
        # Delegate to Shopify agent
        shopify_result = await self.orchestrator.delegate_task_to_agent(
            agent_id=shopify_agent_id,
            message=shopify_task_message
        )
        
        print(f"✅ Shopify agent response received!")
        print(f"📊 Shopify Result: {str(shopify_result)[:200]}...")
        
        # Step 2: Shopify agent delegates to UPS agent for tracking
        print("\n📦 Step 2: Shopify agent delegates to UPS agent for tracking...")
        
        ups_task_message = f"""
        Tracking Request from Shopify Agent:
        
        Order ID: {customer_order_id}
        Tracking Number: 1Z999AA10123456784
        Customer: John Doe
        
        Please provide detailed tracking information including:
        1. Current location
        2. Estimated delivery date
        3. Delivery status
        4. Any delays or issues
        
        This is for customer order {customer_order_id} inquiry.
        """
        
        # Delegate to UPS agent
        ups_result = await self.orchestrator.delegate_task_to_agent(
            agent_id=ups_agent_id,
            message=ups_task_message
        )
        
        print(f"✅ UPS agent response received!")
        print(f"📊 UPS Result: {str(ups_result)[:200]}...")
        
        # Step 3: Compile final response for customer
        print("\n📋 Step 3: Compiling final response for customer...")
        
        final_response = {
            "customer_inquiry": customer_message,
            "order_id": customer_order_id,
            "shopify_response": shopify_result,
            "ups_tracking_response": ups_result,
            "final_status": "Order is shipped and being tracked",
            "summary": f"Order {customer_order_id} is currently in transit. Tracking shows it's on schedule for delivery."
        }
        
        print("🎉 Customer Service Workflow Completed!")
        print("="*60)
        print("FINAL CUSTOMER RESPONSE:")
        print("="*60)
        print(f"Order ID: {final_response['order_id']}")
        print(f"Status: {final_response['final_status']}")
        print(f"Summary: {final_response['summary']}")
        print("="*60)
        
        return final_response
    
    async def _demonstrate_mock_customer_service_workflow(self):
        """Demonstrate customer service workflow with mock data."""
        print("\n🎭 Demonstrating Customer Service Workflow with Mock Data...")
        
        # Mock customer scenario
        customer_order_id = "ORD-2024-001"
        customer_message = f"What is the status of my order {customer_order_id}?"
        
        print(f"👤 Customer Inquiry: {customer_message}")
        
        # Mock workflow steps
        workflow_steps = [
            {
                "agent_id": "shopify-agent-mock",
                "message": f"Customer inquiry about order {customer_order_id}. Please provide order status and tracking information.",
                "metadata": {
                    "step": 1,
                    "agent_type": "shopify",
                    "customer_order": customer_order_id
                }
            },
            {
                "agent_id": "ups-agent-mock", 
                "message": f"Tracking request for order {customer_order_id}. Tracking number: 1Z999AA10123456784. Provide detailed tracking status.",
                "dependencies": ["step_1"],
                "metadata": {
                    "step": 2,
                    "agent_type": "ups",
                    "tracking_number": "1Z999AA10123456784"
                }
            },
            {
                "agent_id": "customer-service-mock",
                "message": f"Compile final response for customer about order {customer_order_id}. Include both order status and tracking information.",
                "dependencies": ["step_1", "step_2"],
                "metadata": {
                    "step": 3,
                    "agent_type": "customer_service",
                    "final_response": True
                }
            }
        ]
        
        print(f"📋 Creating mock customer service workflow with {len(workflow_steps)} steps...")
        
        try:
            # Create workflow
            workflow = await self.orchestrator.create_workflow(
                name="Customer Service Order Inquiry Workflow",
                steps_config=workflow_steps
            )
            
            print(f"✅ Mock workflow created: {workflow.workflow_id}")
            print(f"📊 Workflow steps: {len(workflow.steps)}")
            
            # Execute workflow
            print("\n🚀 Executing mock customer service workflow...")
            
            workflow_result = await self.orchestrator.execute_workflow(workflow.workflow_id)
            
            if "error" in workflow_result:
                print(f"⚠️ Mock workflow execution failed: {workflow_result['error']}")
                print("This is expected in mock mode - demonstrating the workflow structure")
            else:
                print(f"✅ Mock workflow execution completed!")
                print(f"📊 Execution time: {workflow_result.get('execution_time', 0):.2f} seconds")
                print(f"📋 Steps completed: {len(workflow_result.get('results', {}))}")
            
            # Show mock final response
            print("\n🎭 MOCK CUSTOMER SERVICE RESPONSE:")
            print("="*60)
            print(f"Order ID: {customer_order_id}")
            print("Status: Order Shipped")
            print("Tracking Number: 1Z999AA10123456784")
            print("Current Location: In Transit - Memphis, TN")
            print("Estimated Delivery: Tomorrow by 6:00 PM")
            print("Summary: Your order is on schedule and will be delivered tomorrow.")
            print("="*60)
            
        except Exception as e:
            print(f"⚠️ Mock workflow demonstration failed: {e}")
    
    async def step6_demonstrate_advanced_coordination_patterns(self):
        """Step 6: Demonstrate advanced coordination patterns for customer service."""
        print("\n🤝 Step 6: Demonstrating Advanced Customer Service Coordination...")
        
        try:
            # Find available agents
            shopify_agents = await self.orchestrator.discover_agents(query="shopify")
            ups_agents = await self.orchestrator.discover_agents(query="ups")
            
            if not shopify_agents or not ups_agents:
                print("❌ Required agents not found. Please register both Shopify and UPS agents first.")
                return
            
            shopify_agent = shopify_agents[0]
            ups_agent = ups_agents[0]
            
            print(f"🎯 Available agents:")
            print(f"  - Shopify: {shopify_agent['name']}")
            print(f"  - UPS: {ups_agent['name']}")
            
            # Demonstrate different coordination patterns
            await self._demonstrate_coordination_patterns(shopify_agent['id'], ups_agent['id'])
            
        except Exception as e:
            logger.error(f"❌ Failed to demonstrate coordination patterns: {e}")
            print(f"❌ Coordination demonstration failed: {e}")
            print("Please ensure both Shopify and UPS agents are registered and running.")
    
    async def _demonstrate_coordination_patterns(self, shopify_agent_id: str, ups_agent_id: str):
        """Demonstrate different coordination patterns."""
        
        # Pattern 1: Sequential Customer Service
        print("\n🔄 Pattern 1: Sequential Customer Service")
        sequential_config = {
            "type": "sequential",
            "primary_agent": shopify_agent_id,
            "supporting_agents": [ups_agent_id],
            "task_description": "Customer order inquiry - check order status, then get tracking info"
        }
        
        try:
            sequential_result = await self.orchestrator.coordinate_agents(sequential_config)
            print(f"✅ Sequential coordination completed!")
            print(f"📊 Agents involved: {sequential_result.get('agents_involved', [])}")
        except Exception as e:
            print(f"⚠️ Sequential coordination failed: {e}")
        
        # Pattern 2: Parallel Information Gathering
        print("\n⚡ Pattern 2: Parallel Information Gathering")
        parallel_config = {
            "type": "parallel",
            "primary_agent": shopify_agent_id,
            "supporting_agents": [ups_agent_id],
            "task_description": "Gather order and tracking information simultaneously"
        }
        
        try:
            parallel_result = await self.orchestrator.coordinate_agents(parallel_config)
            print(f"✅ Parallel coordination completed!")
            print(f"📊 Agents involved: {parallel_result.get('agents_involved', [])}")
        except Exception as e:
            print(f"⚠️ Parallel coordination failed: {e}")
        
        # Pattern 3: Workflow-based Customer Service
        print("\n📋 Pattern 3: Workflow-based Customer Service")
        workflow_config = {
            "type": "workflow",
            "workflow_steps": [
                {
                    "agent_id": shopify_agent_id,
                    "message": "Step 1: Process customer order inquiry",
                    "metadata": {"step": 1, "task": "order_lookup"}
                },
                {
                    "agent_id": ups_agent_id,
                    "message": "Step 2: Get detailed tracking information",
                    "dependencies": ["step_1"],
                    "metadata": {"step": 2, "task": "tracking_lookup"}
                },
                {
                    "agent_id": shopify_agent_id,
                    "message": "Step 3: Compile final customer response",
                    "dependencies": ["step_1", "step_2"],
                    "metadata": {"step": 3, "task": "final_response"}
                }
            ]
        }
        
        try:
            workflow_result = await self.orchestrator.coordinate_agents(workflow_config)
            print(f"✅ Workflow coordination completed!")
            print(f"📊 Workflow result: {workflow_result.get('results', {})}")
        except Exception as e:
            print(f"❌ Workflow coordination failed: {e}")
            print("Please ensure both agents are running and accessible.")
    
    async def step7_show_multi_agent_stats(self):
        """Step 7: Show multi-agent orchestration statistics."""
        print("\n📊 Step 7: Multi-Agent Orchestration Statistics...")
        
        try:
            # Get orchestrator stats
            stats = self.orchestrator.get_stats()
            
            print("📈 Multi-Agent Orchestration Statistics:")
            print(f"  - SDK Available: {stats['sdk_available']}")
            print(f"  - Agents loaded: {stats['agents_loaded']}")
            print(f"  - Active workflows: {stats['active_workflows']}")
            print(f"  - Workflows created: {stats['workflows_created']}")
            print(f"  - Active tasks: {stats['active_tasks']}")
            print(f"  - Tasks queued: {stats['tasks_queued']}")
            print(f"  - Executions: {stats['execution_count']}")
            print(f"  - Cancellations: {stats['cancel_count']}")
            
            # Show multi-agent capabilities
            capabilities = stats.get('multi_agent_capabilities', {})
            print(f"\n🔧 Multi-Agent Capabilities:")
            for capability, enabled in capabilities.items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {capability.replace('_', ' ').title()}")
            
            # Show SDK components
            print(f"\n🔧 SDK Framework Components:")
            print(f"  - A2AClient: {type(self.orchestrator.client).__name__}")
            print(f"  - A2ACardResolver: {type(self.orchestrator.card_resolver).__name__}")
            print(f"  - MultiAgentOrchestrator: {type(self.orchestrator).__name__}")
            
            # Show available agents
            print(f"\n🤖 Available Agents ({len(self.orchestrator.agents)}):")
            for agent_id, agent in list(self.orchestrator.agents.items())[:5]:
                print(f"  - {agent['name']} ({agent_id})")
                print(f"    Status: {agent['status']}")
                print(f"    Loaded: {agent['loaded_at']}")
                print(f"    Agent Card: {'Available' if agent.get('agent_card') else 'Not available'}")
            
        except Exception as e:
            logger.error(f"❌ Failed to show multi-agent stats: {e}")
            print(f"⚠️ Statistics display failed: {e}")
    


async def main():
    """Main function."""
    print("🚀 Starting Multi-Agent Customer Service Orchestration Example")
    print("This example demonstrates customer service workflows with Shopify and UPS agents:")
    print("- Customer order inquiry processing")
    print("- Multi-agent task delegation and coordination")
    print("- Agent discovery from A2A Registry")
    print("- Complex customer service workflows")
    print()
    print("Scenario: Customer asks Shopify agent for order status, then delegates to UPS agent for tracking")
    print("Based on: https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent")
    print()
    
    if not SDK_AVAILABLE:
        print("❌ A2A SDK is not available!")
        print("Please install the A2A SDK with: pip install a2a-sdk")
        return 1
    
    try:
        example = MultiAgentOrchestrationExample()
        await example.run_example()
        
    except Exception as e:
        logger.error(f"❌ Example execution failed: {e}")
        print(f"\n❌ Example failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure A2A SDK is installed: pip install a2a-sdk")
        print("2. Ensure A2A Registry is running and accessible")
        print("3. Check that agents are registered in the registry")
        print("4. Verify network connectivity")
        print("5. Check API keys and authentication")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
