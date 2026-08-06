from datetime import datetime, timedelta

from app.core.time import KST
from app.rag import mjc_notices
from app.schemas.notice import Notice

# 6시간마다 학사공지 게시판을 다시 긁어온다. app.core.notice_scheduler가
# 백그라운드에서 이 간격으로 refresh_now()를 실제로 호출한다(요청 트래픽과
# 무관하게 진짜 6시간마다). 아래 CACHE_TTL/list_notices()의 lazy 새로고침은
# 그 스케줄러가 아직 한 번도 못 돌았거나(방금 기동) 죽었을 때를 위한
# 안전망일 뿐이다.
CACHE_TTL = timedelta(hours=6)

_cache: list[Notice] | None = None
_cache_fetched_at: datetime | None = None


def _is_stale() -> bool:
    return _cache_fetched_at is None or datetime.now(KST) - _cache_fetched_at > CACHE_TTL


def _refresh() -> None:
    global _cache, _cache_fetched_at
    fresh = mjc_notices.fetch_recent_notices()
    if fresh:
        _cache = fresh
        _cache_fetched_at = datetime.now(KST)
    # fresh가 빈 리스트면(네트워크 실패 등) 새로고침 자체를 하지 않은 것으로
    # 치고, 기존 캐시(있다면 오래된 것이라도)를 계속 쓴다 - 학교 사이트가
    # 잠깐 안 열린다고 화면을 텅 비우지 않는다.


def list_notices() -> list[Notice]:
    if _is_stale():
        _refresh()
    return _cache or []


def refresh_now() -> None:
    """캐시가 신선하든 말든 무조건 다시 긁어온다. app.core.notice_scheduler의
    백그라운드 루프가 6시간마다 이 함수를 호출한다."""
    _refresh()


def reset() -> None:
    """Mock 저장소들과 동일한 패턴: 테스트 사이에 캐시가 새지 않도록."""
    global _cache, _cache_fetched_at
    _cache = None
    _cache_fetched_at = None
