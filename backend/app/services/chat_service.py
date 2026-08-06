from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.core.time import KST
from app.rag import school_info
from app.schemas.chat import ChatAction, ChatResponse
from app.schemas.course import Course, CourseCategory, CourseClassType
from app.schemas.student import ScheduleItem
from app.services import ai_client, course_service, student_service

# 확인할 데이터가 없을 때 쓰는 고정 문구. AI_AGENT_RULES.md: 데이터가 없으면
# 이렇게 말하고, 학교 규정을 지어내지 않는다. AI가 다듬지 못하게 별도 취급한다.
NO_DATA_ANSWER = "현재 연결된 데이터에서 확인할 수 없습니다."

# Phase 7: AI는 이미 계산된 사실 문장의 "말투"만 다듬는다. 새 정보를 절대
# 추가하지 않도록 시스템 프롬프트에서 명시적으로 못박는다 (AI_AGENT_RULES.md -
# LLM은 학교 데이터의 Source of Truth가 아니다).
_REPHRASE_SYSTEM_PROMPT = (
    "너는 명지전문대학교 AI 캠퍼스 비서다. 사용자가 보내는 안내문에 담긴 사실"
    "(숫자, 이름, 시간, 상태 등)은 절대 바꾸거나 더하지 말고, 같은 의미를 유지"
    "하면서 학생에게 자연스럽고 친절한 한국어 말투로만 한 문단으로 다듬어라."
)


def _rephrase(answer: str) -> str:
    client = ai_client.get_client()
    if client is None:
        return answer
    rephrased = client.generate(system=_REPHRASE_SYSTEM_PROMPT, user=answer)
    return rephrased or answer

DAY_ORDER = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


class ChatIntent(StrEnum):
    AVAILABLE_COURSES = "AVAILABLE_COURSES"
    SEARCH_COURSES = "SEARCH_COURSES"
    SCHEDULE_TODAY = "SCHEDULE_TODAY"
    NEXT_CLASS = "NEXT_CLASS"
    SCHOOL_INFO = "SCHOOL_INFO"


@dataclass
class CourseFilters:
    class_types: set[CourseClassType | None] = field(default_factory=set)
    categories: set[CourseCategory] = field(default_factory=set)

    def is_empty(self) -> bool:
        return not self.class_types and not self.categories


def extract_course_filters(message: str) -> CourseFilters:
    """Very small rule-based keyword extractor. 실데이터엔 classType이
    OFFLINE 또는 None(원격, 실시간/녹화 구분 불가)만 존재하므로 "온라인"
    관련 언급은 전부 None으로 모은다 - 실시간/녹화를 구분해서 답하면
    근거 없이 지어내는 것이라 그렇게 하지 않는다."""
    filters = CourseFilters()

    if "온라인" in message:
        filters.class_types.add(None)
    if "오프라인" in message:
        filters.class_types.add(CourseClassType.OFFLINE)
    if "하이브리드" in message or "혼합" in message:
        filters.class_types.add(CourseClassType.HYBRID)

    if "전공" in message:
        filters.categories.add(CourseCategory.MAJOR_COURSE)
    if "교양" in message:
        wants_required = "필수" in message
        wants_elective = "선택" in message
        if wants_required:
            filters.categories.add(CourseCategory.GENERAL_REQUIRED)
        if wants_elective:
            filters.categories.add(CourseCategory.GENERAL_ELECTIVE)
        if not wants_required and not wants_elective:
            filters.categories.update(
                {
                    CourseCategory.GENERAL_COURSE,
                    CourseCategory.GENERAL_REQUIRED,
                    CourseCategory.GENERAL_ELECTIVE,
                }
            )

    return filters


def classify_intent(message: str, filters: CourseFilters) -> ChatIntent:
    if any(k in message for k in ("다음 수업", "다음 강의", "다음 시간표")):
        return ChatIntent.NEXT_CLASS
    if any(k in message for k in ("오늘 수업", "오늘 뭐", "오늘 시간표", "오늘 몇 시")):
        return ChatIntent.SCHEDULE_TODAY
    if any(k in message for k in ("신청 가능", "신청가능", "지금 신청")):
        return ChatIntent.AVAILABLE_COURSES
    if not filters.is_empty():
        return ChatIntent.SEARCH_COURSES
    return ChatIntent.SCHOOL_INFO


def _matches_filters(course: Course, filters: CourseFilters) -> bool:
    if filters.class_types and course.classType not in filters.class_types:
        return False
    if filters.categories and course.category not in filters.categories:
        return False
    return True


