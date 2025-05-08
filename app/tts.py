import requests
from .config import settings

def synthesize_voice(text: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.tts_voice_id}"
    headers = {"xi-api-key": settings.eleven_api_key}
    payload = {
        "text": text,
        "voice_settings": {
            "tts_voice_id": settings.tts_voice_id,
            "stability": settings.tts_stability,
            "similarity_boost": settings.tts_similarity
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.content
