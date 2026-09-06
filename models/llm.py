import httpx
from langchain_openai import ChatOpenAI
from config import settings

def validate_openrouter_credentials(api_key: str) -> tuple[bool, str]:
    """Validates OpenRouter API key prior to pipeline execution."""
    if not api_key:
        return False, "OpenRouter API Key is empty."
    if not api_key.startswith("sk-or-"):
        return False, "Invalid format. OpenRouter keys start with 'sk-or-'."
    try:
        resp = httpx.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0
        )
        if resp.status_code == 200:
            return True, "Key verified successfully."
        return False, f"Auth verification failed (HTTP {resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Could not reach OpenRouter auth endpoint: {str(e)}"

def create_llm(model_name: str, temperature: float = 0.0) -> ChatOpenAI:
    """Centralized LLM factory routing calls through OpenRouter API."""
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set. Configure .env or provide via UI.")

    return ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
        temperature=temperature,
        max_retries=2,
        extra_body={"provider": {"allow_fallbacks": True}},
        default_headers={
            "HTTP-Referer": "https://localhost:8501",
            "X-Title": "Multi-Agent Deep Researcher",
        }
    )