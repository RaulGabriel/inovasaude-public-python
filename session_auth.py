# app/routes/session_auth.py

from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.database import SessionLocal
from app.models.user import User

# ---- Configuração de Segurança ----
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- Dependência para o Banco de Dados ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Configuração do Roteador ----
router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)
templates = Jinja2Templates(directory="app/templates")


# ---- Rota para exibir a página de login ----
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, verified: bool = False, error: Optional[str] = None):
    """Exibe a página de login e mensagens de feedback."""
    return templates.TemplateResponse("login.html", {"request": request, "verified": verified, "error": error})


# ---- Rota para processar a ação de login ----
@router.post("/login")
def login_action(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Processa o formulário de login, valida as credenciais e cria a sessão."""

    user = db.query(User).filter(User.email == email).first()

    # 1. Validação: O usuário existe?
    if not user:
        return RedirectResponse("/auth/login?error=invalid_credentials", status_code=302)

    # 2. Validação: A senha está correta?
    if not pwd_context.verify(password, user.hashed_password):
        return RedirectResponse("/auth/login?error=invalid_credentials", status_code=302)

    # 3. Validação: A conta está ativa?
    if not user.is_active:
        return RedirectResponse("/auth/login?error=not_verified", status_code=302)

    # 4. Sucesso: Armazena um dicionário do utilizador na sessão
    request.session["user"] = {
        "username": user.username,
        "email": user.email
    }
    
    # Redireciona para a URL correta do painel.
    return RedirectResponse("/painel/", status_code=302)


# ---- Rota para fazer logout ----
@router.get("/logout")
def logout(request: Request):
    """Limpa a sessão do usuário e o redireciona para a página inicial."""
    request.session.clear()
    return RedirectResponse("/", status_code=302)
