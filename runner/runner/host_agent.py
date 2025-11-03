import logging

from fastapi import HTTPException

from .a2a_executor import A2ARemoteExecutor
from .agent_registry import AgentRegistry
from .memory import SessionMemory
from .models import (
    DelegationTrace,
    HostRunRequest,
    HostRunResponse,
)
from .skill_selector import SkillSelector

logger = logging.getLogger(__name__)


class HostAgent:
    def __init__(
        self,
        memory: SessionMemory,
        registry: AgentRegistry,
        executor: A2ARemoteExecutor,
        selector: SkillSelector,
        max_hops: int = 3,
    ):
        self.memory = memory
        self.registry = registry
        self.executor = executor
        self.selector = selector
        self.max_hops = max_hops

    async def handle(self, req: HostRunRequest) -> HostRunResponse:
        # delegation safety
        trace = req.delegation_trace or DelegationTrace(chain=[], hops=0)
        if trace.hops >= self.max_hops:
            raise HTTPException(status_code=400, detail="Max delegation depth reached")

        # record user message globally
        global_session = self.memory.append_global_user(req.token, req.prompt)

        # merge context overrides
        if req.context_overrides:
            self.memory.update_global_state(req.token, req.context_overrides)
            global_session = self.memory.get_global(req.token)

        # pick agent
        chosen_card, routing_scores = self._select_agent(req)
        if not chosen_card:
            raise HTTPException(status_code=404, detail="No suitable agent found")

        # update trace
        trace.chain.append(chosen_card.id)
        trace.hops += 1

        # per-agent (user)
        agent_session = self.memory.append_agent_user(req.token, chosen_card.id, req.prompt)

        # call remote agent
        try:
            output, raw = await self.executor.run(
                chosen_card,
                agent_session.messages,
                global_session,
                req.prompt,
            )
        except ValueError as ve:
            # Handle agent execution errors (endpoint unreachable, etc.)
            error_msg = str(ve)
            raise HTTPException(status_code=503, detail=f"Agent execution failed: {error_msg}")
        except Exception as e:
            # Handle other execution errors
            logger.error(f"Agent execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

        # per-agent (assistant)
        agent_session = self.memory.append_agent_assistant(req.token, chosen_card.id, output)
        global_session = self.memory.append_global_agent(req.token, output)

        # check for delegation
        delegate = raw.get("delegate")
        if delegate:
            # delegate is a dict: {agent_id?, prompt, context_overrides?}
            if not isinstance(delegate, dict):
                raise HTTPException(status_code=400, detail="Delegate must be a dict")

            delegate_prompt = delegate.get("prompt")
            if not delegate_prompt:
                raise HTTPException(status_code=400, detail="Delegate must include 'prompt' field")

            sub_req = HostRunRequest(
                prompt=delegate_prompt,
                token=req.token,
                force_agent_id=delegate.get("agent_id"),
                context_overrides=delegate.get("context_overrides"),
                delegation_trace=trace,
            )
            sub_resp = await self.handle(sub_req)

            # update shared state with delegated result
            self.memory.update_global_state(req.token, sub_resp.global_session.shared_state)
            combined_output = f"{output}\n\n[Delegated to {sub_resp.chosen_agent_id} → {sub_resp.output}]"
            global_session = self.memory.append_global_agent(req.token, combined_output)

            return HostRunResponse(
                chosen_agent_id=chosen_card.id,
                output=combined_output,
                session=agent_session,
                global_session=global_session,
                routing_scores=routing_scores,
            )

        # no delegation → normal return
        return HostRunResponse(
            chosen_agent_id=chosen_card.id,
            output=output,
            session=agent_session,
            global_session=global_session,
            routing_scores=routing_scores,
        )

    def _select_agent(self, req: HostRunRequest):
        if req.force_agent_id:
            card = self.registry.get(req.force_agent_id)
            if card:
                return card, {}
        agents = self.registry.list_agents()
        return self.selector.pick_best(req.prompt, agents)
