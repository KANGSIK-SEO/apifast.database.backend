from sqlalchemy.orm import Session

from auth.passwords import hash_password, verify_password
from models import Project, User
from repositories import user_repository


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def seed_demo_accounts(db: Session) -> None:
    accounts = (
        ("alice@example.com", "앨리스", "alice1234", "앨리스의 프로젝트"),
        ("bob@example.com", "밥", "bob1234", "밥의 프로젝트"),
    )
    for email, name, password, project_name in accounts:
        user = user_repository.get_by_email(db, email)
        if user is None:
            user = user_repository.create(db, email, name, hash_password(password))
        if not user.projects:
            db.add(
                Project(
                    owner_id=user.id,
                    name=project_name,
                    description="할 일을 관리하는 예시 프로젝트입니다.",
                )
            )
    db.commit()
