# app/routes/dashboard.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/painel",
    tags=["Dashboard"]
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Verifica se o utilizador está logado e renderiza a página do painel.
    """
    # Procura pelo dicionário 'user' na sessão
    user_data = request.session.get("user")
    
    # Se não encontrar os dados do utilizador, redireciona para o login
    if not user_data:
        return RedirectResponse("/auth/login", status_code=302)
    
    # Se encontrar, passa o nome de utilizador para a página do painel
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user_data.get("username")})
