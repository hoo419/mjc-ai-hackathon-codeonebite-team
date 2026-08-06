from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CourseModel(Base):
    """Mirrors the Course object in API_CONTRACT.md section 4. sessions/
    eligible_depts are stored as JSON-serialized text (Neon supports JSONB,
    but plain String keeps the Mock/DB code paths symmetric - the
    repository layer is the only place that (de)serializes)."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    professor: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)
    class_type: Mapped[str | None] = mapped_column(String, nullable=True)
    sessions_json: Mapped[str] = mapped_column(String)
    target_grade: Mapped[int] = mapped_column(Integer)
    eligible_depts_json: Mapped[str] = mapped_column(String)
    capacity: Mapped[int] = mapped_column(Integer)
    enrolled: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    last_updated: Mapped[str] = mapped_column(String)
