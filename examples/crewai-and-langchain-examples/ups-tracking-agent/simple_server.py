#!/usr/bin/env python3
"""
Simple FastAPI server for UPS Tracking Agent (Mock Version).
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
    title="UPS Tracking Agent",
    description="Mock UPS Shipment Tracker Agent",
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
    service: str = "UPS Tracking Agent"
    version: str = "1.0.0"

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        ok=True,
        timestamp=datetime.now(),
        service="UPS Tracking Agent",
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "UPS Tracking Agent",
        "version": "1.0.0",
        "description": "Mock UPS shipment tracking and status checking",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.post("/chat")
async def chat(message: ChatMessage):
    """Chat endpoint for UPS tracking queries."""
    try:
        logger.info(f"📨 UPS Agent received message: {message.message}")
        
        # Mock UPS tracking response
        if "track" in message.message.lower():
            response = {
                "status": "success",
                "message": "Package tracking information retrieved",
                "tracking_number": "1Z999AA10123456784",
                "status": "In Transit",
                "location": "Memphis, TN",
                "estimated_delivery": "2024-10-27",
                "details": [
                    {"date": "2024-10-25", "time": "08:30", "status": "Package picked up", "location": "Origin"},
                    {"date": "2024-10-25", "time": "14:20", "status": "In transit", "location": "Memphis, TN"},
                    {"date": "2024-10-26", "time": "06:45", "status": "Out for delivery", "location": "Destination City"}
                ]
            }
        else:
            response = {
                "status": "success",
                "message": f"UPS Agent processed: {message.message}",
                "response": "I can help you track UPS shipments. Please provide a tracking number or ask about shipment status."
            }
        
        logger.info(f"📤 UPS Agent sending response: {response}")
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent": "UPS Tracking Agent"
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities."""
    return {
        "name": "UPS Tracking Agent",
        "description": "Mock UPS shipment tracking and status checking",
        "capabilities": [
            "Track UPS shipments by tracking number",
            "Provide shipment status updates",
            "Handle multiple tracking numbers",
            "Natural language processing for tracking queries"
        ],
        "supported_formats": ["json", "text"],
        "protocols": ["http", "websocket"]
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8006"))
    logger.info(f"🚀 Starting UPS Tracking Agent on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
