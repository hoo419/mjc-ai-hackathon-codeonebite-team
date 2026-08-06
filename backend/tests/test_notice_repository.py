from datetime import timedelta

from app.core.time import KST
from app.repositories import notice_repository
from app.schemas.notice import Notice
import datetime as datetime_module


def _notice(id_: str) -> Notice:
    return Notice(
        id=id_,
        title=f"title-{id_}",
        category="ACADEMIC",
        publishedAt="2026-08-06T00:00:00+09:00",
        url=f"https://www.mjc.ac.kr/bbs/data/view.do?data_idx={id_}",
    )


def test_list_notices_fetches_when_cache_is_empty(monkeypatch):
    notice_repository.reset()
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: [_notice("1")])

    result = notice_repository.list_notices()

    assert result == [_notice("1")]


def test_list_notices_reuses_cache_within_ttl(monkeypatch):
    notice_repository.reset()
    calls = {"count": 0}

    def fake_fetch(limit=4):
        calls["count"] += 1
        return [_notice(str(calls["count"]))]

    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", fake_fetch)

    first = notice_repository.list_notices()
    second = notice_repository.list_notices()

    assert calls["count"] == 1
    assert first == second == [_notice("1")]


def test_list_notices_refetches_after_ttl_expires(monkeypatch):
    notice_repository.reset()
    calls = {"count": 0}

    def fake_fetch(limit=4):
        calls["count"] += 1
        return [_notice(str(calls["count"]))]

    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", fake_fetch)

    notice_repository.list_notices()
    # 캐시 타임스탬프를 6시간보다 더 과거로 돌려서 만료 상태를 시뮬레이션.
    notice_repository._cache_fetched_at = datetime_module.datetime.now(KST) - timedelta(hours=7)

    notice_repository.list_notices()

    assert calls["count"] == 2


def test_list_notices_keeps_stale_cache_when_refetch_fails(monkeypatch):
    notice_repository.reset()
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: [_notice("good")])
    notice_repository.list_notices()
    notice_repository._cache_fetched_at = datetime_module.datetime.now(KST) - timedelta(hours=7)

    # 다음 새로고침 시도는 실패(빈 리스트) - 그래도 예전 캐시를 계속 보여준다.
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: [])

    result = notice_repository.list_notices()

    assert result == [_notice("good")]


def test_list_notices_returns_empty_when_never_fetched_and_fetch_fails(monkeypatch):
    notice_repository.reset()
    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", lambda limit=4: [])

    assert notice_repository.list_notices() == []


def test_reset_clears_cache_so_next_call_refetches(monkeypatch):
    notice_repository.reset()
    calls = {"count": 0}

    def fake_fetch(limit=4):
        calls["count"] += 1
        return [_notice(str(calls["count"]))]

    monkeypatch.setattr(notice_repository.mjc_notices, "fetch_recent_notices", fake_fetch)

    notice_repository.list_notices()
    notice_repository.reset()
    notice_repository.list_notices()

    assert calls["count"] == 2
