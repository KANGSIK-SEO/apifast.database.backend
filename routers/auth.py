from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_optional_user
from database import get_db
from main_templates import templates
from services import auth_service


router = APIRouter(tags=["authentication"])


@router.get("/login", response_class=HTMLResponse, name="login")
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if user:
        return RedirectResponse(url="/projects/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"user": None, "error": None},
    )


@router.post("/login", response_class=HTMLResponse, name="login_submit")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate(db, email, password)
    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"user": None, "error": "이메일 또는 비밀번호를 확인해 주세요."},
            status_code=401,
        )
    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/projects/", status_code=303)


@router.post("/logout", name="logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
