#!/usr/bin/env python3
"""
Simple FastAPI server for Shopify Status Agent (Mock Version).
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Shopify Status Agent",
    description="Mock Shopify Order Tracker Agent",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    session_id: str = None

class HealthResponse(BaseModel):
    ok: bool
    timestamp: datetime
    service: str = "Shopify Status Agent"
    version: str = "1.0.0"

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        ok=True,
        timestamp=datetime.now(),
        service="Shopify Status Agent",
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Shopify Status Agent",
        "version": "1.0.0",
        "description": "Mock Shopify order tracking and status checking",
        "endpoints": {
            "health": "/healthz",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.post("/chat")
async def chat(message: ChatMessage):
    """Chat endpoint for Shopify order queries."""
    try:
        logger.info(f"📨 Shopify Agent received message: {message.message}")
        
        # Mock Shopify order response
        if "order" in message.message.lower() or "1001" in message.message:
            response = {
                "status": "success",
                "message": "Order information retrieved",
                "order_number": "1001",
                "status": "Fulfilled",
                "tracking_number": "1Z999AA10123456784",
                "customer_email": "customer@example.com",
                "total": "$99.99",
                "items": [
                    {"name": "Product A", "quantity": 2, "price": "$49.99"}
                ],
                "shipping_address": {
                    "name": "John Doe",
                    "address": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001"
                },
                "timeline": [
                    {"date": "2024-10-24", "status": "Order placed"},
                    {"date": "2024-10-24", "status": "Payment confirmed"},
                    {"date": "2024-10-25", "status": "Order fulfilled"},
                    {"date": "2024-10-25", "status": "Shipped"}
                ]
            }
        else:
            response = {
                "status": "success",
                "message": f"Shopify Agent processed: {message.message}",
                "response": "I can help you track Shopify orders. Please provide an order number or ask about order status."
            }
        
        logger.info(f"📤 Shopify Agent sending response: {response}")
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent": "Shopify Status Agent"
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities."""
    return {
        "name": "Shopify Status Agent",
        "description": "Mock Shopify order tracking and status checking",
        "capabilities": [
            "Track Shopify orders by order number",
            "Provide order status updates",
            "Customer order history",
            "Natural language processing for order queries"
        ],
        "supported_formats": ["json", "text"],
        "protocols": ["http", "websocket"]
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8005"))
    logger.info(f"🚀 Starting Shopify Status Agent on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
