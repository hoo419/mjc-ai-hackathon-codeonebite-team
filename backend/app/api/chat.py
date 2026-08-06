import logging

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def post_chat(payload: ChatRequest) -> ChatResponse:
    try:
        return chat_service.handle_message(payload.message)
    except Exception:
        # AI_AGENT_RULES.md 실패 처리: 원인은 서버 로그에만 남기고, 사용자에게는
        # traceback 대신 안정적인 응답을 돌려준다.
        logger.exception("chat handling failed for message=%r", payload.message)
        return ChatResponse(
            answer="일시적인 오류로 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."
        )
