"""
Notification document model for MongoDB via Beanie ODM.
Stores in-app web notifications for citizens and admins.
"""

from datetime import datetime
from typing import Literal, Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class Notification(Document):
    """A web notification stored for a specific user."""

    user_id: PydanticObjectId
    title: str
    message: str
    type: Literal["success", "info", "warning", "error"] = "info"
    is_read: bool = False
    complaint_id: Optional[str] = None   # for quick linking
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
        ]
