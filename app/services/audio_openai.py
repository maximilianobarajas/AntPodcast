import os
import uuid
from app.services.ai_client import get_client

# Default output directory (git-ignored if you added media/ to .gitignore)
PODCAST_OUT_DIR = os.getenv("PODCAST_OUT_DIR", "media/podcasts")
DEFAULT_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")  # official TTS model
DEFAULT_VOICE = os.getenv("OPENAI_TTS_VOICE", "onyx")  # try: alloy|echo|fable|onyx|nova|shimmer

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def text_to_mp3_openai(
    text: str,
    voice: str = DEFAULT_VOICE,
    filename: str | None = None,
    model: str = DEFAULT_TTS_MODEL,
) -> str:
    """
    Renders `text` into an MP3 using OpenAI TTS and returns the absolute file path.

    Uses Audio->Speech API via streaming, per OpenAI docs (Python). 
    """
    ensure_dir(PODCAST_OUT_DIR)
    name = filename or f"{uuid.uuid4().hex}.mp3"
    out_path = os.path.join(PODCAST_OUT_DIR, name)

    client = get_client()
    # OpenAI docs show `with_streaming_response.create(...).stream_to_file(...)` for TTS. :contentReference[oaicite:0]{index=0}
    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=text,
    ) as response:
        response.stream_to_file(out_path)

    return out_path
