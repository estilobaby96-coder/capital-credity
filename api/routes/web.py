from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@router.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    return templates.TemplateResponse(request, "clientes.html")

@router.get("/emprestimos", response_class=HTMLResponse)
def emprestimos_page(request: Request):
    return templates.TemplateResponse(request, "emprestimos.html")

@router.get("/recebimentos", response_class=HTMLResponse)
def recebimentos_page(request: Request):
    return templates.TemplateResponse(request, "recebimentos.html")

@router.get("/relatorios", response_class=HTMLResponse)
def relatorios_page(request: Request):
    return templates.TemplateResponse(request, "relatorios.html")

@router.get("/politica", response_class=HTMLResponse)
def politica_page(request: Request):
    return templates.TemplateResponse(request, "politica.html")
