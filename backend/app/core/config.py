from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> repo root is 3 levels up.
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Allowed CORS origins for local Next.js development.
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Directory containing Mock JSON data (data/*.json), shared at repo root
    # so it can later be swapped for a database-backed repository.
    data_dir: Path = REPO_ROOT / "data"

    # OpenAI-compatible AI provider settings (used from Phase 6 onward).
    ai_api_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model: str | None = None


settings = Settings()
