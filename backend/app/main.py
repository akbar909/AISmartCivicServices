"""
AI Smart Civic Services — FastAPI Application Entrypoint

A civic complaint management platform where citizens report local
infrastructure problems and an AI pipeline classifies, prioritizes,
and summarizes them for a service-team dashboard.

AI Technology:
- Classification: Pre-trained scikit-learn models (TF-IDF + LogReg/SVC/RF)
- Summarization: Google Gemini API (gemini-2.5-flash)
- Chatbot: Google Gemini API with civic-scoped system prompt
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db, close_db
from app.services.ai_service import load_models, ensure_nltk_resources
from app.services.gemini_service import configure_gemini
from app.services.cloudinary_service import configure_cloudinary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──
    logger.info("Starting AI Smart Civic Services...")

    # 1. Initialize MongoDB + Beanie
    await init_db()

    # 2. Ensure NLTK resources are available
    ensure_nltk_resources()

    # 3. Load ML models (scikit-learn — classification only)
    load_models()

    # 4. Configure Gemini (summarization + chatbot only)
    configure_gemini()

    # 5. Configure Cloudinary
    configure_cloudinary()

    # 6. Seed default departments and users if empty
    await _seed_departments()
    await _seed_default_users()

    logger.info("Application startup complete")
    yield

    # ── Shutdown ──
    await close_db()
    logger.info("Application shutdown complete")


async def _seed_departments():
    """Seed default departments on first startup if the collection is empty."""
    from app.models.department import Department, DEFAULT_DEPARTMENTS

    count = await Department.find().count()
    if count == 0:
        logger.info("Seeding default departments...")
        for dept_data in DEFAULT_DEPARTMENTS:
            dept = Department(**dept_data)
            await dept.insert()
        logger.info(f"Seeded {len(DEFAULT_DEPARTMENTS)} departments")


async def _seed_default_users():
    """Seed default admin and citizen accounts on startup if missing."""
    from app.models.user import User
    from app.services.auth_service import hash_password

    users = [
        {"email": "admin@gmail.com", "password": "test12", "name": "System Admin", "role": "admin"},
        {"email": "test@gmail.com", "password": "test12", "name": "Citizen User", "role": "citizen"},
    ]
    for u in users:
        existing = await User.find_one(User.email == u["email"])
        if not existing:
            new_user = User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
            )
            await new_user.insert()
            logger.info(f"Auto-seeded user: {u['email']} ({u['role']})")


# Create FastAPI app
app = FastAPI(
    title="AI Smart Civic Services",
    description="Civic complaint management with AI-powered classification and summarization",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://aismartcivicservices.vercel.app"
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler returning consistent JSON error shape."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
        },
    )


# ── Register Routers ──
from app.routers import auth, complaints, chatbot, admin, notifications

app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(chatbot.router)
app.include_router(admin.router)
app.include_router(notifications.router)


# ── Health Check ──
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "AI Smart Civic Services"}
