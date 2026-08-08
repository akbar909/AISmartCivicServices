# Database models package
from app.models.user import User
from app.models.complaint import Complaint
from app.models.department import Department
from app.models.notification import Notification

__all__ = ["User", "Complaint", "Department", "Notification"]
