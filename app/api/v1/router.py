"""Main API v1 router."""

from fastapi import APIRouter

from .endpoints.generate import router as generate_router
from .endpoints.personas import router as personas_router
from .endpoints.health import router as health_router

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include all sub-routers
router.include_router(generate_router)
router.include_router(personas_router)
router.include_router(health_router)

# Add route tags info for OpenAPI documentation
tags_metadata = [
    {
        "name": "content_generation",
        "description": "Content generation using multi-agent AI workflow",
        "externalDocs": {
            "description": "Learn more about the AI agents",
            "url": "https://github.com/yourusername/TargetScriptAI",
        },
    },
    {
        "name": "persona_management",
        "description": "Manage target personas for content generation",
    },
    {
        "name": "health",
        "description": "System health checks and status monitoring",
    },
]
