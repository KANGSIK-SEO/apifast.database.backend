from fastapi import Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User
from repositories import user_repository


class LoginRequired(Exception):
    pass


def get_optional_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        request.session.clear()
    return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    user = get_optional_user(request, db)
    if user is None:
        raise LoginRequired
    return user
