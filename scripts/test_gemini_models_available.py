from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from google import genai
from app.config import get_settings

client = genai.Client(api_key=get_settings().GEMINI_API_KEY)
models_to_test = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash-lite-001',
    'gemini-flash-latest',
    'gemini-2.5-pro',
    'gemini-3.6-flash',
]

print("Testing model generation...")
for m in models_to_test:
    try:
        res = client.models.generate_content(model=m, contents="Say hello in 2 words")
        print(f"[OK] {m}: {res.text.strip()}")
    except Exception as e:
        print(f"[FAIL] {m}: {e}")
