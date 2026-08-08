"""
Department document model for MongoDB via Beanie ODM.
"""

from beanie import Document
from pydantic import Field


class Department(Document):
    """Represents a civic service department."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")

    class Settings:
        name = "departments"


# Default departments to seed on first startup
DEFAULT_DEPARTMENTS = [
    {"name": "Roads", "description": "Road maintenance, potholes, traffic signals, street conditions"},
    {"name": "Water", "description": "Water supply, hydrant leaks, water system issues"},
    {"name": "Waste", "description": "Garbage collection, sanitation, graffiti removal"},
    {"name": "Electricity", "description": "Street lights, power outages, electrical infrastructure"},
    {"name": "Drainage", "description": "Sewer systems, drainage blockages, flooding"},
    {"name": "Safety", "description": "Public safety concerns, noise complaints, hazards"},
    {"name": "Other", "description": "General complaints not fitting other categories"},
]
