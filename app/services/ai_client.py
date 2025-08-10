import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

_client = OpenAI(api_key=OPENAI_API_KEY)

def get_client() -> OpenAI:
    return _client

def get_default_model() -> str:
    return OPENAI_MODEL
