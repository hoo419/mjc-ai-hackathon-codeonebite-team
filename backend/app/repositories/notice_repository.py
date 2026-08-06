import json
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.schemas.notice import Notice


@lru_cache
def _load_raw(data_dir: Path) -> list[dict]:
    path = data_dir / "notices.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def list_notices() -> list[Notice]:
    return [Notice.model_validate(item) for item in _load_raw(settings.data_dir)]
