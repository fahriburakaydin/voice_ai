# app/stt.py
from openai import OpenAI
from .config import settings

oa = OpenAI(api_key=settings.openai_api_key)

def transcribe_audio(path: str) -> str:
    with open(path, "rb") as audio_file:
        # this returns a str when response_format="text"
        transcription: str = oa.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text"
        )
    return transcription
