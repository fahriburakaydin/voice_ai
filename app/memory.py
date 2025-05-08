# app/memory.py
import json
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from redis import Redis
from .config import settings

# —— Pinecone long-term setup —— #
pc = Pinecone(
    api_key=settings.pinecone_api_key,
    environment=settings.pinecone_env
)
if settings.pinecone_index not in pc.list_indexes().names():
    pc.create_index(
        name=settings.pinecone_index,
        dimension=settings.embedding_dim,
        metric="cosine",
        spec=ServerlessSpec()               # free serverless tier
    )
index = pc.Index(settings.pinecone_index)

# —— OpenAI client for embeddings —— #
oa = OpenAI(api_key=settings.openai_api_key)

# —— Redis short-term setup —— #
redis_client = Redis.from_url(settings.redis_url)

def get_short(user_id: str) -> list[dict]:
    """Return the last N messages for this user from Redis."""
    raw = redis_client.get(f"{user_id}:short") or b"[]"
    return json.loads(raw)

def append_short(user_id: str, role: str, text: str):
    """Append one turn to the short-term history, trimming to length."""
    history = get_short(user_id)
    history.append({"role": role, "content": text})
    # keep only the last N turns
    history = history[-settings.short_term_size :]
    redis_client.set(f"{user_id}:short", json.dumps(history))

def retrieve_long(user_id: str, query: str) -> list[str]:
    """Embed the query, fetch top-K similar past insights."""
    resp = oa.embeddings.create(
        model=settings.embedding_model,
        input=query
    )
    emb = resp.data[0].embedding
    results = index.query(
        vector=emb,
        top_k=settings.memory_k,
        include_metadata=True
    )
    return [m.metadata["text"] for m in results.matches]

def upsert_long(user_id: str, text: str):
    """Embed one fact and upsert it under the user’s namespace."""
    resp = oa.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    emb = resp.data[0].embedding
    vid = f"{user_id}-{abs(hash(text))}"
    index.upsert([(vid, emb, {"text": text, "user": user_id})])
