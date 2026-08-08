"""
Complaint document model for MongoDB via Beanie ODM.

Contains embedded sub-documents for AI classification output and location.
"""

from datetime import datetime
from typing import Literal, Optional, List

from beanie import Document
from pydantic import BaseModel, Field
from beanie import PydanticObjectId


class AIOutput(BaseModel):
    """AI classification and summarization results.
    
    - category & priority: from pre-trained scikit-learn models (NOT Gemini)
    - summary: from Gemini API (nullable — complaint saves even if Gemini fails)
    """

    category: str
    category_confidence: float = Field(..., ge=0, le=1)
    priority: str
    priority_confidence: float = Field(..., ge=0, le=1)
    summary: Optional[str] = None


class Location(BaseModel):
    """Complaint location — text is required, coordinates are optional."""

    text: str = Field(..., min_length=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ImageAnalysis(BaseModel):
    """Local AI image analysis sub-document."""

    status: str = "success"
    is_relevant: bool = True
    rejection_reason: Optional[str] = None
    clarity_score: float = 0.0
    clarity_label: str = "Unknown"
    lighting: str = "Unknown"
    detected_tags: List[str] = Field(default_factory=list)
    suggested_category: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class Complaint(Document):
    """
    A civic complaint submitted by a citizen.
    
    The AI pipeline runs on creation:
    1. Text → TF-IDF → category_model (sklearn) → category + confidence
    2. Text → TF-IDF → priority_model (sklearn) → priority + confidence
    3. Text + category + priority → Gemini API → summary
    4. Image → Local Computer Vision Analyzer → clarity, lighting, visual tags
    """

    citizen_id: PydanticObjectId
    description: str = Field(..., min_length=10, max_length=5000)
    ai_output: AIOutput
    citizen_confirmed_category: Optional[str] = None
    location: Location
    image_url: Optional[str] = None
    image_analysis: Optional[ImageAnalysis] = None
    status: Literal["Open", "Assigned", "In Progress", "Resolved"] = "Open"
    assigned_department: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "complaints"
        indexes = [
            "citizen_id",
            "status",
            "ai_output.category",
            "ai_output.priority",
            "created_at",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Large pothole on Main Street causing tire damage",
                "location": {"text": "123 Main St, Downtown"},
            }
        }
