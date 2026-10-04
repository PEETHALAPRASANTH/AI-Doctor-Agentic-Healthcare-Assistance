from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./doctor.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_agent_steps: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
