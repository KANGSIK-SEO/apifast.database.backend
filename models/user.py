from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # 계정이 삭제되면 해당 사용자의 프로젝트와 작업도 함께 제거합니다.
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
