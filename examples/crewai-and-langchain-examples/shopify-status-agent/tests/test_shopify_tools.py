"""Tests for Shopify tools."""

import pytest
from unittest.mock import AsyncMock, patch

from app.tools.shopify import ShopifyOrderTool, ShopifyStatusTool, ShopifyTrackingTool


class TestShopifyOrderTool:
    """Test Shopify order tool."""
    
    @pytest.mark.asyncio
    async def test_mock_find_order_by_number(self):
        """Test finding order by number in mock mode."""
        tool = ShopifyOrderTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun("1001")
            
            assert "Found order:" in result
            assert "1001" in result
            assert "customer1***@example.com" in result  # PII should be masked
    
    @pytest.mark.asyncio
    async def test_mock_find_order_not_found(self):
        """Test finding non-existent order in mock mode."""
        tool = ShopifyOrderTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun("9999")
            
            assert "No order found" in result
    
    @pytest.mark.asyncio
    async def test_mock_find_order_by_email(self):
        """Test finding order by email in mock mode."""
        tool = ShopifyOrderTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun("1001", email="customer1@example.com")
            
            assert "Found order:" in result
            assert "customer1***@example.com" in result  # PII should be masked
    
    @pytest.mark.asyncio
    async def test_real_api_not_configured(self):
        """Test real API when not configured."""
        tool = ShopifyOrderTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = False
            mock_settings.shopify_base_url = ""
            mock_settings.shopify_access_token = None
            
            result = await tool._arun("1001")
            
            assert "Shopify API not configured" in result


class TestShopifyStatusTool:
    """Test Shopify status tool."""
    
    @pytest.mark.asyncio
    async def test_mock_get_order_status(self):
        """Test getting order status in mock mode."""
        tool = ShopifyStatusTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun(1001)
            
            assert "Order 1001 status:" in result
            assert "shipped" in result
    
    @pytest.mark.asyncio
    async def test_mock_get_order_status_not_found(self):
        """Test getting status for non-existent order."""
        tool = ShopifyStatusTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun(9999)
            
            assert "No order found" in result


class TestShopifyTrackingTool:
    """Test Shopify tracking tool."""
    
    @pytest.mark.asyncio
    async def test_mock_get_tracking(self):
        """Test getting tracking info in mock mode."""
        tool = ShopifyTrackingTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun(1001)
            
            assert "Tracking info for order 1001:" in result
            assert "1Z999AA1234567890" in result
    
    @pytest.mark.asyncio
    async def test_mock_get_tracking_not_shipped(self):
        """Test getting tracking for unshipped order."""
        tool = ShopifyTrackingTool()
        
        with patch('app.tools.shopify.settings') as mock_settings:
            mock_settings.mock_mode = True
            
            result = await tool._arun(1002)
            
            assert "Tracking info for order 1002:" in result
            assert "Not yet shipped" in result


def test_mask_pii():
    """Test PII masking function."""
    from app.tools.shopify import mask_pii
    
    # Test email masking
    assert mask_pii("customer@example.com") == "customer***@example.com"
    assert mask_pii("test.user@domain.co.uk") == "test.user***@domain.co.uk"
    
    # Test phone masking
    assert mask_pii("+1-555-123-4567") == "***-***-4567"
    assert mask_pii("(555) 123-4567") == "***-***-4567"
    
    # Test combined
    text = "Contact customer@example.com or call +1-555-123-4567"
    masked = mask_pii(text)
    assert "customer***@example.com" in masked
    assert "***-***-4567" in masked
