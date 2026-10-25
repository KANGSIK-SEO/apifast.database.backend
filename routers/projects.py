from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from main_templates import templates
from models import User
from services import project_service, task_service


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_class=HTMLResponse, name="project_list")
def project_list(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="projects/list.html",
        context={"user": user, "projects": project_service.list_projects(db, user.id)},
    )


@router.get("/new", response_class=HTMLResponse, name="project_create_form")
def project_create_form(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="projects/form.html",
        context={"user": user},
    )


@router.post("/", name="project_create")
def project_create(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.create_project(db, user.id, name, description)
    return RedirectResponse(url=f"/projects/{project.id}", status_code=303)


@router.get("/{project_id}", response_class=HTMLResponse, name="project_detail")
def project_detail(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.get_project(db, project_id, user.id)
    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={"user": user, "project": project},
    )


@router.post("/{project_id}/tasks", name="task_create")
def task_create(
    project_id: int,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task_service.create_task(db, user.id, project_id, title, description)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/{project_id}/tasks/{task_id}/toggle", name="task_toggle")
def task_toggle(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project_service.get_project(db, project_id, user.id)
    task_service.toggle_task_status(db, user.id, project_id, task_id)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
