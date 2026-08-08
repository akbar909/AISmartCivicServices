from pathlib import Path
import sys
import asyncio

# Setup sys.path to include the backend directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.gemini_service import configure_gemini, generate_summary, chatbot_reply, generate_clarifying_question

async def main():
    print("=== Testing Gemini Service ===")
    configure_gemini()
    
    print("\n[1] Testing Summary Generation:")
    summary = await generate_summary(
        complaint_text="There is a deep pothole on Main Street near 5th Ave causing tire damage and heavy traffic delay.",
        category="Road",
        priority="High"
    )
    print("Result:", summary)

    print("\n[2] Testing Clarifying Question Generation:")
    question = await generate_clarifying_question(
        complaint_text="Water leak somewhere on Main Street.",
        suggested_category="Water",
        confidence=0.55
    )
    print("Result:", question)

    print("\n[3] Testing Chatbot Reply (Categories Query):")
    reply = await chatbot_reply(
        message="What are the available complaint categories?",
        history=[]
    )
    print("Result:\n" + reply)

if __name__ == "__main__":
    asyncio.run(main())
