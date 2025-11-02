from typing import List, Dict, Tuple, Optional
from .models import A2AAgentCard


class SkillSelector:
    """
    Very simple scoring that prefers
    - skill overlap
    - domain match
    - lower priority number
    """

    def score(self, prompt: str, agents: List[A2AAgentCard]) -> Dict[str, float]:
        tokens = set(prompt.lower().split())
        scores: Dict[str, float] = {}

        for a in agents:
            score = 0.0
            skillset = {s.lower() for s in (a.skills or [])}
            overlap = tokens.intersection(skillset)
            score += len(overlap) * 2.0

            if a.domain and a.domain.lower() in prompt.lower():
                score += 1.5

            # small bonus for priority
            score += max(0, 5 - a.priority) * 0.2

            scores[a.id] = score

        return scores

    def pick_best(self, prompt: str, agents: List[A2AAgentCard]) -> Tuple[Optional[A2AAgentCard], Dict[str, float]]:
        if not agents:
            return None, {}

        scores = self.score(prompt, agents)
        best_id = max(scores, key=lambda k: scores[k])
        best_agent = next(a for a in agents if a.id == best_id)
        return best_agent, scores

