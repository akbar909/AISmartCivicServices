import urllib.request
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.image_analysis_service import analyze_uploaded_image

profile_pic_path = PROJECT_ROOT / "scripts" / "profile_pic_test.jpg"

req = urllib.request.Request(
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300", # Sample portrait / profile pic
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as resp, open(profile_pic_path, "wb") as out:
    out.write(resp.read())

print("Downloaded sample profile picture:", profile_pic_path)

res = analyze_uploaded_image(str(profile_pic_path), expected_category="Road")
print("PROFILE PIC ANALYSIS RESULT:")
for k, v in res.items():
    print(f"  - {k}: {v}")
