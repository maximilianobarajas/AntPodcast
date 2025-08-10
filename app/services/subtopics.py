import json
from typing import List, Union, Dict, Any

from app.services.ai_client import get_client, get_default_model
from app.templates.prompts import get_subtopic_prompt

def get_subtopics(main_topic: str = "", num: int = 0) -> Union[List[str], Dict[str, Any]]:
    if not main_topic or not isinstance(num, int) or num <= 0:
        return {"msg": "Not a valid request"}

    client = get_client()
    model = get_default_model() or "gpt-4o-mini"

    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful writing assistant."},
                {"role": "user", "content": get_subtopic_prompt(main_topic=main_topic, num=num)},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        subtopics = data.get("subtopics", [])
        # Ensure we return a list of strings, trimmed, deduped, at most `num`
        clean = []
        seen = set()
        for s in subtopics:
            if not isinstance(s, str):
                continue
            t = s.strip()
            if t and t.lower() not in seen:
                seen.add(t.lower())
                clean.append(t)
            if len(clean) >= num:
                break
        return clean
    except Exception as e:
        # Return a friendly error payload instead of throwing
        return {"msg": f"Failed to generate subtopics: {e.__class__.__name__}"}
