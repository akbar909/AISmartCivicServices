"""
Chatbot router: AI-powered category suggestion and conversational guidance.

- /suggest: Uses the trained scikit-learn model for category suggestion,
  with optional Gemini-powered clarifying questions when confidence is low.
- /message: Uses Gemini for free-form conversational guidance, scoped
  to civic complaint topics via a system prompt.
"""

import logging

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.chatbot import (
    SuggestRequest,
    SuggestResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.services.auth_service import get_current_user
from app.services.ai_service import classify_complaint
from app.services.gemini_service import generate_clarifying_question, chatbot_reply

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_category(
    request: SuggestRequest,
    current_user: User = Depends(get_current_user),
):
    """Suggest a complaint category based on partial/full text.
    
    Uses the trained scikit-learn category model for the suggestion.
    Uses Gemini ONLY to generate a clarifying question when:
    - Classification confidence is below 0.6, OR
    - Key details (location, severity) seem missing from the text
    """
    # ML-based classification (scikit-learn — NOT Gemini)
    result = classify_complaint(request.text)

    # Generate clarifying question via Gemini when confidence is low
    clarifying_question = None
    if result["category_confidence"] < 0.6 or len(request.text.split()) < 8:
        clarifying_question = await generate_clarifying_question(
            request.text,
            result["category"],
            result["category_confidence"],
        )

    return SuggestResponse(
        suggested_category=result["category"],
        confidence=result["category_confidence"],
        clarifying_question=clarifying_question,
    )


@router.post("/message", response_model=ChatMessageResponse)
async def chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """General conversational endpoint for the guidance chatbot.
    
    Uses Gemini API with a system prompt that keeps responses focused on
    civic complaint categories and guidance. Does NOT answer unrelated questions.
    """
    # Convert history to the format expected by gemini_service
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in request.history
    ]

    reply = await chatbot_reply(
        message=request.message,
        history=history,
    )

    return ChatMessageResponse(reply=reply)
