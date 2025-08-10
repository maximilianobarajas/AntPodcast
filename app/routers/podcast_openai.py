import os
from pydantic import BaseModel, Field
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.services.ai_client import get_client
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services.podcast_script import build_podcast_script
from app.services.audio_openai import text_to_mp3_openai, PODCAST_OUT_DIR

router = APIRouter(prefix="/podcast", tags=["podcast-openai"])

class BuildPodcastRequest(BaseModel):
    source_text: str = Field(..., description="Raw text to restructure as a podcast")
    title: str | None = Field(None, description="Episode title")
    target_minutes: int = Field(8, ge=3, le=60)
    segments: int = Field(4, ge=3, le=12)
    tone: str = Field("friendly and informative")
    host_name: str | None = None
    voice: str = Field("onyx", description="OpenAI TTS voice (e.g., alloy, echo, fable, onyx, nova, shimmer)")
    out_name: str | None = Field(None, description="Optional output filename (mp3)")

@router.post("/build-openai")
def build_podcast_openai(req: BuildPodcastRequest):
    script = build_podcast_script(
        source_text=req.source_text,
        title=req.title,
        target_minutes=req.target_minutes,
        segments=req.segments,
        tone=req.tone,
        host_name=req.host_name,
    )

    client = get_client()
    buf = BytesIO()
    # stream TTS into memory
    with client.audio.speech.with_streaming_response.create(
        model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        voice=req.voice,
        input=script,
    ) as resp:
        for chunk in resp.iter_bytes():  # pseudo-iter; use the iterator your client provides
            buf.write(chunk)

    buf.seek(0)
    # return as inline audio/mpeg
    return StreamingResponse(
        buf,
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="episode.mp3"'}
    )

@router.get("/file/{name}")
def get_podcast_file(name: str):
    path = os.path.join(PODCAST_OUT_DIR, name)
    return FileResponse(path, media_type="audio/mpeg", filename=name)
