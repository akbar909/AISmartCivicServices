"""
Notifications router — REST polling-based web notifications.

Endpoints:
  GET    /api/notifications             → list current user's notifications
  GET    /api/notifications/unread-count → fast badge count for polling
  PATCH  /api/notifications/{id}/read  → mark one as read
  PATCH  /api/notifications/read-all   → mark all as read
"""

import logging
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from app.models.notification import Notification
from app.models.user import User
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


# ── Response Schemas ──────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    complaint_id: Optional[str]
    created_at: datetime


class UnreadCountResponse(BaseModel):
    count: int


# ── Helper ────────────────────────────────────────────────────────────────────

async def create_notification(
    user_id: PydanticObjectId,
    title: str,
    message: str,
    notif_type: str = "info",
    complaint_id: Optional[str] = None,
) -> None:
    """Create and persist a web notification for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        complaint_id=complaint_id,
    )
    await notif.insert()


def _to_response(n: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=str(n.id),
        title=n.title,
        message=n.message,
        type=n.type,
        is_read=n.is_read,
        complaint_id=n.complaint_id,
        created_at=n.created_at,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
):
    """Fetch the last 20 notifications for the current user, newest first."""
    notifications = (
        await Notification.find(Notification.user_id == current_user.id)
        .sort("-created_at")
        .limit(20)
        .to_list()
    )
    return [_to_response(n) for n in notifications]


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
):
    """Return just the unread notification count — polled every 30s by frontend."""
    count = await Notification.find(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()
    return UnreadCountResponse(count=count)


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read for the current user."""
    unread = await Notification.find(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).to_list()
    for n in unread:
        await n.set({"is_read": True})
    logger.info(f"Marked {len(unread)} notifications as read for user {current_user.id}")


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_one_read(
    notification_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    notif = await Notification.get(notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    await notif.set({"is_read": True})
    notif = await Notification.get(notification_id)
    return _to_response(notif)
