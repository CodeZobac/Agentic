"""
API router for v1 endpoints.
"""
from fastapi import APIRouter

from backend.api.v1.endpoints import auth, users, agents, tasks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])