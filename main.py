import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from auth.dependencies import LoginRequired, get_optional_user
from database import Base, SessionLocal, engine, get_db
from main_templates import templates
from models import Project, Task, User
from routers.auth import router as auth_router
from routers.projects import router as projects_router
from services.auth_service import seed_demo_accounts


Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_demo_accounts(db)

app = FastAPI(title="함께하는 할 일 보드")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "local-development-secret-change-me"),
    same_site="lax",
    https_only=os.getenv("COOKIE_HTTPS_ONLY", "false").lower() == "true",
)
app.include_router(auth_router)
app.include_router(projects_router)


@app.exception_handler(LoginRequired)
async def login_required(_request: Request, _exception: LoginRequired):
    return RedirectResponse(url="/login", status_code=303)


@app.exception_handler(404)
async def not_found(request: Request, _exception):
    with SessionLocal() as db:
        user = get_optional_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={"user": user},
        status_code=404,
    )


@app.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": user},
    )
