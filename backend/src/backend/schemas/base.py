"""
Base schemas for the Agentic backend.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.
    """
    class Config:
        from_attributes = True
        populate_by_name = True