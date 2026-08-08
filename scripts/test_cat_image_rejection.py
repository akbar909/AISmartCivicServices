from pathlib import Path
import sys
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.image_analysis_service import analyze_uploaded_image

# Create a sample cat image using PIL / fake cat image
cat_img_path = PROJECT_ROOT / "scripts" / "cat_test.jpg"

# Download a real small sample cat image or create one
import urllib.request
req = urllib.request.Request(
    "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=300",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as resp, open(cat_img_path, "wb") as out:
    out.write(resp.read())
print("Downloaded sample cat photo:", cat_img_path)

if cat_img_path.exists():
    res = analyze_uploaded_image(str(cat_img_path))
    print("CAT IMAGE ANALYSIS RESULT:")
    for k, v in res.items():
        print(f"  - {k}: {v}")
