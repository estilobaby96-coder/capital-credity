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
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    return templates.TemplateResponse("clientes.html", {"request": request})

@router.get("/emprestimos", response_class=HTMLResponse)
def emprestimos_page(request: Request):
    return templates.TemplateResponse("emprestimos.html", {"request": request})

@router.get("/recebimentos", response_class=HTMLResponse)
def recebimentos_page(request: Request):
    return templates.TemplateResponse("recebimentos.html", {"request": request})

@router.get("/relatorios", response_class=HTMLResponse)
def relatorios_page(request: Request):
    return templates.TemplateResponse("relatorios.html", {"request": request})
