from pathlib import Path
import sys
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.image_analysis_service import analyze_uploaded_image

# Create a sample test image
test_img_path = PROJECT_ROOT / "scripts" / "sample_pothole.jpg"
img_array = np.zeros((300, 300, 3), dtype=np.uint8)
img_array[:, :] = [70, 70, 75] # Asphalt grey background
img_array[100:200, 100:200] = [30, 25, 20] # Dark pothole hole
Image.fromarray(img_array).save(test_img_path)

print("Analyzing sample image locally...")
res = analyze_uploaded_image(str(test_img_path))
print("LOCAL IMAGE ANALYSIS RESULT:")
for k, v in res.items():
    print(f"  - {k}: {v}")
