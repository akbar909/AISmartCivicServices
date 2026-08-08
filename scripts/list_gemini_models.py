from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import get_settings
from google import genai

settings = get_settings()
print("API Key loaded:", bool(settings.GEMINI_API_KEY))

client = genai.Client(api_key=settings.GEMINI_API_KEY)
print("Listing available models...")
try:
    models = list(client.models.list())
    for m in models:
        # Print model names that support generateContent
        name = getattr(m, 'name', str(m))
        print("-", name)
except Exception as e:
    print("Error listing models:", e)
