"""
User document model for MongoDB via Beanie ODM.
"""

from datetime import datetime
from typing import Literal

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    """Represents a platform user (citizen or admin)."""

    name: str = Field(..., min_length=1, max_length=100)
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    role: Literal["citizen", "admin"] = "citizen"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "role": "citizen",
            }
        }
