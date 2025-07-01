from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/planos", response_class=HTMLResponse)
def planos(request: Request):
    return templates.TemplateResponse("planos.html", {"request": request})

@router.get("/contato", response_class=HTMLResponse)
def contato(request: Request):
    return templates.TemplateResponse("contato.html", {"request": request})