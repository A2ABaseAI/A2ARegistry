"""
Tests for the A2A Host Orchestrator.
"""
import pytest
from runner.models import A2AAgentCard, HostRunRequest
from runner.agent_registry import AgentRegistry
from runner.memory import SessionMemory
from runner.skill_selector import SkillSelector


def test_agent_registry():
    """Test agent registry operations."""
    registry = AgentRegistry()
    card = A2AAgentCard(
        id="test-agent",
        name="Test Agent",
        endpoint="https://example.com/agent",
    )
    registry.register(card)
    assert registry.get("test-agent") == card
    assert len(registry.list_agents()) == 1


def test_memory():
    """Test memory operations."""
    memory = SessionMemory()
    token = "test-token"
    agent_id = "test-agent"
    
    # Test global session
    global_session = memory.get_global(token)
    assert global_session.token == token
    assert len(global_session.messages) == 0
    
    # Test appending messages
    memory.append_global_user(token, "Hello")
    global_session = memory.get_global(token)
    assert len(global_session.messages) == 1
    assert global_session.messages[0].content == "Hello"
    
    # Test agent session
    agent_session = memory.get_agent_session(token, agent_id)
    assert agent_session.agent_id == agent_id
    assert agent_session.token == token


def test_skill_selector():
    """Test skill-based agent selection."""
    selector = SkillSelector()
    agents = [
        A2AAgentCard(
            id="shopify",
            name="Shopify Agent",
            skills=["shopify", "orders"],
            domain="ecommerce",
            endpoint="https://example.com/shopify",
            priority=1,
        ),
        A2AAgentCard(
            id="ups",
            name="UPS Agent",
            skills=["ups", "tracking"],
            domain="logistics",
            endpoint="https://example.com/ups",
            priority=2,
        ),
    ]
    
    prompt = "check my shopify orders"
    scores = selector.score(prompt, agents)
    assert scores["shopify"] > scores["ups"]
    
    best_agent, all_scores = selector.pick_best(prompt, agents)
    assert best_agent.id == "shopify"

