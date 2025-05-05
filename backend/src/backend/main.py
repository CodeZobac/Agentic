"""
Main application module for the Agentic backend.
"""
import os
from typing import Any

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.api import api_router
from backend.core.config import settings
from backend.db.database import Base, engine, get_db, SessionLocal
from backend.db.models import User
from backend.core.security import get_password_hash
from backend.schemas.user import UserCreate

# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # For development, allow all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router)


@app.on_event("startup")
async def create_superuser() -> None:
    """
    Create a superuser on application startup if one doesn't exist.
    """
    db = SessionLocal()
    try:
        # Check if any user exists
        user = db.query(User).first()
        if not user:
            # Create a superuser with default credentials
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            
            db_obj = User(
                email=admin_email,
                username=admin_username,
                hashed_password=get_password_hash(admin_password),
                is_active=True,
                is_superuser=True,
            )
            db.add(db_obj)
            db.commit()
            print(f"Created superuser: {admin_username}")
    finally:
        db.close()


@app.get("/")
def root() -> Any:
    """
    Root endpoint to confirm API is running.
    """
    return {
        "status": "ok",
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
    }


def start() -> None:
    """
    Start the application with uvicorn.
    """
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    start()