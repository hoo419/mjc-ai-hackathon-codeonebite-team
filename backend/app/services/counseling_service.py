import json

from app.repositories import counseling_repository
from app.schemas.counseling import (
    AptitudeAnalysisResponse,
    CounselingRequestPayload,
    CounselingRequestResponse,
    CounselingRequestStatus,
    CounselingSummaryResponse,
)
from app.services import ai_client, student_service

_APTITUDE_SYSTEM_PROMPT = (
    "너는 명지전문대학교 학생의 진로적성/핵심역량/종합심리검사 결과를 정리하는 "
    "도우미다. 사용자가 보내는 원문 텍스트 안의 내용만 사용해서 분석하라. "
    "원문에 없는 내용은 절대 추측하거나 지어내지 마라. 다른 설명 없이 정확히 "
    '이 JSON 형식으로만 답하라: {"summary": "한 문단 요약", '
    '"insights": ["인사이트1", "인사이트2"]}'
)


def get_current_student_summary() -> CounselingSummaryResponse | None:
    student = student_service.get_current_student()
    return counseling_repository.get_summary_for_student(student.id)


def _parse_aptitude_response(text: str) -> AptitudeAnalysisResponse:
    try:
        data = json.loads(text)
        summary = str(data.get("summary", "")).strip()
        insights = [str(i).strip() for i in data.get("insights", []) if str(i).strip()]
        if summary:
            return AptitudeAnalysisResponse(summary=summary, insights=insights)
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    # AI didn't return valid JSON - fall back to its raw reply as the
    # summary rather than failing outright. Still 100% derived from the
    # provided rawText, nothing fabricated.
    return AptitudeAnalysisResponse(summary=text.strip(), insights=[])


def analyze_aptitude(raw_text: str) -> AptitudeAnalysisResponse | None:
    """Returns None when there's nothing to analyze or the AI provider is
    unavailable/fails - the caller returns ANALYSIS_UNAVAILABLE rather than
    fabricating a career/personality analysis (AI_AGENT_RULES.md)."""
    if not raw_text.strip():
        return None

    client = ai_client.get_client()
    if client is None:
        return None

    generated = client.generate(system=_APTITUDE_SYSTEM_PROMPT, user=raw_text)
    if generated is None:
        return None

    return _parse_aptitude_response(generated)


def submit_request(payload: CounselingRequestPayload) -> CounselingRequestResponse:
    """Mock 상담 요청 접수. 실제 라우팅/담당자 배정은 아직 없고, 요청을
    받았다는 것만 확인해준다."""
    student = student_service.get_current_student()
    request_id = counseling_repository.add_request(student.id, payload)
    return CounselingRequestResponse(
        success=True,
        requestId=request_id,
        status=CounselingRequestStatus.REQUESTED,
    )
