"""
Cloudinary Image Upload Service with local fallback.

If CLOUDINARY_CLOUD_NAME is provided, uploads images to Cloudinary.
Otherwise, saves images locally to the `uploads/` directory.
"""

import os
import uuid
import logging
import aiofiles
import cloudinary
import cloudinary.uploader
from app.config import get_settings

logger = logging.getLogger(__name__)

_configured = False


def configure_cloudinary():
    """Configure Cloudinary credentials from settings."""
    global _configured
    settings = get_settings()
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
        try:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            _configured = True
            logger.info("Cloudinary configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Cloudinary: {e}")
            _configured = False
    else:
        logger.info("Cloudinary credentials not set. Falling back to local disk uploads.")


async def upload_image_file(file_content: bytes, filename: str) -> str:
    """
    Upload an image file. Returns a public URL string.
    
    If Cloudinary is configured, uploads directly to Cloudinary.
    Otherwise, saves to local `uploads/` folder and returns local URL path.
    """
    settings = get_settings()
    ext = os.path.splitext(filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    # Try Cloudinary upload if configured
    if _configured:
        try:
            res = cloudinary.uploader.upload(
                file_content,
                folder="civic_complaints",
                public_id=f"complaint_{uuid.uuid4().hex}",
                resource_type="image",
            )
            secure_url = res.get("secure_url") or res.get("url")
            logger.info(f"Image uploaded to Cloudinary: {secure_url}")
            return secure_url
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}. Falling back to local disk.")

    # Fallback to local storage
    upload_dir = settings.UPLOAD_DIR or "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    local_url = f"/uploads/{unique_name}"
    logger.info(f"Image saved locally: {local_url}")
    return local_url
