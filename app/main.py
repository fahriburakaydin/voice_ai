import os, uuid, aiofiles
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from .config import settings
from .stt import transcribe_audio
from .gpt import generate_reply, extract_insights, SYSTEM_PROMPT
from .tts import synthesize_voice
from .storage import upload_audio
from .memory import (
    get_short, append_short,
    retrieve_long, upsert_long
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse, FileResponse


import logging
logging.info(f"Loaded settings:  GCP_PROJECT={settings.gcp_project}, "
             f"GCS_BUCKET={settings.gcs_bucket}, "
             f"REDIS_URL={settings.redis_url}")


app = FastAPI()

# 1️⃣ Allow  UI to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # or restrict to the domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve CSS/JS under /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve the UI under / (index.html)
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("app/static/index.html")

@app.post("/chat/")
async def chat(
    user_id: str = Form(...),
    text: str    = Form(None),
    audio: UploadFile = File(None)
):
    if not text and not audio:
        raise HTTPException(400, "Send text or audio.")

    # 1. Get user_text
    if audio:
        tmp = f"/tmp/{uuid.uuid4()}.{audio.filename.split('.')[-1]}"
        async with aiofiles.open(tmp, "wb") as f:
            await f.write(await audio.read())
        user_text = transcribe_audio(tmp)
        os.remove(tmp)
    else:
        user_text = text

    # 2. Memory retrieval
    long_mem  = retrieve_long(user_id, user_text)
    short_hist = get_short(user_id)

    # 3. Build GPT prompt
    messages = [
    {"role":"system", "content": SYSTEM_PROMPT},
    {"role":"system", "content": "Memories:\n" + "\n".join(f"- {m}" for m in long_mem)},
    *short_hist,
    {"role":"user",   "content": user_text}
    ]


    # 4. Generate reply + TTS
    reply = generate_reply(messages)
    audio_bytes = synthesize_voice(reply)
    audio_url   = upload_audio(audio_bytes)

    # 5. Update memories
    append_short(user_id, "user", user_text)
    append_short(user_id, "assistant", reply)
    for insight in extract_insights(user_text, reply):
        upsert_long(user_id, insight)

    return JSONResponse({"reply": reply, "audio_url": audio_url})
