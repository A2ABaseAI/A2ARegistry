"""Tests for the LangChain agent."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agent import ShopifyAgent


class TestShopifyAgent:
    """Test Shopify agent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        with patch('app.agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock()
            return ShopifyAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent is not None
        assert len(agent.tools) == 3  # ShopifyOrderTool, ShopifyStatusTool, ShopifyTrackingTool
        assert agent.memory_store == {}
    
    def test_get_memory_new_session(self, agent):
        """Test getting memory for new session."""
        session_id = "test-session-123"
        memory = agent.get_memory(session_id)
        
        assert session_id in agent.memory_store
        assert memory is not None
        assert memory.memory_key == "chat_history"
    
    def test_get_memory_existing_session(self, agent):
        """Test getting memory for existing session."""
        session_id = "test-session-123"
        memory1 = agent.get_memory(session_id)
        memory2 = agent.get_memory(session_id)
        
        assert memory1 is memory2  # Same instance
    
    @pytest.mark.asyncio
    async def test_chat_success(self, agent):
        """Test successful chat interaction."""
        with patch.object(agent.agent_executor, 'ainvoke') as mock_invoke:
            mock_invoke.return_value = {
                "output": "I found your order #1001. It was shipped on 2024-01-12 via UPS."
            }
            
            result = await agent.chat("Where's my order #1001?")
            
            assert result["response"] == "I found your order #1001. It was shipped on 2024-01-12 via UPS."
            assert result["session_id"] is not None
            assert result["order_info"] is None  # No order info extracted in this case
    
    @pytest.mark.asyncio
    async def test_chat_with_order_info(self, agent):
        """Test chat with order information extraction."""
        with patch.object(agent.agent_executor, 'ainvoke') as mock_invoke:
            mock_invoke.return_value = {
                "output": "Found order: {\"id\": 1001, \"name\": \"#1001\", \"fulfillment_status\": \"fulfilled\"}"
            }
            
            result = await agent.chat("Where's my order #1001?")
            
            assert result["response"] is not None
            assert result["session_id"] is not None
            assert result["order_info"] is not None
            assert result["order_info"]["order_id"] == 1001
            assert result["order_info"]["order_number"] == "#1001"
            assert result["order_info"]["status"] == "fulfilled"
    
    @pytest.mark.asyncio
    async def test_chat_error_handling(self, agent):
        """Test chat error handling."""
        with patch.object(agent.agent_executor, 'ainvoke') as mock_invoke:
            mock_invoke.side_effect = Exception("Test error")
            
            result = await agent.chat("Where's my order #1001?")
            
            assert "I apologize, but I encountered an error" in result["response"]
            assert result["session_id"] is not None
            assert result["order_info"] is None
    
    @pytest.mark.asyncio
    async def test_stream_chat(self, agent):
        """Test streaming chat."""
        with patch.object(agent.agent_executor, 'astream') as mock_stream:
            # Mock streaming response
            async def mock_stream_generator():
                yield {"output": "I found your order"}
                yield {"intermediate_steps": [("find_order", "Order found")]}
            
            mock_stream.return_value = mock_stream_generator()
            
            chunks = []
            async for chunk in agent.stream_chat("Where's my order #1001?"):
                chunks.append(chunk)
            
            assert len(chunks) >= 2
            assert any(chunk["type"] == "content" for chunk in chunks)
            assert any(chunk["type"] == "tool_call" for chunk in chunks)
    
    def test_extract_order_info(self, agent):
        """Test order information extraction."""
        # Test with order info in response
        response_with_order = "Found order: {\"id\": 1001, \"name\": \"#1001\", \"fulfillment_status\": \"fulfilled\"}"
        order_info = agent._extract_order_info(response_with_order)
        
        assert order_info is not None
        assert order_info["order_id"] == 1001
        assert order_info["order_number"] == "#1001"
        assert order_info["status"] == "fulfilled"
        
        # Test without order info
        response_without_order = "I couldn't find that order."
        order_info = agent._extract_order_info(response_without_order)
        
        assert order_info is None
    
    def test_clear_memory(self, agent):
        """Test clearing memory."""
        session_id = "test-session-123"
        
        # Create memory
        agent.get_memory(session_id)
        assert session_id in agent.memory_store
        
        # Clear memory
        result = agent.clear_memory(session_id)
        assert result is True
        assert session_id not in agent.memory_store
        
        # Try to clear non-existent session
        result = agent.clear_memory("non-existent")
        assert result is False
    
    def test_get_session_count(self, agent):
        """Test getting session count."""
        assert agent.get_session_count() == 0
        
        agent.get_memory("session1")
        agent.get_memory("session2")
        
        assert agent.get_session_count() == 2
        
        agent.clear_memory("session1")
        
        assert agent.get_session_count() == 1
