from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CourseModel(Base):
    """Mirrors the Course object in API_CONTRACT.md section 4. Column
    names are snake_case (Python/DB convention); the repository layer maps
    them back to the camelCase Course pydantic schema."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    professor: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)
    class_type: Mapped[str] = mapped_column(String)
    day: Mapped[str] = mapped_column(String)
    start_time: Mapped[str] = mapped_column(String)
    end_time: Mapped[str] = mapped_column(String)
    building: Mapped[str | None] = mapped_column(String, nullable=True)
    room: Mapped[str | None] = mapped_column(String, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer)
    enrolled: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    last_updated: Mapped[str] = mapped_column(String)
