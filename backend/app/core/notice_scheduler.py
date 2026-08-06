import asyncio
import logging

from app.repositories import notice_repository

logger = logging.getLogger(__name__)

REFRESH_INTERVAL_SECONDS = 6 * 60 * 60  # 6시간


async def _tick() -> None:
    """한 번 새로고침 시도. notice_repository.refresh_now()가 동기(httpx.Client)
    함수라 asyncio.to_thread로 돌려서 이벤트 루프를 막지 않는다 - 안 그러면
    학교 사이트가 느릴 때(리스트+상세 4건, 최대 25초 가까이) 그 사이 다른
    모든 API 요청이 멈춰버린다."""
    try:
        await asyncio.to_thread(notice_repository.refresh_now)
    except Exception:
        logger.exception("background notice refresh failed")


async def run_notice_refresh_loop(interval_seconds: float = REFRESH_INTERVAL_SECONDS) -> None:
    """앱이 켜져 있는 동안 계속 도는 백그라운드 루프. 기동하자마자 한 번
    새로고침하고(캐시를 바로 채움), 그 뒤로는 interval_seconds마다 반복.
    이게 진짜 "6시간마다" 새로고침을 보장한다 - notice_repository.list_notices()의
    lazy 새로고침은 요청이 없으면 6시간이 넘어도 안 도는 안전망일 뿐이다."""
    while True:
        await _tick()
        await asyncio.sleep(interval_seconds)
