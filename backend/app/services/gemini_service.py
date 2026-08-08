"""
Gemini AI Service.

Uses Google's Gemini API for:
1. generate_summary() — short actionable summary of a complaint for the service team
2. chatbot_reply() — conversational responses for the guidance chatbot

This service is SEPARATE from the ML classification (ai_service.py).
Classification uses pre-trained scikit-learn models; Gemini is only used
for natural language generation (summaries and chat).

All Gemini calls are wrapped in try/except for graceful degradation:
- If summary generation fails, the complaint still saves with summary=None
- If chatbot reply fails, a generic fallback message is returned
"""

import logging
from typing import List, Optional

from google import genai
from google.genai import types

from app.config import get_settings

logger = logging.getLogger(__name__)

# Global client reference
_client = None
_configured = False

MODEL_NAME = "gemini-2.5-flash"

# System prompt for the guidance chatbot — keeps Gemini focused on civic complaints
CHATBOT_SYSTEM_PROMPT = """You are a helpful civic services assistant for a municipal complaint platform called "AI Smart Civic Services".

Your role is to help citizens file effective complaints about local infrastructure problems. You should:
1. Help citizens describe their issues clearly and completely
2. Suggest which category their complaint might fall under
3. Ask clarifying questions when details are missing (severity, timing, scope — note: location is collected in a separate form field)
4. Provide guidance on what information helps service teams resolve issues faster

When asked about categories or listing options, ALWAYS format them in a clean, structured bulleted list with bold category names, exactly like this:

Certainly! Here are all the valid complaint categories that you can choose from:
* **Road**: Potholes, street conditions, traffic signals, road damage
* **Water**: Water supply issues, hydrant leaks, water system problems
* **Waste**: Garbage collection, sanitation, graffiti
* **Electricity**: Street lights, power outages, electrical infrastructure
* **Drainage**: Sewer systems, drainage blockages, flooding
* **Safety**: Public safety concerns, noise complaints, hazards
* **Other**: Issues not fitting the above categories

Feel free to describe an issue, and I can suggest which category it might best fit into!

FORMATTING REQUIREMENTS:
- Always use clean Markdown formatting with bullet points (* or -), bold category titles, and line breaks between items.
- Never collapse bulleted lists into a single continuous line of text.
- Stay focused on civic complaint guidance. Do not answer unrelated questions outside municipal services."""


# Candidate models to try in order when encountering quota limits or errors
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]


def configure_gemini():
    """Configure the Gemini API client. Called once at startup."""
    global _client, _configured

    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        logger.warning(
            "GEMINI_API_KEY not set. Summary generation and chatbot will be unavailable."
        )
        return

    try:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
        _configured = True
        logger.info("Gemini API configured successfully with google-genai SDK")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")


def _call_gemini_with_fallback(contents, system_instruction: Optional[str] = None) -> str:
    """Execute generate_content with automatic fallback models on 429 quota or 404 errors."""
    if not _configured or not _client:
        raise RuntimeError("Gemini API is not configured")

    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(system_instruction=system_instruction)
            
            response = _client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            err_str = str(e)
            logger.warning(f"Gemini call to model '{model_name}' failed: {e}")
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "NOT_FOUND" in err_str or "404" in err_str:
                continue
            break

    if last_error:
        raise last_error
    raise RuntimeError("No Gemini response received")


async def generate_summary(
    complaint_text: str, category: str, priority: str
) -> Optional[str]:
    """Generate a short, actionable summary of a complaint for the service team."""
    if not _configured or not _client:
        logger.warning("Gemini not configured, skipping summary generation")
        return None

    prompt = f"""Summarize this civic complaint in 1-2 concise, actionable sentences for the municipal service team. 
Focus on: what the problem is, where it is, and urgency level.

Category: {category}
Priority: {priority}
Complaint: {complaint_text}

Provide only the summary, no preamble or labels."""

    try:
        summary = _call_gemini_with_fallback(contents=prompt)
        logger.info("Summary generated successfully")
        return summary
    except Exception as e:
        logger.error(f"Gemini summary generation failed: {e}")
        return None


async def generate_clarifying_question(
    complaint_text: str, suggested_category: str, confidence: float
) -> Optional[str]:
    """Generate a clarifying question when classification confidence is low."""
    if not _configured or not _client:
        return None

    prompt = f"""A citizen is filing a civic complaint. Based on their description, the AI suggests category "{suggested_category}" with {confidence:.0%} confidence.

Complaint text: "{complaint_text}"

Note: The complaint form already has a SEPARATE required field for "Location". Therefore, DO NOT ask for location, address, or street name.

If the description is missing important problem details (severity, scope, hazard level, timing, or duration), generate ONE short, friendly clarifying question to help them describe the problem better. If the description seems complete or already detailed, respond with just "None".

Respond with only the question or "None", nothing else."""

    try:
        result = _call_gemini_with_fallback(contents=prompt)
        if result.lower() == "none":
            return None
        return result
    except Exception as e:
        logger.error(f"Gemini clarifying question generation failed: {e}")
        return None


async def chatbot_reply(
    message: str,
    history: List[dict],
    context: Optional[str] = None,
) -> str:
    """Generate a conversational response for the guidance chatbot."""
    if not _configured or not _client:
        return (
            "I'm sorry, the AI assistant is currently unavailable. "
            "Please describe your complaint in the form and our team will review it."
        )

    try:
        contents = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])],
            ))

        user_message = message
        if context:
            user_message = f"[Context: {context}]\n\n{message}"
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        ))

        return _call_gemini_with_fallback(
            contents=contents,
            system_instruction=CHATBOT_SYSTEM_PROMPT,
        )
    except Exception as e:
        logger.error(f"Gemini chatbot reply failed: {e}")
        return (
            "I'm having trouble connecting right now. Please try again, "
            "or go ahead and submit your complaint — our team will review it."
        )
