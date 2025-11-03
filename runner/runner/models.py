from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class A2AAgentCard(BaseModel):
    """
    Remote-only A2A Agent Card.
    """

    id: str
    name: str
    description: Optional[str] = None

    # routing metadata
    skills: List[str] = []
    domain: Optional[str] = None
    priority: int = 10

    # remote execution
    endpoint: str
    method: str = "POST"

    # misc
    metadata: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, Any]] = None


class AgentMessage(BaseModel):
    role: str
    content: str
    ts: datetime


class AgentSession(BaseModel):
    token: str
    agent_id: str
    messages: List[AgentMessage] = []
    state: Dict[str, Any] = {}


class GlobalSession(BaseModel):
    token: str
    messages: List[AgentMessage] = []
    shared_state: Dict[str, Any] = {}


class DelegateRequest(BaseModel):
    """
    This is what a REMOTE AGENT can send back to the HOST
    to ask it to call another agent.
    """

    agent_id: Optional[str] = None
    prompt: str
    context_overrides: Optional[Dict[str, Any]] = None


class DelegationTrace(BaseModel):
    """
    Used to prevent infinite delegation loops.
    """

    chain: List[str] = []
    hops: int = 0


class RunAgentRequest(BaseModel):
    agent_card: A2AAgentCard
    prompt: str
    token: str
    context_overrides: Optional[Dict[str, Any]] = None


class RunAgentResponse(BaseModel):
    output: str
    session: AgentSession
    global_session: GlobalSession


class HostRunRequest(BaseModel):
    prompt: str
    token: str
    force_agent_id: Optional[str] = None
    context_overrides: Optional[Dict[str, Any]] = None
    delegation_trace: Optional[DelegationTrace] = None


class HostRunResponse(BaseModel):
    chosen_agent_id: str
    output: str
    session: AgentSession
    global_session: GlobalSession
    routing_scores: Dict[str, float] = {}
