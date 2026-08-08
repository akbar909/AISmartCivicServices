"""
Admin analytics router.

Uses MongoDB aggregation pipelines ($group, $match, $bucket) for efficient
server-side computation — does NOT pull all documents into Python.
"""

import logging
from datetime import datetime, timedelta

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from app.models.complaint import Complaint
from app.models.user import User
from app.services.auth_service import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats")
async def get_stats(current_user: User = Depends(require_admin)):
    """Return aggregated statistics for the admin dashboard.
    
    All computations use MongoDB aggregation pipelines for efficiency.
    Returns:
    - counts by category, priority, status, department
    - average resolution time (for resolved complaints)
    - complaints-over-time trend (last 30 days, grouped by day)
    - total complaints count
    """
    collection = Complaint.get_pymongo_collection()

    # Total counts
    total_complaints = await Complaint.find().count()
    open_count = await Complaint.find({"status": "Open"}).count()
    
    # Resolved this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    resolved_this_week = await Complaint.find({
        "status": "Resolved",
        "updated_at": {"$gte": week_ago},
    }).count()

    # Counts by category (aggregation pipeline)
    category_counts = await collection.aggregate([
        {"$group": {"_id": "$ai_output.category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(length=None)

    # Counts by priority
    priority_counts = await collection.aggregate([
        {"$group": {"_id": "$ai_output.priority", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(length=None)

    # Counts by status
    status_counts = await collection.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(length=None)

    # Counts by department
    department_counts = await collection.aggregate([
        {"$match": {"assigned_department": {"$ne": None}}},
        {"$group": {"_id": "$assigned_department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(length=None)

    # Average resolution time (for resolved complaints)
    avg_resolution = await collection.aggregate([
        {"$match": {"status": "Resolved"}},
        {
            "$project": {
                "resolution_hours": {
                    "$divide": [
                        {"$subtract": ["$updated_at", "$created_at"]},
                        3600000,  # milliseconds to hours
                    ]
                }
            }
        },
        {"$group": {"_id": None, "avg_hours": {"$avg": "$resolution_hours"}}},
    ]).to_list(length=1)

    avg_resolution_hours = (
        round(avg_resolution[0]["avg_hours"], 1) if avg_resolution else 0
    )

    # Complaints over time — last 30 days, grouped by day
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    complaints_over_time = await collection.aggregate([
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]).to_list(length=None)

    # Resolution time by department
    resolution_by_dept = await collection.aggregate([
        {
            "$match": {
                "status": "Resolved",
                "assigned_department": {"$ne": None},
            }
        },
        {
            "$project": {
                "assigned_department": 1,
                "resolution_hours": {
                    "$divide": [
                        {"$subtract": ["$updated_at", "$created_at"]},
                        3600000,
                    ]
                },
            }
        },
        {
            "$group": {
                "_id": "$assigned_department",
                "avg_hours": {"$avg": "$resolution_hours"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"avg_hours": 1}},
    ]).to_list(length=None)

    return {
        "total_complaints": total_complaints,
        "open_count": open_count,
        "resolved_this_week": resolved_this_week,
        "avg_resolution_hours": avg_resolution_hours,
        "category_counts": [
            {"category": c["_id"] or "Other", "count": c["count"]} for c in category_counts
        ],
        "priority_counts": [
            {"priority": p["_id"] or "Medium", "count": p["count"]} for p in priority_counts
        ],
        "status_counts": [
            {"status": s["_id"] or "Open", "count": s["count"]} for s in status_counts
        ],
        "department_counts": [
            {"department": d["_id"] or "Unassigned", "count": d["count"]} for d in department_counts
        ],
        "complaints_over_time": [
            {"date": t["_id"] or "", "count": t["count"]} for t in complaints_over_time
        ],
        "resolution_by_department": [
            {
                "department": r["_id"] or "Unassigned",
                "avg_hours": round(r["avg_hours"], 1) if r.get("avg_hours") is not None else 0,
                "resolved_count": r["count"],
            }
            for r in resolution_by_dept
        ],
    }
