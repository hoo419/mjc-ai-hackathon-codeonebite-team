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

app = FastAPI(title="MJC AI Campus Agent API")

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
