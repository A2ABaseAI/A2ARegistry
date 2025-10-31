"""Shopify API tools for order lookup and tracking."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .config import settings


class FindOrderInput(BaseModel):
    """Input schema for find_order tool."""
    order_number: str = Field(..., description="Order number (with or without #)")
    email: Optional[str] = Field(default=None, description="Customer email")
    phone: Optional[str] = Field(default=None, description="Customer phone")


class GetOrderStatusInput(BaseModel):
    """Input schema for get_order_status tool."""
    order_id: int = Field(..., description="Order ID")


class GetTrackingInput(BaseModel):
    """Input schema for get_tracking tool."""
    order_id: int = Field(..., description="Order ID")


def mask_pii(text: str) -> str:
    """Mask PII in text (email, phone)."""
    if not text:
        return text
    
    # Mask email
    email_pattern = r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    text = re.sub(email_pattern, r'\1***@\2', text)
    
    # Mask phone (keep last 4 digits)
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    text = re.sub(phone_pattern, r'***-***-\4', text)
    
    return text


class ShopifyOrderTool(BaseTool):
    """Tool for finding orders in Shopify."""
    
    name = "find_order"
    description = "Find an order by order number, email, or phone. Returns order details if found."
    args_schema = FindOrderInput
    
    async def _arun(self, order_number: str, email: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Find order asynchronously."""
        try:
            # Clean order number (remove # if present)
            clean_order_number = order_number.lstrip('#')
            
            if settings.mock_mode:
                return await self._mock_find_order(clean_order_number, email, phone)
            
            # Real Shopify API call
            return await self._real_find_order(clean_order_number, email, phone)
            
        except Exception as e:
            return f"Error finding order: {str(e)}"
    
    def _run(self, order_number: str, email: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Find order synchronously."""
        import asyncio
        return asyncio.run(self._arun(order_number, email, phone))
    
    async def _mock_find_order(self, order_number: str, email: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Mock order lookup."""
        # Mock orders data
        mock_orders = {
            "1001": {
                "id": 1001,
                "name": "#1001",
                "email": "customer1@example.com",
                "phone": "+1-555-123-4567",
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "created_at": "2024-01-10T10:30:00Z",
                "updated_at": "2024-01-12T14:20:00Z",
                "total_price": "99.99",
                "currency": "USD",
                "line_items": [
                    {"title": "Wireless Headphones", "quantity": 1, "price": "99.99"}
                ],
                "fulfillments": [
                    {
                        "id": 1,
                        "status": "success",
                        "tracking_number": "1Z999AA1234567890",
                        "tracking_url": "https://www.ups.com/track?trackingNumber=1Z999AA1234567890",
                        "carrier": "UPS",
                        "created_at": "2024-01-12T14:20:00Z"
                    }
                ]
            },
            "1002": {
                "id": 1002,
                "name": "#1002",
                "email": "customer2@example.com",
                "phone": "+1-555-987-6543",
                "financial_status": "paid",
                "fulfillment_status": None,
                "created_at": "2024-01-15T09:15:00Z",
                "updated_at": "2024-01-15T09:15:00Z",
                "total_price": "49.99",
                "currency": "USD",
                "line_items": [
                    {"title": "Phone Case", "quantity": 2, "price": "24.99"}
                ],
                "fulfillments": []
            },
            "1003": {
                "id": 1003,
                "name": "#1003",
                "email": "customer3@example.com",
                "phone": "+1-555-456-7890",
                "financial_status": "paid",
                "fulfillment_status": "delivered",
                "created_at": "2024-01-08T16:45:00Z",
                "updated_at": "2024-01-14T11:30:00Z",
                "total_price": "149.99",
                "currency": "USD",
                "line_items": [
                    {"title": "Laptop Stand", "quantity": 1, "price": "149.99"}
                ],
                "fulfillments": [
                    {
                        "id": 2,
                        "status": "success",
                        "tracking_number": "1Z999BB9876543210",
                        "tracking_url": "https://www.ups.com/track?trackingNumber=1Z999BB9876543210",
                        "carrier": "UPS",
                        "created_at": "2024-01-10T08:00:00Z"
                    }
                ]
            }
        }
        
        # Find order by number
        order = mock_orders.get(order_number)
        
        # If not found by number, try to find by email or phone
        if not order and (email or phone):
            for order_data in mock_orders.values():
                if email and order_data["email"].lower() == email.lower():
                    order = order_data
                    break
                if phone and order_data["phone"] == phone:
                    order = order_data
                    break
        
        if not order:
            return f"No order found for order number {order_number}" + (
                f" with email {mask_pii(email)}" if email else ""
            ) + (
                f" with phone {mask_pii(phone)}" if phone else ""
            )
        
        # Mask PII
        order["email"] = mask_pii(order["email"])
        order["phone"] = mask_pii(order["phone"])
        
        return f"Found order: {order}"
    
    async def _real_find_order(self, order_number: str, email: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Real Shopify API order lookup."""
        if not settings.shopify_base_url or not settings.shopify_access_token:
            return "Shopify API not configured. Please set SHOPIFY_SHOP and SHOPIFY_ACCESS_TOKEN."
        
        async with httpx.AsyncClient() as client:
            try:
                # Search by order number
                params = {
                    "status": "any",
                    "name": f"#{order_number}",
                    "limit": 1
                }
                
                response = await client.get(
                    f"{settings.shopify_base_url}/orders.json",
                    headers=settings.shopify_headers,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get("orders", [])
                    
                    if orders:
                        order = orders[0]
                        # Mask PII
                        order["email"] = mask_pii(order.get("email", ""))
                        order["phone"] = mask_pii(order.get("phone", ""))
                        return f"Found order: {order}"
                
                # If not found by order number, try email/phone search
                if email or phone:
                    search_params = {"status": "any", "limit": 10}
                    if email:
                        search_params["email"] = email
                    
                    response = await client.get(
                        f"{settings.shopify_base_url}/orders.json",
                        headers=settings.shopify_headers,
                        params=search_params,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        orders = data.get("orders", [])
                        
                        # Filter by phone if provided
                        if phone:
                            orders = [o for o in orders if o.get("phone") == phone]
                        
                        if orders:
                            order = orders[0]
                            # Mask PII
                            order["email"] = mask_pii(order.get("email", ""))
                            order["phone"] = mask_pii(order.get("phone", ""))
                            return f"Found order: {order}"
                
                return f"No order found for order number {order_number}" + (
                    f" with email {mask_pii(email)}" if email else ""
                ) + (
                    f" with phone {mask_pii(phone)}" if phone else ""
                )
                
            except httpx.RequestError as e:
                return f"Network error accessing Shopify API: {str(e)}"
            except Exception as e:
                return f"Error accessing Shopify API: {str(e)}"


class ShopifyStatusTool(BaseTool):
    """Tool for getting order status."""
    
    name = "get_order_status"
    description = "Get detailed status information for an order by order ID."
    args_schema = GetOrderStatusInput
    
    async def _arun(self, order_id: int) -> str:
        """Get order status asynchronously."""
        try:
            if settings.mock_mode:
                return await self._mock_get_order_status(order_id)
            
            # Real Shopify API call
            return await self._real_get_order_status(order_id)
            
        except Exception as e:
            return f"Error getting order status: {str(e)}"
    
    def _run(self, order_id: int) -> str:
        """Get order status synchronously."""
        import asyncio
        return asyncio.run(self._arun(order_id))
    
    async def _mock_get_order_status(self, order_id: int) -> str:
        """Mock order status lookup."""
        mock_orders = {
            1001: {"status": "shipped", "tracking": "1Z999AA1234567890"},
            1002: {"status": "processing", "tracking": None},
            1003: {"status": "delivered", "tracking": "1Z999BB9876543210"}
        }
        
        order_info = mock_orders.get(order_id)
        if not order_info:
            return f"No order found with ID {order_id}"
        
        return f"Order {order_id} status: {order_info}"
    
    async def _real_get_order_status(self, order_id: int) -> str:
        """Real Shopify API order status lookup."""
        if not settings.shopify_base_url or not settings.shopify_access_token:
            return "Shopify API not configured."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.shopify_base_url}/orders/{order_id}.json",
                    headers=settings.shopify_headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    order = data.get("order", {})
                    
                    # Mask PII
                    order["email"] = mask_pii(order.get("email", ""))
                    order["phone"] = mask_pii(order.get("phone", ""))
                    
                    return f"Order {order_id} status: {order}"
                else:
                    return f"Order {order_id} not found or access denied"
                    
            except httpx.RequestError as e:
                return f"Network error: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"


class ShopifyTrackingTool(BaseTool):
    """Tool for getting tracking information."""
    
    name = "get_tracking"
    description = "Get tracking information for an order by order ID."
    args_schema = GetTrackingInput
    
    async def _arun(self, order_id: int) -> str:
        """Get tracking info asynchronously."""
        try:
            if settings.mock_mode:
                return await self._mock_get_tracking(order_id)
            
            # Real Shopify API call
            return await self._real_get_tracking(order_id)
            
        except Exception as e:
            return f"Error getting tracking info: {str(e)}"
    
    def _run(self, order_id: int) -> str:
        """Get tracking info synchronously."""
        import asyncio
        return asyncio.run(self._arun(order_id))
    
    async def _mock_get_tracking(self, order_id: int) -> str:
        """Mock tracking lookup."""
        mock_tracking = {
            1001: {
                "tracking_number": "1Z999AA1234567890",
                "tracking_url": "https://www.ups.com/track?trackingNumber=1Z999AA1234567890",
                "carrier": "UPS",
                "status": "In Transit",
                "estimated_delivery": "2024-01-15T18:00:00Z"
            },
            1002: {
                "tracking_number": None,
                "tracking_url": None,
                "carrier": None,
                "status": "Not yet shipped",
                "estimated_delivery": None
            },
            1003: {
                "tracking_number": "1Z999BB9876543210",
                "tracking_url": "https://www.ups.com/track?trackingNumber=1Z999BB9876543210",
                "carrier": "UPS",
                "status": "Delivered",
                "estimated_delivery": "2024-01-14T11:30:00Z"
            }
        }
        
        tracking_info = mock_tracking.get(order_id)
        if not tracking_info:
            return f"No tracking info found for order {order_id}"
        
        return f"Tracking info for order {order_id}: {tracking_info}"
    
    async def _real_get_tracking(self, order_id: int) -> str:
        """Real Shopify API tracking lookup."""
        if not settings.shopify_base_url or not settings.shopify_access_token:
            return "Shopify API not configured."
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.shopify_base_url}/orders/{order_id}/fulfillments.json",
                    headers=settings.shopify_headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    fulfillments = data.get("fulfillments", [])
                    
                    if fulfillments:
                        fulfillment = fulfillments[0]  # Get latest fulfillment
                        tracking_info = {
                            "tracking_number": fulfillment.get("tracking_number"),
                            "tracking_url": fulfillment.get("tracking_url"),
                            "carrier": fulfillment.get("carrier"),
                            "status": fulfillment.get("status"),
                            "created_at": fulfillment.get("created_at")
                        }
                        return f"Tracking info for order {order_id}: {tracking_info}"
                    else:
                        return f"No fulfillments found for order {order_id}"
                else:
                    return f"Order {order_id} not found or access denied"
                    
            except httpx.RequestError as e:
                return f"Network error: {str(e)}"
            except Exception as e:
                return f"Error: {str(e)}"
