from openai import OpenAI
from app.core.settings import OPENAI_API_KEY

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client
