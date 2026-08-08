import urllib.request
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.image_analysis_service import analyze_uploaded_image

water_img_path = PROJECT_ROOT / "scripts" / "water_test.jpg"

req = urllib.request.Request(
    "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg", # Or hydrant image
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as resp, open(water_img_path, "wb") as out:
    out.write(resp.read())

print("Downloaded sample water photo:", water_img_path)

# Test 1: Match expected_category="Water"
res1 = analyze_uploaded_image(str(water_img_path), expected_category="Water")
print("\n[TEST 1] Expected = Water:")
print(f"  - is_relevant: {res1.get('is_relevant')}")
print(f"  - suggested_category: {res1.get('suggested_category')}")
print(f"  - detected_tags: {res1.get('detected_tags')}")

# Test 2: Mismatch expected_category="Road"
res2 = analyze_uploaded_image(str(water_img_path), expected_category="Road")
print("\n[TEST 2] Expected = Road (MISMATCH):")
print(f"  - is_relevant: {res2.get('is_relevant')}")
print(f"  - rejection_reason: {res2.get('rejection_reason')}")
