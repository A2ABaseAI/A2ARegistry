"""FastAPI server for Shopify Status Agent."""

import json
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .agent import agent
from .config import settings
from .schemas import (
    ChatMessage,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
)

# Create FastAPI app
app = FastAPI(
    title="Shopify Status Agent",
    description="LangChain + FastAPI + Shopify Order Tracker Agent",
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        ok=True,
        timestamp=datetime.now(),
        mock_mode=settings.mock_mode,
        shopify_configured=bool(settings.shopify_base_url and settings.shopify_access_token),
    )


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Serve the chat page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Chat endpoint for non-streaming responses."""
    try:
        result = await agent.chat(message.message, message.session_id)
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            order_info=result["order_info"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Internal server error",
                detail=str(e),
                session_id=message.session_id,
            ).dict(),
        )


@app.post("/api/chat/stream")
async def chat_stream_endpoint(message: ChatMessage):
    """Streaming chat endpoint with Server-Sent Events."""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream."""
        try:
            async for chunk in agent.stream_chat(message.message, message.session_id):
                # Format as SSE
                data = json.dumps(chunk)
                yield f"data: {data}\n\n"
            
            # Send end marker
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_chunk = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "session_id": message.session_id,
            }
            data = json.dumps(error_chunk)
            yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation memory for a session."""
    success = agent.clear_memory(session_id)
    
    if success:
        return {"message": f"Session {session_id} cleared successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/sessions/count")
async def get_session_count():
    """Get number of active sessions."""
    return {"count": agent.get_session_count()}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return ErrorResponse(
        error=exc.detail,
        detail=f"HTTP {exc.status_code}",
    ).dict()


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc),
    ).dict()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
