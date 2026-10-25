from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    owner: Mapped["User"] = relationship(back_populates="projects")
    # 프로젝트 삭제 시 소속 작업도 삭제하는 도메인 정책입니다.
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
