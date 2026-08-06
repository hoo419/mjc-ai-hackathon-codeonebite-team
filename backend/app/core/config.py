from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> repo root is 3 levels up.
REPO_ROOT = Path(__file__).resolve().parents[3]

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Allowed CORS origins. Defaults to local Next.js dev only; in
    # production (Railway) set CORS_EXTRA_ORIGINS to the deployed Vercel
    # URL (comma-separated if there are several, e.g. preview deployments)
    # so the real frontend can call this API - the localhost defaults stay
    # in the list too, harmless in prod, useful for testing against a
    # deployed backend from a local frontend.
    cors_extra_origins: str = ""

    @property
    def cors_origins(self) -> list[str]:
        extra = [o.strip() for o in self.cors_extra_origins.split(",") if o.strip()]
        return _DEFAULT_CORS_ORIGINS + extra

    # Directory containing Mock JSON data (data/*.json), shared at repo root
    # so it can later be swapped for a database-backed repository.
    data_dir: Path = REPO_ROOT / "data"

    # OpenAI-compatible AI provider settings (used from Phase 6 onward).
    ai_api_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model: str | None = None

    # Phase 9: PostgreSQL. When unset, repositories fall back to the Mock
    # JSON files in data/ so the app keeps working without a database
    # (demo resilience if the DB is ever unreachable).
    database_url: str | None = None


settings = Settings()
