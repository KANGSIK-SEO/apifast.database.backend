from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Project
from repositories import project_repository


def list_projects(db: Session, owner_id: int) -> list[Project]:
    return project_repository.list_for_owner(db, owner_id)


def get_project(db: Session, project_id: int, owner_id: int) -> Project:
    project = project_repository.get_for_owner(db, project_id, owner_id)
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


def create_project(db: Session, owner_id: int, name: str, description: str) -> Project:
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="프로젝트 이름을 입력해 주세요.")
    return project_repository.create(db, owner_id, clean_name, description.strip())
