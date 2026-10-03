from faster_whisper import WhisperModel
import requests
from google import genai 


BACKBOARD_API_KEY = "espr_0QE6qLlcgFMva192zz9oJgJGtMmNu16se1NKkW4jwMk"
BACKBOARD_URL = "https://app.backboard.io/api/assistants" # Update per Backboard docs

model_size = "turbo"

# Run on GPU with FP16
model = WhisperModel("base", device="cpu", compute_type="int8")

# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, _ = model.transcribe("user_input.mp3")
user_text = " ".join([segment.text for segment in segments])

 # 3. Call Backboard.io (Routing to Gemma Open Model)


url = "https://app.backboard.io/api/threads/messages"
body = {
  "content": user_text,
  
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "my_tutor",
        "description": "You are a friendly language trainer bot",
        "parameters": {
          "type": "object",
          "properties": {
            "language": {
              "type": "eng",
              "description": "Keep responses concise (1-2 sentences) so they sound natural when spoken.",
            }
          }
        }
      }
    }
  ],
  "tok_k": 10,
}
headers = {
 "X-API-Key": BACKBOARD_API_KEY,
 "assistant_id": "4ba7e8f6-eba2-4c6b-85de-077d8d848d8b",
 "Content-Type": "application/json"
}
response = requests.post(url, json=body, headers=headers)
bot_reply = response.json()["content"]

print(bot_reply)