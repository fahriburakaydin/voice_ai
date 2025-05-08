# app/storage.py
import uuid
from google.cloud import storage
from .config import settings

_client = storage.Client(project=settings.gcp_project)
_bucket = _client.bucket(settings.gcs_bucket)

def upload_audio(data: bytes) -> str:
    # 1) pick a unique name
    blob_name = f"sophie/{uuid.uuid4()}.mp3"
    blob = _bucket.blob(blob_name)
    # 2) upload
    blob.upload_from_string(data, content_type="audio/mpeg")
    # 3) return the public URL (no signing needed)
    return f"https://storage.googleapis.com/{settings.gcs_bucket}/{blob_name}"
