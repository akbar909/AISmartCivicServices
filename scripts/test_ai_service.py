from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.ai_service import load_models, classify_complaint

load_models()
text = ("There is a live exposed electrical wire hanging from a utility pole near the main road. "
        "It's been sparking intermittently since last night, especially after it rained, and it's "
        "very close to a spot where people walk and children play. This is extremely dangerous "
        "and needs urgent attention before someone gets hurt.")

print("CLASSIFICATION RESULT:", classify_complaint(text))
