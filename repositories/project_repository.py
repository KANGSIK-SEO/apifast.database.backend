from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Project


def list_for_owner(db: Session, owner_id: int) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .options(selectinload(Project.owner), selectinload(Project.tasks))
        .order_by(Project.id)
    )
    return list(db.scalars(statement))


def get_for_owner(db: Session, project_id: int, owner_id: int) -> Project | None:
    statement = (
        select(Project)
        .where(Project.id == project_id, Project.owner_id == owner_id)
        .options(selectinload(Project.owner), selectinload(Project.tasks))
    )
    return db.scalar(statement)


def create(db: Session, owner_id: int, name: str, description: str) -> Project:
    project = Project(owner_id=owner_id, name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
