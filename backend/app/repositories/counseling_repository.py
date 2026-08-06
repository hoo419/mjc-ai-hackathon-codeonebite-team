import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.core.time import KST
from app.schemas.counseling import CounselingRequestPayload, CounselingSummaryResponse

# Submitted counseling requests aren't part of any GET response in
# API_CONTRACT.md yet, but keeping them in memory (like enrollment) means a
# future admin/listing endpoint or DB table can reuse this without changing
# the POST endpoint's behavior.
_requests: list[dict] = []


@lru_cache
def _load_summaries(data_dir: Path) -> list[dict]:
    path = data_dir / "counseling.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_summary_for_student(student_id: str) -> CounselingSummaryResponse | None:
    for item in _load_summaries(settings.data_dir):
        if item["studentId"] == student_id:
            return CounselingSummaryResponse.model_validate(item)
    return None


def add_request(student_id: str, payload: CounselingRequestPayload) -> str:
    request_id = f"counsel-req-{len(_requests) + 1:03d}"
    _requests.append(
        {
            "requestId": request_id,
            "studentId": student_id,
            "targetType": payload.targetType,
            "message": payload.message,
            "requestedAt": datetime.now(KST).isoformat(),
        }
    )
    return request_id


def reset() -> None:
    """Used between tests so generated request IDs stay predictable."""
    global _requests
    _requests = []
