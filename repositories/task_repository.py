from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Task


def get_for_owner(db: Session, task_id: int, owner_id: int) -> Task | None:
    statement = (
        select(Task)
        .where(Task.id == task_id, Task.project.has(owner_id=owner_id))
        .options(selectinload(Task.project))
    )
    return db.scalar(statement)


def create(db: Session, project_id: int, title: str, description: str) -> Task:
    task = Task(project_id=project_id, title=title, description=description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_status(db: Session, task: Task, status: str) -> Task:
    task.status = status
    db.commit()
    db.refresh(task)
    return task
