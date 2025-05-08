import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

# — Pinecone setup (unchanged) —
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)
index_name = os.getenv("PINECONE_INDEX")
if index_name not in pc.list_indexes().names():
    pc.create_index(name=index_name, dimension=1536, metric="cosine", spec=ServerlessSpec())

index = pc.Index(index_name)
print("Index stats:", index.describe_index_stats())

# — NEW OpenAI client usage —
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create an embedding
resp = client.embeddings.create(
    model="text-embedding-ada-002",
    input="Hello, Sophie!"
)
real_vec = resp.data[0].embedding  # note: data is now under .data

# Upsert & query
index.upsert([("real-test", real_vec, {"text": "Hello, Sophie!"})])
res = index.query(vector=real_vec, top_k=1, include_metadata=True)
print(res)
