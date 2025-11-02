from typing import Dict
from datetime import datetime
from .models import AgentSession, AgentMessage, GlobalSession


class SessionMemory:
    """
    Multi-level memory:
    - global per token
    - per-agent per (token, agent_id)
    """

    def __init__(self):
        self._per_agent: Dict[str, AgentSession] = {}
        self._global: Dict[str, GlobalSession] = {}

    # ---------- GLOBAL ----------

    def get_global(self, token: str) -> GlobalSession:
        if token not in self._global:
            self._global[token] = GlobalSession(token=token, messages=[], shared_state={})
        return self._global[token]

    def append_global_user(self, token: str, content: str) -> GlobalSession:
        g = self.get_global(token)
        g.messages.append(AgentMessage(role="user", content=content, ts=datetime.utcnow()))
        return g

    def append_global_agent(self, token: str, content: str) -> GlobalSession:
        g = self.get_global(token)
        g.messages.append(AgentMessage(role="assistant", content=content, ts=datetime.utcnow()))
        return g

    def update_global_state(self, token: str, new_state: dict) -> GlobalSession:
        g = self.get_global(token)
        g.shared_state.update(new_state)
        return g

    # ---------- PER AGENT ----------

    def _agent_key(self, token: str, agent_id: str) -> str:
        return f"{token}:{agent_id}"

    def get_agent_session(self, token: str, agent_id: str) -> AgentSession:
        key = self._agent_key(token, agent_id)
        if key not in self._per_agent:
            self._per_agent[key] = AgentSession(
                token=token,
                agent_id=agent_id,
                messages=[],
                state={},
            )
        return self._per_agent[key]

    def append_agent_user(self, token: str, agent_id: str, content: str) -> AgentSession:
        s = self.get_agent_session(token, agent_id)
        s.messages.append(AgentMessage(role="user", content=content, ts=datetime.utcnow()))
        return s

    def append_agent_assistant(self, token: str, agent_id: str, content: str) -> AgentSession:
        s = self.get_agent_session(token, agent_id)
        s.messages.append(AgentMessage(role="assistant", content=content, ts=datetime.utcnow()))
        return s

    def save_agent_session(self, session: AgentSession):
        key = self._agent_key(session.token, session.agent_id)
        self._per_agent[key] = session

