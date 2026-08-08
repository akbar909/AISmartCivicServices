from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app

async def test_lifespan():
    print("Testing application lifespan startup...")
    async with app.router.lifespan_context(app):
        print("Application startup succeeded cleanly!")

if __name__ == "__main__":
    asyncio.run(test_lifespan())
