from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import init_db, close_db
from app.models.user import User
from app.models.complaint import Complaint, Location, AIOutput

async def test_location_schema():
    await init_db()
    citizen = await User.find_one({"email": "test@gmail.com"})
    print("Found citizen:", citizen.email)
    
    complaint = Complaint(
        citizen_id=citizen.id,
        description="There is a severe water pipeline burst flooding the main intersection.",
        ai_output=AIOutput(category="Water", category_confidence=0.95, priority="High", priority_confidence=0.90, summary="Pipe burst flooding intersection."),
        location=Location(text="123 Main St, NY", latitude=40.7128, longitude=-74.0060)
    )
    await complaint.insert()
    print("Complaint created with lat/lon:", complaint.id)
    
    fetched = await Complaint.get(complaint.id)
    print("Fetched location from DB:", fetched.location.dict())
    await close_db()

if __name__ == "__main__":
    asyncio.run(test_location_schema())
