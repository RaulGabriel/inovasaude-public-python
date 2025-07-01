# app/routes/profile.py

from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.database import SessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/perfil",
    tags=["Perfil do Usuário"]
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    """
    Mostra a página de perfil com os dados do utilizador logado.
    """
    user_session = request.session.get("user")
    if not user_session:
        return RedirectResponse("/auth/login", status_code=302)

    user_db = db.query(User).filter(User.email == user_session.get("email")).first()
    if not user_db:
        request.session.clear()
        return RedirectResponse("/auth/login?error=user_not_found", status_code=302)

    return templates.TemplateResponse("perfil.html", {"request": request, "user": user_db})

@router.post("/", response_class=HTMLResponse)
def update_profile(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados do perfil do utilizador.
    """
    user_session = request.session.get("user")
    if not user_session:
        return RedirectResponse("/auth/login", status_code=302)

    user_db = db.query(User).filter(User.email == user_session.get("email")).first()
    if user_db:
        user_db.username = username
        db.commit()
        
        # Atualiza a sessão com o novo nome
        user_session["username"] = username
        request.session["user"] = user_session
        
        # Redireciona de volta para o perfil com uma mensagem de sucesso
        return RedirectResponse("/perfil?success=true", status_code=302)

    return RedirectResponse("/auth/login", status_code=302)
