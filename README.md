# OCTOBER_SOBER

*This is my hackathon project for MLH HacktoberFest.*

## Korean Tutor Setup

The FastAPI app transcribes Korean speech with Whisper, sends the transcript to a
Backboard assistant for document retrieval and Gemini generation, then speaks the
reply in Korean. Configure the Google/Gemini provider and a supported model in
Backboard before running the app.

1. Install dependencies with `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env` and set the Backboard API key, assistant ID, and
   model name. Do not put API keys in source files.
3. In Backboard, upload curated Korean lesson documents to the configured assistant
   and wait until each document is indexed.
4. Run `uvicorn main:app --reload` and open `http://127.0.0.1:8000`.

To check the Backboard assistant independently, run `python test.py` after setting
the environment variables. Unit tests for request construction run with
`python -m pytest tests -q`.

The app does not send a thread ID and sets Backboard memory to `off`; Backboard may
still retain service-side request records. Rotate any API keys previously committed
or shared outside your secrets manager.
