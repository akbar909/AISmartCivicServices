from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import init_db, close_db
from app.models.user import User
from app.routers.admin import get_stats

async def test_admin_stats():
    await init_db()
    admin_user = await User.find_one({"email": "admin@gmail.com"})
    print("Testing get_stats for admin user:", admin_user.email)
    stats = await get_stats(current_user=admin_user)
    print("STATS OUTPUT:", stats)
    await close_db()

if __name__ == "__main__":
    asyncio.run(test_admin_stats())
