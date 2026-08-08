"""
Pydantic request/response schemas for the chatbot endpoints.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SuggestRequest(BaseModel):
    """Request for AI category suggestion based on complaint text."""

    text: str = Field(..., min_length=3, max_length=5000)


class SuggestResponse(BaseModel):
    """Category suggestion response from the ML model + optional Gemini clarification."""

    suggested_category: str
    confidence: float
    clarifying_question: Optional[str] = None


class ChatMessage(BaseModel):
    """A single message in the chatbot conversation history."""

    role: str  # "user" or "assistant"
    content: str


class ChatMessageRequest(BaseModel):
    """Request for the conversational chatbot endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatMessage] = Field(default_factory=list)


class ChatMessageResponse(BaseModel):
    """Chatbot reply."""

    reply: str
