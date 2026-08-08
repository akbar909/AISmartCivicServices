from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import init_db, close_db
from app.models.user import User
from app.services.auth_service import verify_password, create_access_token

async def test_auth():
    await init_db()
    user = await User.find_one({"email": "admin@gmail.com"})
    print("User found:", user)
    if user:
        verified = verify_password("test12", user.password_hash)
        print("Password verified:", verified)
        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        print("Generated Token:", token)
    await close_db()

if __name__ == "__main__":
    asyncio.run(test_auth())
