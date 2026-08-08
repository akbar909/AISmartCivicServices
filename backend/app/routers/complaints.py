"""
Complaints router: CRUD operations with AI classification pipeline.

The complaint creation pipeline:
1. Text → TF-IDF → category_model (scikit-learn) → category + confidence
2. Text → TF-IDF → priority_model (scikit-learn) → priority + confidence
3. Text + category + priority → Gemini API → actionable summary
4. Store complaint with all AI outputs

If Gemini fails, the complaint still saves with summary=None.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status

from app.models.complaint import Complaint, AIOutput, Location, ImageAnalysis
from app.models.user import User
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintResponse,
    ComplaintListResponse,
    AIOutputResponse,
    LocationResponse,
    ImageAnalysisResponse,
)
from app.services.auth_service import get_current_user, require_admin
from app.services.ai_service import classify_complaint
from app.services.gemini_service import generate_summary
from app.services.cloudinary_service import upload_image_file
from app.services.image_analysis_service import analyze_uploaded_image
from app.services.email_service import (
    send_complaint_submitted_email,
    send_new_complaint_admin_email,
    send_status_update_email,
    send_department_assigned_email,
)
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a complaint photo to Cloudinary (or local storage fallback)."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file",
        )

    # 1. Save to temp file & run AI relevance analysis BEFORE storing permanently
    import os, tempfile
    ext = os.path.splitext(file.filename or "upload.jpg")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        res = analyze_uploaded_image(tmp_path)
        if res.get("status") == "success" and not res.get("is_relevant", True):
            rejection_msg = res.get("rejection_reason") or "Uploaded image is not relevant to civic infrastructure issues."
            logger.warning(f"Upload rejected: {rejection_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{rejection_msg} Please upload a clear photo of the reported problem or submit without a photo.",
            )
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    # 2. Image is relevant — store permanently via Cloudinary or local disk
    image_url = await upload_image_file(content, file.filename or "upload.jpg")
    return {"image_url": image_url}


def complaint_to_response(complaint: Complaint) -> ComplaintResponse:
    """Convert a Complaint document to a response schema with string IDs."""
    return ComplaintResponse(
        id=str(complaint.id),
        citizen_id=str(complaint.citizen_id),
        description=complaint.description,
        ai_output=AIOutputResponse(
            category=complaint.ai_output.category,
            category_confidence=complaint.ai_output.category_confidence,
            priority=complaint.ai_output.priority,
            priority_confidence=complaint.ai_output.priority_confidence,
            summary=complaint.ai_output.summary,
        ),
        citizen_confirmed_category=complaint.citizen_confirmed_category,
        location=LocationResponse(
            text=complaint.location.text,
            latitude=complaint.location.latitude,
            longitude=complaint.location.longitude,
        ),
        image_url=complaint.image_url,
        image_analysis=ImageAnalysisResponse(
            status=complaint.image_analysis.status,
            is_relevant=complaint.image_analysis.is_relevant,
            rejection_reason=complaint.image_analysis.rejection_reason,
            clarity_score=complaint.image_analysis.clarity_score,
            clarity_label=complaint.image_analysis.clarity_label,
            lighting=complaint.image_analysis.lighting,
            detected_tags=complaint.image_analysis.detected_tags,
            suggested_category=complaint.image_analysis.suggested_category,
            image_width=complaint.image_analysis.image_width,
            image_height=complaint.image_analysis.image_height,
        ) if complaint.image_analysis else None,
        status=complaint.status,
        assigned_department=complaint.assigned_department,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new complaint with full AI classification pipeline.
    
    Pipeline:
    1. scikit-learn models classify category and priority (ai_service.py)
    2. Gemini generates an actionable summary (gemini_service.py)
    3. Local AI Image Analyzer processes photo for clarity, lighting, visual tags & relevance
    4. Complaint is stored with all AI outputs
    """
    # Step 1: ML classification (scikit-learn — NOT Gemini)
    ai_result = classify_complaint(data.description)
    logger.info(f"AI classified: category={ai_result['category']}, priority={ai_result['priority']}")

    # Step 2: Gemini summary (non-critical — complaint saves even if this fails)
    summary = await generate_summary(
        data.description, ai_result["category"], ai_result["priority"]
    )

    # Step 3: Local Image AI Analysis (runs 100% locally on CPU)
    image_analysis_obj = None
    if data.image_url:
        import os, tempfile, urllib.request
        settings = get_settings()
        target_path = None
        is_temp = False

        if data.image_url.startswith("http://") or data.image_url.startswith("https://"):
            try:
                ext = os.path.splitext(data.image_url.split("?")[0])[1] or ".jpg"
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    req = urllib.request.Request(data.image_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req) as resp:
                        tmp.write(resp.read())
                    target_path = tmp.name
                    is_temp = True
            except Exception as e:
                logger.warning(f"Could not fetch Cloudinary image for analysis: {e}")
        else:
            local_filename = os.path.basename(data.image_url)
            local_path = os.path.join(settings.UPLOAD_DIR, local_filename)
            if os.path.exists(local_path):
                target_path = local_path

        if target_path and os.path.exists(target_path):
            try:
                res = analyze_uploaded_image(target_path, expected_category=ai_result["category"])
                if res.get("status") == "success":
                    if not res.get("is_relevant", True):
                        rejection_msg = res.get("rejection_reason") or f"Uploaded photo is not relevant to reported '{ai_result['category']}' issue."
                        logger.warning(f"Rejecting complaint creation due to image mismatch: {rejection_msg}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{rejection_msg} Please upload a clear photo of the reported problem or submit without a photo.",
                        )

                    image_analysis_obj = ImageAnalysis(
                        status=res.get("status", "success"),
                        is_relevant=res.get("is_relevant", True),
                        rejection_reason=res.get("rejection_reason"),
                        clarity_score=res.get("clarity_score", 0.0),
                        clarity_label=res.get("clarity_label", "Unknown"),
                        lighting=res.get("lighting", "Unknown"),
                        detected_tags=res.get("detected_tags", []),
                        suggested_category=res.get("suggested_category"),
                        image_width=res.get("image_width"),
                        image_height=res.get("image_height"),
                    )
            finally:
                if is_temp and target_path and os.path.exists(target_path):
                    try:
                        os.remove(target_path)
                    except Exception:
                        pass

    # Step 4: Create and store the complaint
    complaint = Complaint(
        citizen_id=current_user.id,
        description=data.description,
        ai_output=AIOutput(
            category=ai_result["category"],
            category_confidence=ai_result["category_confidence"],
            priority=ai_result["priority"],
            priority_confidence=ai_result["priority_confidence"],
            summary=summary,
        ),
        citizen_confirmed_category=data.citizen_confirmed_category,
        location=Location(
            text=data.location.text,
            latitude=data.location.latitude,
            longitude=data.location.longitude,
        ),
        image_url=data.image_url,
        image_analysis=image_analysis_obj,
    )
    await complaint.insert()
    logger.info(f"Complaint created: {complaint.id}")

    # ── Fire notifications + emails (non-blocking) ──
    complaint_id_str = str(complaint.id)

    async def _notify_on_create():
        from app.routers.notifications import create_notification
        # 1. Notify citizen
        await create_notification(
            user_id=current_user.id,
            title="✅ Complaint Submitted",
            message=f"Your complaint about '{ai_result['category']}' has been received and is being processed.",
            notif_type="success",
            complaint_id=complaint_id_str,
        )
        await send_complaint_submitted_email(
            citizen_email=current_user.email,
            citizen_name=current_user.name,
            complaint_id=complaint_id_str,
            category=ai_result["category"],
            priority=ai_result["priority"],
            location=data.location.text,
        )
        # 2. Notify ALL admins
        admins = await User.find(User.role == "admin").to_list()
        for admin in admins:
            await create_notification(
                user_id=admin.id,
                title="🔔 New Complaint Submitted",
                message=f"{current_user.name} reported a '{ai_result['category']}' issue at {data.location.text}.",
                notif_type="info",
                complaint_id=complaint_id_str,
            )
            await send_new_complaint_admin_email(
                admin_email=admin.email,
                admin_name=admin.name,
                complaint_id=complaint_id_str,
                citizen_name=current_user.name,
                category=ai_result["category"],
                priority=ai_result["priority"],
                location=data.location.text,
                description_snippet=data.description,
            )

    asyncio.create_task(_notify_on_create())

    return complaint_to_response(complaint)


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    current_user: User = Depends(get_current_user),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    complaint_status: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List complaints with filtering.
    
    Citizens see only their own complaints.
    Admins see all complaints.
    Supports filtering by category, priority, status, department, date range, and text search.
    """
    # Build MongoDB query filters
    query = {}

    # Role-based filtering
    if current_user.role == "citizen":
        query["citizen_id"] = current_user.id

    # Optional filters
    if category:
        query["ai_output.category"] = category
    if priority:
        query["ai_output.priority"] = priority
    if complaint_status:
        query["status"] = complaint_status
    if department:
        query["assigned_department"] = department
    if date_from:
        query.setdefault("created_at", {})["$gte"] = date_from
    if date_to:
        query.setdefault("created_at", {})["$lte"] = date_to
    if search:
        query["description"] = {"$regex": search, "$options": "i"}

    # Execute query with pagination
    skip = (page - 1) * page_size
    total = await Complaint.find(query).count()
    complaints = (
        await Complaint.find(query)
        .sort("-created_at")
        .skip(skip)
        .limit(page_size)
        .to_list()
    )

    return ComplaintListResponse(
        complaints=[complaint_to_response(c) for c in complaints],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
):
    """Get a single complaint by ID.
    
    Citizens can only view their own complaints.
    Admins can view any complaint.
    """
    complaint = await Complaint.get(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Citizens can only view their own complaints
    if current_user.role == "citizen" and complaint.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own complaints",
        )

    return complaint_to_response(complaint)


@router.patch("/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: PydanticObjectId,
    data: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a complaint's status, department, or confirmed category.
    
    Admin can update status and department.
    Citizens can update their own citizen_confirmed_category.
    """
    complaint = await Complaint.get(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )

    # Authorization check
    if current_user.role == "citizen":
        if complaint.citizen_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own complaints",
            )
        # Citizens can only update confirmed category
        if data.status is not None or data.assigned_department is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update status and department",
            )

    # Apply updates
    update_data = data.model_dump(exclude_unset=True)
    old_status = complaint.status
    old_department = complaint.assigned_department

    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await complaint.set(update_data)

    # Refresh from DB
    complaint = await Complaint.get(complaint_id)

    # ── Fire notifications + emails for citizen (non-blocking) ──
    new_status = complaint.status
    new_department = complaint.assigned_department
    complaint_id_str = str(complaint_id)
    category = complaint.ai_output.category

    async def _notify_on_update():
        from app.routers.notifications import create_notification
        citizen = await User.get(complaint.citizen_id)
        if not citizen:
            return

        # Status changed
        if data.status is not None and new_status != old_status:
            await create_notification(
                user_id=citizen.id,
                title="📋 Complaint Status Updated",
                message=f"Your complaint status changed from '{old_status}' to '{new_status}'.",
                notif_type="success" if new_status == "Resolved" else "info",
                complaint_id=complaint_id_str,
            )
            await send_status_update_email(
                citizen_email=citizen.email,
                citizen_name=citizen.name,
                complaint_id=complaint_id_str,
                old_status=old_status,
                new_status=new_status,
                category=category,
            )

        # Department assigned/changed
        if data.assigned_department is not None and new_department != old_department and new_department:
            await create_notification(
                user_id=citizen.id,
                title="🏢 Department Assigned",
                message=f"Your complaint has been assigned to '{new_department}'.",
                notif_type="info",
                complaint_id=complaint_id_str,
            )
            await send_department_assigned_email(
                citizen_email=citizen.email,
                citizen_name=citizen.name,
                complaint_id=complaint_id_str,
                department=new_department,
                category=category,
            )

    asyncio.create_task(_notify_on_update())

    return complaint_to_response(complaint)


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_complaint(
    complaint_id: PydanticObjectId,
    current_user: User = Depends(require_admin),
):
    """Delete a complaint. Admin only."""
    complaint = await Complaint.get(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found",
        )
    await complaint.delete()
    logger.info(f"Complaint {complaint_id} deleted by admin {current_user.email}")
