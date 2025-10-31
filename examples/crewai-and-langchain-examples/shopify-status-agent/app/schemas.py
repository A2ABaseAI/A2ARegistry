"""Pydantic schemas for Shopify Status Agent."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message schema."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation memory")


class ChatResponse(BaseModel):
    """Chat response schema."""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    order_info: Optional[Dict[str, Any]] = Field(default=None, description="Order information if found")


class OrderInfo(BaseModel):
    """Order information schema."""
    order_id: int = Field(..., description="Order ID")
    order_number: str = Field(..., description="Order number")
    email: str = Field(..., description="Customer email (masked)")
    phone: Optional[str] = Field(default=None, description="Customer phone (masked)")
    financial_status: str = Field(..., description="Financial status")
    fulfillment_status: Optional[str] = Field(default=None, description="Fulfillment status")
    created_at: datetime = Field(..., description="Order creation date")
    updated_at: datetime = Field(..., description="Last update date")
    total_price: str = Field(..., description="Total price")
    currency: str = Field(..., description="Currency")
    line_items: List[Dict[str, Any]] = Field(default=[], description="Order line items")
    fulfillments: List[Dict[str, Any]] = Field(default=[], description="Fulfillment information")
    tracking_info: Optional[Dict[str, Any]] = Field(default=None, description="Tracking information")


class TrackingInfo(BaseModel):
    """Tracking information schema."""
    tracking_number: Optional[str] = Field(default=None, description="Tracking number")
    tracking_url: Optional[str] = Field(default=None, description="Tracking URL")
    carrier: Optional[str] = Field(default=None, description="Shipping carrier")
    status: Optional[str] = Field(default=None, description="Shipping status")
    estimated_delivery: Optional[datetime] = Field(default=None, description="Estimated delivery date")


class HealthResponse(BaseModel):
    """Health check response schema."""
    ok: bool = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    mock_mode: bool = Field(..., description="Whether running in mock mode")
    shopify_configured: bool = Field(..., description="Whether Shopify is configured")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    session_id: Optional[str] = Field(default=None, description="Session ID if available")
