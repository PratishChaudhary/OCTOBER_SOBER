import os
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
from gtts import gTTS

app = FastAPI()

# Mount current directory to serve static HTML files
app.mount("/static", StaticFiles(directory="static"), name="static")
# Load Whisper STT (small model runs fast on CPU/GPU)
stt_model = WhisperModel("base", device="cpu", compute_type="int8")

with open("geminiapi.env") as api:
    GEMINI_API_KEY = "".join(api.readlines(1)).split("=")[1]
    BACKBOARD_API_KEY = api.readlines()[1].split("=")[1]
BACKBOARD_URL = "https://app.backboard.io/api" # Update per Backboard docs

@app.get("/")
async def index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(file: UploadFile = File(...)):
    # 1. Save incoming audio from phone
    audio_path = "user_input.mp3"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # 2. Convert Audio to Text
    segments, _ = stt_model.transcribe(audio_path)
    user_text = " ".join([segment.text for segment in segments])

    # 3. Call Backboard.io (Routing to Gemma Open Model)
    headers = {
        "Authorization": f"Bearer {BACKBOARD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemma-2-9b-it", # Selected Gemma model
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly language practice partner. "
                    "Keep responses concise (1-2 sentences) so they sound natural when spoken."
                )
            },
            {"role": "user", "content": user_text}
        ]
    }
    
    response = requests.post(BACKBOARD_URL, json=payload, headers=headers)
    bot_reply = response.json()["choices"][0]["message"]["content"]
    
    # 4. Convert Text to Speech
    tts = gTTS(text=bot_reply, lang="es") # Change lang code to target language (e.g. 'es', 'en', 'ne')
    output_audio_path = "static/response.mp3"
    tts.save(output_audio_path)

    # 5. Return JSON to frontend
    return JSONResponse({
        "user_transcript": user_text,
        "bot_reply": bot_reply,
        "audio_url": "/static/response.mp3"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)