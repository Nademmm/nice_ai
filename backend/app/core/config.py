from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Niscahya AI Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./niscahya.db"

    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    LLM_PROVIDER: str = "gemini"

    class Config:
        env_file = ".env"


settings = Settings()
