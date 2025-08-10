from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.text_generation import generate_text
from app.services.subtopics import get_subtopics
from app.templates.prompts import (
    system_instructions,
    subtopic_paragraph_prompt,
    intro_prompt,
)

router = APIRouter()

class SubtopicRequest(BaseModel):
    text: str
    subtopic: str
    word_count: int

class IntroRequest(BaseModel):
    main_topic: str
    word_count: int

@router.post("/generate_subtopic_paragraph")
def generate_subtopic_paragraph(req: SubtopicRequest):
    prompt = subtopic_paragraph_prompt(req.text, req.subtopic, req.word_count)
    paragraph = generate_text(
        user_prompt=prompt,
        system_prompt=system_instructions(),
        max_words=req.word_count,
    )
    return {"paragraph": paragraph}

@router.post("/generate_intro")
def generate_intro(req: IntroRequest):
    prompt = intro_prompt(req.main_topic, req.word_count)
    introduction = generate_text(
        user_prompt=prompt,
        system_prompt=system_instructions(),
        max_words=req.word_count,
    )
    return {"introduction": introduction}

@router.post("/generate_subtopics")
def generate_subtopics(
    main_topic: str = Query(..., min_length=1),
    num_topics: int = Query(..., ge=1, le=50),
):
    """
    Returns either:
      - {"subtopics": [str, ...]} on success
      - {"msg": "..."} when invalid input or generation error occurs
    """
    result = get_subtopics(main_topic=main_topic, num=num_topics)
    return {"subtopics": result} if isinstance(result, list) else result
