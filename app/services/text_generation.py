# app/services/text_generation.py
from app.services.ai_client import get_client, get_default_model  # ✅ keep this
# ❌ REMOVE: from app.services.text_generation import generate_text

def generate_text(
    user_prompt: str,
    system_prompt: str = "You are a helpful writing assistant.",
    max_words: int = 150,
    temperature: float = 0.7,
) -> str:
    client = get_client()
    model = get_default_model()

    max_tokens = max(64, int(max_words * 2))  # heuristic

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",    "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()
