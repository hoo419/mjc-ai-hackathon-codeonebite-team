from pydantic import BaseModel

from app.schemas.course import Course


class ChatRequest(BaseModel):
    message: str


class ChatSource(BaseModel):
    title: str
    url: str


class ChatAction(BaseModel):
    type: str
    label: str
    targetId: str


class ChatResponse(BaseModel):
    """Mirrors API_CONTRACT.md section 8. sources/courses/actions are
    optional from Frontend's point of view but always present here as
    (possibly empty) lists so Frontend never has to special-case missing
    keys."""

    answer: str
    sources: list[ChatSource] = []
    courses: list[Course] = []
    actions: list[ChatAction] = []
