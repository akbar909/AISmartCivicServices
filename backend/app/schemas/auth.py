"""
Pydantic request/response schemas for authentication endpoints.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request body for user registration."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["citizen", "admin"] = "citizen"


class LoginRequest(BaseModel):
    """Request body for login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User data returned to the client.
    
    Note: ObjectId is serialized to string via the `id` field alias.
    """

    id: str
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
