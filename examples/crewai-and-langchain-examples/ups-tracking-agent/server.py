#!/usr/bin/env python3
"""
FastAPI server for UPS Tracking Agent.
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

# Add the UPS agent to the path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from ups_agent.agent import UPSStatusAgent
from ups_agent.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="UPS Tracking Agent",
    description="CrewAI + FastAPI + UPS Shipment Tracker Agent",
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

# Initialize UPS agent
ups_agent = None

class ChatMessage(BaseModel):
    message: str
    session_id: str = None

class HealthResponse(BaseModel):
    ok: bool
    timestamp: datetime
    service: str = "UPS Tracking Agent"
    version: str = "1.0.0"

@app.on_event("startup")
async def startup_event():
    """Initialize the UPS agent on startup."""
    global ups_agent
    try:
        logger.info("🚀 Starting UPS Tracking Agent...")
        ups_agent = UPSStatusAgent()
        logger.info("✅ UPS Tracking Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize UPS Tracking Agent: {e}")
        raise

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
        "description": "CrewAI agent for UPS shipment tracking and status checking",
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
        if not ups_agent:
            raise HTTPException(status_code=503, detail="UPS agent not initialized")
        
        logger.info(f"📨 Received message: {message.message}")
        
        # Process the message with the UPS agent
        response = await ups_agent.process_message(message.message)
        
        logger.info(f"📤 Sending response: {response}")
        
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
        "description": "AI agent for tracking UPS shipments and providing status updates using CrewAI",
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
