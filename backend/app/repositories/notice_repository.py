from datetime import datetime, timedelta

from app.core.time import KST
from app.rag import mjc_notices
from app.schemas.notice import Notice

# 6시간마다 학사공지 게시판을 다시 긁어온다. 방문이 뜸하면 그보다 더 오래된
# 캐시를 계속 보여줄 수 있지만(요청이 들어올 때만 새로고침을 시도하는
# lazy-refresh 방식이라 백그라운드 스케줄러는 없음), 그게 아무도 안 보는데
# 미리 긁어두는 것보다 낫다.
CACHE_TTL = timedelta(hours=6)

_cache: list[Notice] | None = None
_cache_fetched_at: datetime | None = None


def _is_stale() -> bool:
    return _cache_fetched_at is None or datetime.now(KST) - _cache_fetched_at > CACHE_TTL


def list_notices() -> list[Notice]:
    global _cache, _cache_fetched_at
    if _is_stale():
        fresh = mjc_notices.fetch_recent_notices()
        if fresh:
            _cache = fresh
            _cache_fetched_at = datetime.now(KST)
        # fresh가 빈 리스트면(네트워크 실패 등) 새로고침 자체를 하지 않은
        # 것으로 치고, 기존 캐시(있다면 오래된 것이라도)를 계속 쓴다 - 학교
        # 사이트가 잠깐 안 열린다고 화면을 텅 비우지 않는다.

    return _cache or []


def reset() -> None:
    """Mock 저장소들과 동일한 패턴: 테스트 사이에 캐시가 새지 않도록."""
    global _cache, _cache_fetched_at
    _cache = None
    _cache_fetched_at = None