def _course_actions(courses: list[Course]) -> list[ChatAction]:
    return [
        ChatAction(type="VIEW_COURSE", label="과목 보기", targetId=course.id)
        for course in courses
    ]


def _handle_course_search(filters: CourseFilters, require_available: bool) -> ChatResponse:
    all_courses = course_service.search_courses()
    courses = [c for c in all_courses if _matches_filters(c, filters)]
    if require_available:
        courses = [
            c
            for c in courses
            if c.status.value == "OPEN" and course_service.remaining_seats(c) > 0
        ]

    if not courses:
        return ChatResponse(answer="조건에 맞는 과목을 찾지 못했습니다.")

    answer = f"조건에 맞는 과목을 {len(courses)}건 찾았습니다."
    return ChatResponse(answer=answer, courses=courses, actions=_course_actions(courses))


def _today_schedule(schedule: list[ScheduleItem], today: str) -> list[ScheduleItem]:
    return sorted((s for s in schedule if s.day == today), key=lambda s: s.startTime)


def _find_next_class(
    schedule: list[ScheduleItem], today_index: int, now_time: str
) -> ScheduleItem | None:
    rotated_days = DAY_ORDER[today_index:] + DAY_ORDER[:today_index]
    for offset, day in enumerate(rotated_days):
        day_items = sorted((s for s in schedule if s.day == day), key=lambda s: s.startTime)
        for item in day_items:
            if offset == 0 and item.startTime <= now_time:
                continue  # already started or finished today
            return item
    return None


def _handle_schedule_today(now: datetime) -> ChatResponse:
    today = DAY_ORDER[now.weekday()]
    schedule = student_service.get_current_student_schedule()
    todays_items = _today_schedule(schedule, today)

    if not todays_items:
        return ChatResponse(answer="오늘은 등록된 수업이 없습니다.")

    lines = [
        f"{item.name} ({item.startTime}~{item.endTime}, {item.building or '온라인'} {item.room or ''})".strip()
        for item in todays_items
    ]
    answer = "오늘 수업은 다음과 같습니다: " + ", ".join(lines)
    courses = [c for i in todays_items if (c := course_service.get_course_by_id(i.courseId))]
    return ChatResponse(answer=answer, courses=courses, actions=_course_actions(courses))


def _handle_next_class(now: datetime) -> ChatResponse:
    schedule = student_service.get_current_student_schedule()
    next_item = _find_next_class(schedule, now.weekday(), now.strftime("%H:%M"))

    if next_item is None:
        return ChatResponse(answer="예정된 다음 수업이 없습니다.")

    location = next_item.building or "온라인"
    room = f" {next_item.room}" if next_item.room else ""
    answer = (
        f"다음 수업은 {next_item.name} ({next_item.day} {next_item.startTime}~"
        f"{next_item.endTime}, {location}{room})입니다."
    )
    course = course_service.get_course_by_id(next_item.courseId)
    courses = [course] if course else []
    return ChatResponse(answer=answer, courses=courses, actions=_course_actions(courses))


def handle_message(message: str, now: datetime | None = None) -> ChatResponse:
    """Structured pipeline per AI_AGENT_RULES.md:
    message -> intent/parameter extraction -> service call -> answer text.
    No real school fact is invented here; every fact comes from
    course_service/student_service, which read Mock data (soon: DB)."""
    now = now or datetime.now(KST)
    filters = extract_course_filters(message)
    intent = classify_intent(message, filters)

    if intent == ChatIntent.AVAILABLE_COURSES:
        response = _handle_course_search(filters, require_available=True)
    elif intent == ChatIntent.SEARCH_COURSES:
        response = _handle_course_search(filters, require_available=False)
    elif intent == ChatIntent.SCHEDULE_TODAY:
        response = _handle_schedule_today(now)
    elif intent == ChatIntent.NEXT_CLASS:
        response = _handle_next_class(now)
    else:
        # SCHOOL_INFO: search the school site in real time and answer only
        # from what's actually found there (app/rag/school_info.py). This
        # path already produces a fact-constrained answer on its own, so it
        # skips the generic _rephrase() step below - and if nothing useful
        # was found, we fall back to the fixed safety sentence, never
        # fabricating a school-policy answer, and never letting the AI
        # rephrase that fixed sentence either.
        return school_info.answer(message, now=now) or ChatResponse(answer=NO_DATA_ANSWER)

    response.answer = _rephrase(response.answer)
    return response
