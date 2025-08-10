import json
import pytest

from app.templates import prompts
from app.services import subtopics as subtopics_service
from app.services import text_generation as tg

def test_prompts_shapes():
    s = prompts.system_instructions()
    assert isinstance(s, str) and len(s) > 10

    p1 = prompts.intro_prompt("Graphs", 80)
    assert "Graphs" in p1 and "~80" in p1

    p2 = prompts.subtopic_paragraph_prompt("txt", "sub", 50)
    assert "txt" in p2 and "sub" in p2 and "~50" in p2

    p3 = prompts.get_subtopic_prompt("AI", 5)
    assert '"subtopics"' in p3 and "AI" in p3 and "5" in p3

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Fake OpenAI calls used by both services
    class _Resp:
        def __init__(self, content):
            self.choices = [type("C", (), {"message": type("M", (), {"content": content})})]

    class _Chat:
        class _Completions:
            @staticmethod
            def create(**kwargs):
                wants_json = kwargs.get("response_format", {}).get("type") == "json_object"
                if wants_json:
                    return _Resp(json.dumps({"subtopics": ["One", "Two", "Two", "Three"]}))
                return _Resp("GEN_TEXT")

        completions = _Completions()

    class _Client:
        chat = _Chat()

    from app.services import ai_client
    monkeypatch.setattr(ai_client, "_client", _Client())
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

def test_generate_text_wrapper():
    out = tg.generate_text(user_prompt="Hello", system_prompt="Sys", max_words=20)
    assert out == "GEN_TEXT"

def test_get_subtopics_service_dedup_and_trim():
    out = subtopics_service.get_subtopics(main_topic="AI", num=3)
    # Deduped, limited to 3
    assert out == ["One", "Two", "Three"]

def test_get_subtopics_invalid():
    out = subtopics_service.get_subtopics(main_topic="", num=0)
    assert isinstance(out, dict) and out.get("msg")
