"""
API router initialization.
"""
from fastapi import APIRouter

from backend.api.v1.api import api_router as api_v1_router
from backend.core.config import settings

# Main API router
api_router = APIRouter()

# Include API v1 routes
api_router.include_router(api_v1_router, prefix=settings.API_V1_STR)