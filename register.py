# app/routes/register.py

# Imports nativos e de bibliotecas
import secrets
from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Imports locais da sua aplicação
from app.models.database import SessionLocal
from app.models.user import User
from app.utils.email import send_verification_email

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

# ---- Rota para exibir o formulário de cadastro ----
@router.get("/cadastro", response_class=HTMLResponse)
def register_form(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse("cadastro.html", {"request": request, "error": error})

# ---- Rota para processar o cadastro do usuário ----
@router.post("/cadastro", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != password_confirm:
        return RedirectResponse("/auth/cadastro?error=password_mismatch", status_code=302)

    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return RedirectResponse("/auth/cadastro?error=user_exists", status_code=302)

    hashed_password = pwd_context.hash(password)
    verification_token = secrets.token_urlsafe(32)

    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_active=False,
        verification_token=verification_token
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await send_verification_email(to_email=new_user.email, token=verification_token)

    return templates.TemplateResponse("verifique_email.html", {"request": request, "email": new_user.email})

# ---- Rota para verificar o e-mail do usuário (COM DEBUG) ----
@router.get("/verificar-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Recebe o token, imprime informações de debug e tenta ativar a conta."""

    # --- INÍCIO DO CÓDIGO DE DEBUG ---
    print("\n" + "="*50)
    print(f"DEBUG: Rota /verificar-email recebida com o token:")
    print(f"'{token}'")
    print("-" * 20)

    all_users = db.query(User).all()
    print("DEBUG: Tokens atualmente no banco de dados:")
    if not all_users:
        print("Nenhum usuário no banco de dados.")
    for u in all_users:
        print(f"  - User ID {u.id}, Token: '{u.verification_token}'")
    print("="*50 + "\n")
    # --- FIM DO CÓDIGO DE DEBUG ---

    user = db.query(User).filter(User.verification_token == token).first()

    if user and not user.is_active:
        print("SUCESSO: Token encontrado! Ativando usuário.")
        user.is_active = True
        user.verification_token = None
        db.commit()
        return RedirectResponse("/auth/login?verified=true", status_code=302)

    print("FALHA: Token não encontrado ou usuário já ativo. Redirecionando...")
    return RedirectResponse("/auth/login?error=invalid_token", status_code=302)

