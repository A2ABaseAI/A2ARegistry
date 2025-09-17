from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

# Serve static files from the frontend build directory
frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "build"


@router.get("/")
async def serve_index():
    """Serve the React app index.html for all non-API routes."""
    index_path = frontend_build_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "message": (
                "Frontend not built. Run 'npm run build' in the frontend directory."
            )
        }


@router.get("/static/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files from the frontend build."""
    static_path = frontend_build_path / "static" / file_path
    if static_path.exists():
        return FileResponse(static_path)
    else:
        return {"error": "File not found"}


@router.get("/{path:path}")
async def serve_spa(path: str):
    """Serve the React app for all other routes (SPA routing)."""
    # Check if it's an API route - exclude all API endpoints
    api_prefixes = [
        "agents/",
        "clients/",
        "peering/",
        "oauth/",
        "health",
        "stats/",
        ".well-known/",
        "api/",
        "docs",
        "redoc",
        "openapi.json",
    ]

    if any(path.startswith(prefix) for prefix in api_prefixes):
        return {"error": "API route not found"}

    # Serve index.html for all other routes (SPA routing)
    index_path = frontend_build_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "message": (
                "Frontend not built. Run 'npm run build' in the frontend directory."
            )
        }
