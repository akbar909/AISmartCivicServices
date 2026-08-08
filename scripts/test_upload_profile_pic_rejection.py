import urllib.request
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
pic_path = PROJECT_ROOT / "scripts" / "profile_pic_test.jpg"

login_data = json.dumps({"email": "test@gmail.com", "password": "test12"}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
res = json.loads(urllib.request.urlopen(req).read())
token = res["access_token"]

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = []
body.append(f"--{boundary}".encode())
body.append(f'Content-Disposition: form-data; name="file"; filename="profile_pic.jpg"'.encode())
body.append(b"Content-Type: image/jpeg")
body.append(b"")
with open(pic_path, "rb") as f:
    body.append(f.read())
body.append(f"--{boundary}--".encode())
body.append(b"")
payload = b"\r\n".join(body)

upload_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/complaints/upload-image",
    data=payload,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
)

print("Attempting to upload professional profile picture via POST /api/complaints/upload-image...")
try:
    resp = urllib.request.urlopen(upload_req)
    print("SUCCESS (UNEXPECTED):", resp.read().decode())
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"REJECTED WITH HTTP {e.code}:", err_body)
