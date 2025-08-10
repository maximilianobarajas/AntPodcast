from app.services.text_generation import generate_text
from app.templates.podcast_prompts import system_podcast_host, restructure_to_podcast_prompt

def build_podcast_script(
    source_text: str,
    title: str | None = None,
    target_minutes: int = 8,
    segments: int = 4,
    tone: str = "friendly and informative",
    host_name: str | None = None,
) -> str:
    prompt = restructure_to_podcast_prompt(
        source_text=source_text,
        title=title,
        target_minutes=target_minutes,
        segments=max(3, segments),
        tone=tone,
        host_name=host_name,
    )
    return generate_text(
        user_prompt=prompt,
        system_prompt=system_podcast_host(),
        max_words=target_minutes * 160  # ~160 wpm spoken
    )
