from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class StudentModel(Base):
    """Mirrors API_CONTRACT.md section 6 - GET /students/me."""

    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    department: Mapped[str] = mapped_column(String)
    grade: Mapped[int] = mapped_column(Integer)
    semester: Mapped[int] = mapped_column(Integer)
