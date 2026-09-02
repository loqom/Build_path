from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    TAVILY_API_KEY: str
    GROQ_API_KEY: str = ""
    NODE_CALLBACK_URL: str = "http://localhost:5000/api/pipeline/callback"
    INTERNAL_API_KEY: str = "buildpath-internal-key-2026"
    CHROMA_DB_PATH: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()