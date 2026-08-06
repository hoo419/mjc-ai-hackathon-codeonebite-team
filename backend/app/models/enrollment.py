from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EnrollmentModel(Base):
    """Backing store for POST/DELETE /enrollment. Not directly part of
    API_CONTRACT.md (that only defines the request/response shapes)."""

    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id"))
    course_id: Mapped[str] = mapped_column(String, ForeignKey("courses.id"))
    status: Mapped[str] = mapped_column(String)
    enrolled_at: Mapped[str] = mapped_column(String)
