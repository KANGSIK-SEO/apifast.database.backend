from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Task
from repositories import project_repository, task_repository


def create_task(
    db: Session,
    owner_id: int,
    project_id: int,
    title: str,
    description: str,
) -> Task:
    project = project_repository.get_for_owner(db, project_id, owner_id)
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    clean_title = title.strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="할 일 제목을 입력해 주세요.")
    return task_repository.create(db, project.id, clean_title, description.strip())


def toggle_task_status(
    db: Session,
    owner_id: int,
    project_id: int,
    task_id: int,
) -> Task:
    task = task_repository.get_for_owner(db, task_id, owner_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")
    next_status = "completed" if task.status == "in_progress" else "in_progress"
    return task_repository.update_status(db, task, next_status)
