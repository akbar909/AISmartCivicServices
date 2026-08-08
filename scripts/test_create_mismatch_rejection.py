import urllib.request
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
cat_img_path = PROJECT_ROOT / "scripts" / "cat_test.jpg"

# 1. Login as citizen
login_data = json.dumps({"email": "test@gmail.com", "password": "test12"}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req).read())
token = res["access_token"]

# 2. Try creating a Road complaint with cat image URL
complaint_payload = json.dumps({
    "description": "Potholes, street conditions, traffic signals, road damage on Main St",
    "location": {"text": "123 Main Street"},
    "image_url": "/uploads/cat_test.jpg"
}).encode()

create_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/complaints",
    data=complaint_payload,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
)

print("Attempting to submit Road complaint with cat image URL...")
try:
    resp = urllib.request.urlopen(create_req)
    print("SUCCESS (UNEXPECTED):", resp.read().decode())
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"REJECTED WITH HTTP {e.code}:", err_body)
