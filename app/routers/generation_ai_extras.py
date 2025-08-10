# app/routers/generation_ai_extras.py  (or add into your existing generation router)

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.text_generation import generate_text

router = APIRouter()

class Step(BaseModel):
    id: Optional[str] = None
    title: str
    notes: str = ""

class FlashcardsReq(BaseModel):
    topic: str = ""
    steps: List[Step] = []
    num_cards: int = 20

class MindmapReq(BaseModel):
    topic: str
    steps: List[Step] = []

@router.post("/generate_flashcards")
def generate_flashcards(req: FlashcardsReq) -> Dict[str, Any]:
    topic = (req.topic or "").strip()
    notes_blob = "\n\n".join(
        f"- {s.title}: {s.notes}" if s.notes else f"- {s.title}"
        for s in req.steps if (s.title or s.notes)
    )
    user_prompt = f"""
Create flashcards as JSON. Use this structure only:

{{
  "cards": [{{"q": "Question text", "a": "Answer text"}}, ...]
}}

Rules:
- 1-2 sentences per answer.
- Prioritize fundamentals.
- Avoid duplicates and trivia.
- Return EXACT JSON (no backticks, no prose).
- Max {req.num_cards} cards.

Topic: {topic or "(none)"}
Notes:
{notes_blob if notes_blob else "(no extra notes)"}
""".strip()

    raw = generate_text(user_prompt=user_prompt,
                        system_prompt="You are a precise study assistant. Return strict JSON.",
                        max_words=400)
    import json
    try:
        data = json.loads(raw)
        cards = data.get("cards", [])
        # sanitize
        out = []
        seen = set()
        for c in cards:
            q = str(c.get("q") or c.get("question") or "").strip()
            a = str(c.get("a") or c.get("answer") or "").strip()
            if not q: continue
            key = (q.lower(), a.lower())
            if key in seen: continue
            seen.add(key)
            out.append({"q": q, "a": a})
            if len(out) >= req.num_cards: break
        return {"cards": out}
    except Exception as e:
        return {"msg": f"Failed to parse flashcards: {e.__class__.__name__}"}

@router.post("/generate_mindmap")
def generate_mindmap(req: MindmapReq) -> Dict[str, Any]:
    topic = (req.topic or "").strip() or "Topic"
    notes_blob = "\n".join(
        f"- {s.title}: {s.notes}" if s.notes else f"- {s.title}"
        for s in req.steps if (s.title or s.notes)
    )
    user_prompt = f"""
Return a mind map as JSON with exactly this shape:

{{
  "nodes": [
    {{"id":"center","label":"{topic}","type":"center"}},
    {{"id":"sub-1","label":"...", "type":"subtopic"}},
    {{"id":"c-1","label":"...", "type":"concept", "parent":"sub-1"}}
  ],
  "edges": [{{"from":"center","to":"sub-1"}}, {{"from":"sub-1","to":"c-1"}}]
}}

Guidelines:
- 6–10 subtopics max.
- 0–3 concept nodes per subtopic (optional).
- IDs must be simple and unique (kebab-case ok).
- Always include the center node with id "center".
- Use information from Topic and Notes. If notes absent, infer common, useful subtopics.
- Return STRICT JSON (no backticks, no extra text).

Topic: {topic}
Notes:
{notes_blob if notes_blob else "(no notes)"}    
""".strip()

    raw = generate_text(user_prompt=user_prompt,
                        system_prompt="You are a structured mapping assistant. Return strict JSON.",
                        max_words=450)
    import json
    try:
        data = json.loads(raw)
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        # minimal sanity
        if not any(n.get("type") == "center" for n in nodes):
            nodes.insert(0, {"id":"center","label":topic,"type":"center"})
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        return {"msg": f"Failed to parse mindmap: {e.__class__.__name__}"}
