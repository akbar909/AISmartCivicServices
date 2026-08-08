"""
Pydantic request/response schemas for complaint endpoints.
Handles ObjectId serialization so the frontend receives clean JSON string IDs.
"""

from datetime import datetime
from typing import Literal, Optional, List

from pydantic import BaseModel, Field


class LocationInput(BaseModel):
    """Location data from the complaint form."""

    text: str = Field(..., min_length=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ComplaintCreate(BaseModel):
    """Request body to create a new complaint.
    
    Only description and location are required from the citizen.
    AI classification and summarization are computed server-side.
    """

    description: str = Field(..., min_length=10, max_length=5000)
    location: LocationInput
    citizen_confirmed_category: Optional[str] = None
    image_url: Optional[str] = None


class ComplaintUpdate(BaseModel):
    """Request body for admin updates to a complaint."""

    status: Optional[Literal["Open", "Assigned", "In Progress", "Resolved"]] = None
    assigned_department: Optional[str] = None
    citizen_confirmed_category: Optional[str] = None


class AIOutputResponse(BaseModel):
    """AI classification results in the response."""

    category: str
    category_confidence: float
    priority: str
    priority_confidence: float
    summary: Optional[str] = None


class LocationResponse(BaseModel):
    """Location data in the response."""

    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ImageAnalysisResponse(BaseModel):
    """Local AI image analysis output."""

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


class ComplaintResponse(BaseModel):
    """Full complaint data returned to the client."""

    id: str
    citizen_id: str
    description: str
    ai_output: AIOutputResponse
    citizen_confirmed_category: Optional[str] = None
    location: LocationResponse
    image_url: Optional[str] = None
    image_analysis: Optional[ImageAnalysisResponse] = None
    status: str
    assigned_department: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplaintListResponse(BaseModel):
    """Paginated list of complaints."""

    complaints: List[ComplaintResponse]
    total: int
    page: int
    page_size: int
