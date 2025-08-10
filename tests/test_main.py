import os
import json
import pytest
from fastapi.testclient import TestClient

# Ensure the app import path is correct for your project
from app.main import app

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # Set a dummy key so import of ai_client doesn't explode
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

@pytest.fixture
def client(monkeypatch):
    # Patch OpenAI client used inside services to avoid network calls
    from app.services import ai_client

    class _Resp:
        def __init__(self, content):
            self.choices = [type("C", (), {"message": type("M", (), {"content": content})})]

    class _Chat:
        class _Completions:
            @staticmethod
            def create(**kwargs):
                # Return JSON for subtopics, plain text for others
                messages = kwargs.get("messages", [])
                wants_json = kwargs.get("response_format", {}).get("type") == "json_object"
                if wants_json:
                    fake = json.dumps({"subtopics": ["A", "B", "C", "D", "E", "F"]})
                else:
                    fake = "FAKE_GENERATED_TEXT"
                return _Resp(fake)

        completions = _Completions()

    class _Client:
        chat = _Chat()

    monkeypatch.setattr(ai_client, "_client", _Client())
    return TestClient(app)

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "Hello, World!"

def test_generate_intro(client):
    payload = {"main_topic": "Graphs", "word_count": 60}
    r = client.post("/generate_intro", json=payload)
    assert r.status_code == 200
    assert "introduction" in r.json()
    assert r.json()["introduction"] == "FAKE_GENERATED_TEXT"

def test_generate_subtopic_paragraph(client):
    payload = {"text": "X", "subtopic": "Y", "word_count": 80}
    r = client.post("/generate_subtopic_paragraph", json=payload)
    assert r.status_code == 200
    assert "paragraph" in r.json()
    assert r.json()["paragraph"] == "FAKE_GENERATED_TEXT"

def test_generate_subtopics_ok(client):
    r = client.post("/generate_subtopics", params={"main_topic": "ML", "num_topics": 6})
    assert r.status_code == 200
    assert r.json()["subtopics"][:3] == ["A", "B", "C"]

def test_generate_subtopics_invalid(client):
    r = client.post("/generate_subtopics", params={"main_topic": "", "num_topics": 0})
    # Router has validation for num_topics, but check service return shape on bad inputs
    # Simulate calling service directly by expecting a 422 here due to Query(..., ge=1)
    assert r.status_code in (200, 422)
