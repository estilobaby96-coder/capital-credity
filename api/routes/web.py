from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()

import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")
templates = Jinja2Templates(directory=templates_dir)

CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate"
}

@router.get("/manifest.json")
def manifest():
    return FileResponse(os.path.join(static_dir, "manifest.json"))

@router.get("/service-worker.js")
def service_worker():
    return FileResponse(os.path.join(static_dir, "service-worker.js"))

@router.get("/.well-known/assetlinks.json")
def assetlinks():
    return [
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "com.capitalcredity.oficialapp",
                "sha256_cert_fingerprints": [
                    "ED:EC:EB:E4:FA:9A:90:92:FA:B4:13:78:CD:82:58:08:24:01:58:91:68:9D:7F:39:B0:51:EE:99:F2:41:AB:E3"
                ]
            }
        }
    ]

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", headers=CACHE_HEADERS)

@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", headers=CACHE_HEADERS)

@router.get("/clientes", response_class=HTMLResponse)
def clientes_page(request: Request):
    return templates.TemplateResponse(request, "clientes.html", headers=CACHE_HEADERS)

@router.get("/emprestimos", response_class=HTMLResponse)
def emprestimos_page(request: Request):
    return templates.TemplateResponse(request, "emprestimos.html", headers=CACHE_HEADERS)

@router.get("/recebimentos", response_class=HTMLResponse)
def recebimentos_page(request: Request):
    return templates.TemplateResponse(request, "recebimentos.html", headers=CACHE_HEADERS)

@router.get("/relatorios", response_class=HTMLResponse)
def relatorios_page(request: Request):
    return templates.TemplateResponse(request, "relatorios.html", headers=CACHE_HEADERS)
