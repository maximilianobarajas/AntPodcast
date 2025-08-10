def system_podcast_host() -> str:
    return (
        "You are a veteran podcast producer and host. "
        "You restructure provided material into a compelling, broadcast-ready script. "
        "Write spoken language (not academic prose). Use short sentences, clear transitions, and signposting."
    )

def restructure_to_podcast_prompt(
    source_text: str,
    title: str | None,
    target_minutes: int,
    segments: int,
    tone: str,
    host_name: str | None,
) -> str:
    t = title or "Untitled Episode"
    host = host_name or "Host"
    return (
        f"Task: Restructure the material into a podcast script for '{t}'.\n\n"
        "CONSTRAINTS:\n"
        f"- Target duration: ~{target_minutes} minutes.\n"
        f"- Number of segments: {segments} (Intro, {segments-2} body segments, Outro DO NOT WRITE INTRO, SEGMENT OR OUTRO IN THE SCRIPT, MAKE IT SEEM AS HUMAN AS POSSIBLE).\n"
        f"- Tone: {tone}.\n"
        "- Style: conversational, engaging; avoid jargon and long sentences.\n"
        "- Include natural transitions and brief teasers before each segment.\n"
        "- Avoid filler like 'um'/'uh'.\n\n"
        "FORMAT:\n"
        "Return plain text ready to be read aloud by a host.\n"
    )
