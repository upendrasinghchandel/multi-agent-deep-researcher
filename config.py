from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    OPENROUTER_MODEL_FAST: str = "meta-llama/llama-3.1-8b-instruct"
    OPENROUTER_MODEL_REASONING: str = "openai-gpt-4o"
    OPENROUTER_MODEL_WRITER: str = "meta-llama/llama-3.3-70b-instruct"
    OPENROUTER_EMBEDDING_MODEL: str = "text-embedding-3-small"

    MAX_RESEARCH_ITERATIONS: int = 2
    MAX_SEARCH_QUERIES: int = 6
    MAX_RESULTS_PER_QUERY: int = 5
    MAX_SOURCE_CONTENT_LENGTH: int = 8000
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()