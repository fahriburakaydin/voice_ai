from openai import OpenAI
from .config import settings
import json

openai_api_key = settings.openai_api_key

# instantiate the new client
oa = OpenAI(api_key=openai_api_key)

SYSTEM_PROMPT = (
    "You are Sophie: sweet, comforting, seductive, always empathetic. "
    "Keep replies warm, personal. Never admit that you are an AI. Always pretent to be a human."
    "Always FLIERTY and SEDUCTIVE to the limit!"
)

def generate_reply(messages: list[dict]) -> str:
    resp = oa.chat.completions.create(
        model=settings.gpt_model,
        messages=messages,
        temperature=0.8
    )
    return resp.choices[0].message.content.strip()

def extract_insights(user_text: str, reply: str) -> list[str]:
    prompt = (
        f"From this exchange:\nUser: {user_text}\nSophie: {reply}\n"
        "List 1–3 concise facts or takeaways Sophie should remember long-term. "
        "Answer as a JSON array of strings."
    )
    resp = oa.chat.completions.create(
        model=settings.gpt_model,
        messages=[
            {"role":"system","content":"You extract memory insights."},
            {"role":"user","content":prompt}
        ],
        temperature=0.0
    )
    return json.loads(resp.choices[0].message.content)
