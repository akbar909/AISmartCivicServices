"""
Async email notification service using aiosmtplib + Gmail SMTP.

Sends HTML emails for:
- Complaint submission confirmation (citizen)
- New complaint alert (admin)
- Status update (citizen)
- Department assignment (citizen)
"""

import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_base_html(title: str, body: str) -> str:
    """Wrap content in a branded HTML email template."""
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <style>
    body {{ margin:0; padding:0; background:#f1f5f9; font-family: 'Segoe UI', Arial, sans-serif; }}
    .wrapper {{ max-width:600px; margin:32px auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08); }}
    .header {{ background:linear-gradient(135deg,#0f766e,#059669); padding:32px 40px; text-align:center; }}
    .header h1 {{ margin:0; color:#ffffff; font-size:22px; font-weight:700; letter-spacing:-0.5px; }}
    .header p {{ margin:6px 0 0; color:#99f6e4; font-size:13px; }}
    .body {{ padding:36px 40px; }}
    .body h2 {{ margin:0 0 12px; color:#0f172a; font-size:18px; font-weight:700; }}
    .body p {{ margin:0 0 16px; color:#475569; font-size:14px; line-height:1.7; }}
    .badge {{ display:inline-block; padding:6px 14px; border-radius:99px; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; }}
    .badge-open {{ background:#dbeafe; color:#1d4ed8; }}
    .badge-assigned {{ background:#fef3c7; color:#b45309; }}
    .badge-inprogress {{ background:#ede9fe; color:#6d28d9; }}
    .badge-resolved {{ background:#dcfce7; color:#15803d; }}
    .badge-high {{ background:#fee2e2; color:#b91c1c; }}
    .badge-medium {{ background:#fef3c7; color:#b45309; }}
    .badge-low {{ background:#f0fdf4; color:#166534; }}
    .info-box {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:20px 24px; margin:20px 0; }}
    .info-box .row {{ display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:13px; }}
    .info-box .row:last-child {{ border-bottom:none; }}
    .info-box .label {{ color:#94a3b8; font-weight:600; }}
    .info-box .value {{ color:#0f172a; font-weight:600; text-align:right; max-width:65%; }}
    .btn {{ display:inline-block; background:linear-gradient(135deg,#0f766e,#059669); color:#ffffff!important; text-decoration:none; padding:13px 28px; border-radius:10px; font-weight:700; font-size:14px; margin-top:8px; }}
    .footer {{ background:#f8fafc; border-top:1px solid #e2e8f0; padding:20px 40px; text-align:center; color:#94a3b8; font-size:12px; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🏙️ AI Smart Civic Services</h1>
      <p>Intelligent Grievance Management Platform</p>
    </div>
    <div class="body">
      {body}
    </div>
    <div class="footer">
      <p>This is an automated message from AI Smart Civic Services.<br/>Please do not reply to this email.</p>
    </div>
  </div>
</body>
</html>
"""


async def _send_email(to_email: str, subject: str, html_body: str) -> None:
    """Send a single HTML email via Gmail SMTP (async, non-blocking)."""
    settings = get_settings()
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.warning("SMTP credentials not configured — email not sent.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            start_tls=True,
            username=settings.EMAIL_USER,
            password=settings.EMAIL_PASSWORD,
        )
        logger.info(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


def send_email_background(to_email: str, subject: str, html_body: str) -> None:
    """Fire-and-forget email — creates its own event loop task so it never blocks the request."""
    asyncio.create_task(_send_email(to_email, subject, html_body))


# ── Email Templates ──────────────────────────────────────────────────────────

async def send_complaint_submitted_email(
    citizen_email: str,
    citizen_name: str,
    complaint_id: str,
    category: str,
    priority: str,
    location: str,
) -> None:
    """Send confirmation email to citizen after submitting a complaint."""
    priority_class = {"High": "high", "Medium": "medium", "Low": "low"}.get(priority, "low")
    body = f"""
      <h2>✅ Complaint Submitted Successfully</h2>
      <p>Hi <strong>{citizen_name}</strong>, your civic complaint has been received and is being processed by our AI system.</p>
      <div class="info-box">
        <div class="row"><span class="label">Complaint ID</span><span class="value">#{complaint_id[-8:].upper()}</span></div>
        <div class="row"><span class="label">Category</span><span class="value">{category}</span></div>
        <div class="row"><span class="label">Priority</span><span class="value"><span class="badge badge-{priority_class}">{priority}</span></span></div>
        <div class="row"><span class="label">Location</span><span class="value">{location}</span></div>
        <div class="row"><span class="label">Status</span><span class="value"><span class="badge badge-open">Open</span></span></div>
      </div>
      <p>You will receive email updates when your complaint status changes or a department is assigned.</p>
    """
    await _send_email(
        citizen_email,
        f"✅ Complaint Received — #{complaint_id[-8:].upper()}",
        _get_base_html("Complaint Submitted", body),
    )


async def send_new_complaint_admin_email(
    admin_email: str,
    admin_name: str,
    complaint_id: str,
    citizen_name: str,
    category: str,
    priority: str,
    location: str,
    description_snippet: str,
) -> None:
    """Notify admin about a newly submitted complaint."""
    priority_class = {"High": "high", "Medium": "medium", "Low": "low"}.get(priority, "low")
    body = f"""
      <h2>🔔 New Complaint Submitted</h2>
      <p>Hi <strong>{admin_name}</strong>, a new civic complaint has been submitted and requires your attention.</p>
      <div class="info-box">
        <div class="row"><span class="label">Complaint ID</span><span class="value">#{complaint_id[-8:].upper()}</span></div>
        <div class="row"><span class="label">Citizen</span><span class="value">{citizen_name}</span></div>
        <div class="row"><span class="label">Category</span><span class="value">{category}</span></div>
        <div class="row"><span class="label">Priority</span><span class="value"><span class="badge badge-{priority_class}">{priority}</span></span></div>
        <div class="row"><span class="label">Location</span><span class="value">{location}</span></div>
      </div>
      <p style="font-style:italic;color:#64748b;">"{description_snippet[:200]}{'...' if len(description_snippet) > 200 else ''}"</p>
      <p>Please log in to the admin dashboard to assign a department and take action.</p>
    """
    await _send_email(
        admin_email,
        f"🔔 New Complaint — {category} | Priority: {priority}",
        _get_base_html("New Complaint", body),
    )


async def send_status_update_email(
    citizen_email: str,
    citizen_name: str,
    complaint_id: str,
    old_status: str,
    new_status: str,
    category: str,
) -> None:
    """Notify citizen that their complaint status has changed."""
    status_class = {
        "Open": "open", "Assigned": "assigned",
        "In Progress": "inprogress", "Resolved": "resolved"
    }.get(new_status, "open")
    body = f"""
      <h2>📋 Complaint Status Updated</h2>
      <p>Hi <strong>{citizen_name}</strong>, your complaint status has been updated by the service team.</p>
      <div class="info-box">
        <div class="row"><span class="label">Complaint ID</span><span class="value">#{complaint_id[-8:].upper()}</span></div>
        <div class="row"><span class="label">Category</span><span class="value">{category}</span></div>
        <div class="row"><span class="label">Previous Status</span><span class="value">{old_status}</span></div>
        <div class="row"><span class="label">New Status</span><span class="value"><span class="badge badge-{status_class}">{new_status}</span></span></div>
      </div>
      {'<p>🎉 Great news! Your complaint has been resolved. Thank you for helping improve your community.</p>' if new_status == "Resolved" else '<p>Your complaint is being actively worked on. We will keep you updated.</p>'}
    """
    await _send_email(
        citizen_email,
        f"📋 Status Update: {new_status} — #{complaint_id[-8:].upper()}",
        _get_base_html("Status Updated", body),
    )


async def send_department_assigned_email(
    citizen_email: str,
    citizen_name: str,
    complaint_id: str,
    department: str,
    category: str,
) -> None:
    """Notify citizen that their complaint has been assigned to a department."""
    body = f"""
      <h2>🏢 Department Assigned</h2>
      <p>Hi <strong>{citizen_name}</strong>, your complaint has been reviewed and assigned to the responsible department.</p>
      <div class="info-box">
        <div class="row"><span class="label">Complaint ID</span><span class="value">#{complaint_id[-8:].upper()}</span></div>
        <div class="row"><span class="label">Category</span><span class="value">{category}</span></div>
        <div class="row"><span class="label">Assigned Department</span><span class="value"><strong>{department}</strong></span></div>
      </div>
      <p>The <strong>{department}</strong> department has been notified and will begin working on your complaint. You will receive further updates as progress is made.</p>
    """
    await _send_email(
        citizen_email,
        f"🏢 Department Assigned — #{complaint_id[-8:].upper()}",
        _get_base_html("Department Assigned", body),
    )
