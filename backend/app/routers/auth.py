"""
Authentication router: signup, login, and current user endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """Register a new citizen or admin user."""
    # Check if email already exists
    existing = await User.find_one({"email": request.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
    )
    await user.insert()
    logger.info(f"New {user.role} user registered: {user.email}")

    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate and receive a JWT token."""
    user = await User.find_one({"email": request.email})
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
    )
