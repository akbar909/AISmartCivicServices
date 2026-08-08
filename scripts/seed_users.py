from pathlib import Path
import sys
import asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import init_db, close_db
from app.models.user import User
from app.services.auth_service import hash_password

async def seed_users():
    print("Connecting to MongoDB...")
    await init_db()

    users_to_seed = [
        {
            "email": "admin@gmail.com",
            "password": "test12",
            "name": "System Admin",
            "role": "admin"
        },
        {
            "email": "test@gmail.com",
            "password": "test12",
            "name": "Citizen Test User",
            "role": "citizen"
        }
    ]

    for u_data in users_to_seed:
        existing = await User.find_one(User.email == u_data["email"])
        if existing:
            print(f"User '{u_data['email']}' already exists. Updating password & role...")
            existing.password_hash = hash_password(u_data["password"])
            existing.role = u_data["role"]
            existing.name = u_data["name"]
            await existing.save()
            print(f"Updated user '{u_data['email']}' successfully.")
        else:
            print(f"Creating user '{u_data['email']}' ({u_data['role']})...")
            new_user = User(
                name=u_data["name"],
                email=u_data["email"],
                password_hash=hash_password(u_data["password"]),
                role=u_data["role"]
            )
            await new_user.insert()
            print(f"Created user '{u_data['email']}' successfully.")

    await close_db()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_users())
