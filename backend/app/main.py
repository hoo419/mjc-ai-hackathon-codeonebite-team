import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.campus import router as campus_router
from app.api.chat import router as chat_router
from app.api.counseling import router as counseling_router
from app.api.courses import router as courses_router
from app.api.enrollment import router as enrollment_router
from app.api.notices import router as notices_router
from app.api.students import router as students_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Phase 9: when DATABASE_URL is set, create tables and seed them from
    # data/*.json on first run. Without it, repositories fall back to
    # reading the Mock JSON files directly - no code above the repository
    # layer needs to know which one is active.
    if settings.database_url:
        from app.core import db, seed

        db.init_engine(settings.database_url)
        seed.seed_if_empty()

    # 학사공지를 6시간마다 백그라운드에서 새로고침 (notice_repository.py 참고).
    from app.core.notice_scheduler import run_notice_refresh_loop

    notice_task = asyncio.create_task(run_notice_refresh_loop())
    try:
        yield
    finally:
        # cancel()만 하고 끝내면 "Task was destroyed but it is pending!"
        # 경고가 뜰 수 있다(asyncio.run()이 알아서 정리해주는 러너에서는 안
        # 보이지만, 그건 이 코드가 아니라 그 러너 덕분이다) - 취소가 실제로
        # 처리될 때까지 기다려서 이 코드 스스로 안전하게 만든다.
        notice_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await notice_task


app = FastAPI(title="MJC AI Campus Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(enrollment_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(notices_router, prefix="/api")
app.include_router(counseling_router, prefix="/api")
app.include_router(campus_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
