import os

from dotenv import load_dotenv

from backboard_client import generate_reply


load_dotenv()

api_key = os.getenv("BACKBOARD_API_KEY")
assistant_id = os.getenv("BACKBOARD_ASSISTANT_ID")
model_name = os.getenv("BACKBOARD_MODEL_NAME", "gemini-2.5-flash")

if not api_key or not assistant_id:
    raise SystemExit("Set BACKBOARD_API_KEY and BACKBOARD_ASSISTANT_ID in .env first.")

reply, retrieved_files = generate_reply(
    user_text="안녕하세요. 한국어로 대화 연습을 하고 싶어요.",
    api_key=api_key,
    assistant_id=assistant_id,
    model_name=model_name,
    system_prompt=(
        "You are a friendly Korean conversation partner. Speak naturally in Korean, "
        "gently correct mistakes, and continue with a relevant follow-up."
    ),
)

print(reply)
print(f"Retrieved files: {len(retrieved_files)}")