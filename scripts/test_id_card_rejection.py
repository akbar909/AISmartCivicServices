import urllib.request
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.image_analysis_service import analyze_uploaded_image

id_card_path = PROJECT_ROOT / "scripts" / "id_card_test.jpg"

req = urllib.request.Request(
    "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=300", # Document / ID card / legal paper photo
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as resp, open(id_card_path, "wb") as out:
    out.write(resp.read())

print("Downloaded sample document/ID card photo:", id_card_path)

res = analyze_uploaded_image(str(id_card_path), expected_category="Road")
print("ID CARD / DOCUMENT ANALYSIS RESULT:")
for k, v in res.items():
    print(f"  - {k}: {v}")
