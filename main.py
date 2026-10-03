import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
from gtts import gTTS
from backboard_client import BackboardError, generate_reply

load_dotenv()

BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY")
BACKBOARD_ASSISTANT_ID = os.getenv("BACKBOARD_ASSISTANT_ID")
BACKBOARD_MODEL_NAME = os.getenv("BACKBOARD_MODEL_NAME", "gemini-3.8-flash")
TUTOR_SYSTEM_PROMPT = (
    "You are a friendly Korean conversation partner helping a learner practice Korean. "
    "The Learner will speak in English and you will translate their meaning into natural Korean. "
    "Just translate the meaning of the Learner's English into natural Korean, donot over-explain grammar unless asked. "
)

app = FastAPI()

# Mount current directory to serve static HTML files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Load Whisper STT (small model runs fast on CPU/GPU)
stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")

@app.get("/")
async def index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(file: UploadFile = File(...)):
    if not BACKBOARD_API_KEY or not BACKBOARD_ASSISTANT_ID:
        raise HTTPException(
            status_code=503,
            detail="Backboard API key and assistant ID must be configured.",
        )

    # 1. Save incoming audio from phone
    audio_path = "user_input.mp3"
    audio_content = await file.read()
    if not audio_content:
        raise HTTPException(status_code=422, detail="The uploaded audio file is empty.")
    with open(audio_path, "wb") as f:
        f.write(audio_content)

    # 2. Convert Audio to Text
    segments, _ = stt_model.transcribe(audio_path, language="en")
    user_text = " ".join([segment.text for segment in segments])
    if not user_text.strip():
        raise HTTPException(status_code=422, detail="No speech was recognized.")

    # 3. Retrieve lesson context with Backboard and generate through its Google provider
    try:
        bot_reply, retrieved_files = generate_reply(
            user_text=user_text,
            api_key=BACKBOARD_API_KEY,
            assistant_id=BACKBOARD_ASSISTANT_ID,
            model_name=BACKBOARD_MODEL_NAME,
            system_prompt=TUTOR_SYSTEM_PROMPT,
        )
    except BackboardError as exc:
        raise HTTPException(
            status_code=502,
            detail="The language tutor service could not generate a reply.",
        ) from exc
    
    # 4. Convert Text to Speech
    tts = gTTS(text=bot_reply, lang="ko")
    output_audio_path = "static/response.mp3"
    try:
        tts.save(output_audio_path)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Korean speech could not be generated.",
        ) from exc

    # 5. Return JSON to frontend
    return JSONResponse({
        "user_transcript": user_text,
        "bot_reply": bot_reply,
        "audio_url": "/static/response.mp3",
        "retrieved_files": retrieved_files,
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)