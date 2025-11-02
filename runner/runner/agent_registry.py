from typing import List, Dict, Optional
from .models import A2AAgentCard


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, A2AAgentCard] = {}

    def register(self, card: A2AAgentCard):
        self._agents[card.id] = card

    def list_agents(self) -> List[A2AAgentCard]:
        return list(self._agents.values())

    def get(self, agent_id: str) -> Optional[A2AAgentCard]:
        return self._agents.get(agent_id)

