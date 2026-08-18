from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Capital Credity API", version="1.0.0")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://capital-credity.vercel.app",   # URL ativa até 19/08
        "https://www.capitalcredity.com.br",    # DNS liberado dia 19
        "https://capitalcredity.com.br",        # DNS liberado dia 19
        "http://localhost:8000",                # dev local
        "http://127.0.0.1:8000",               # dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota raiz removida para que o web.router (Jinja2) assuma o controle

from api.routes import clientes, emprestimos, pagamentos, dashboard, auth, web, relatorios
from fastapi.staticfiles import StaticFiles

# Servir os arquivos de imagem/ícones nativos do app como estáticos
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
assets_dir = os.path.join(BASE_DIR, "assets")
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(web.router) # Rotas das páginas HTML
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(emprestimos.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(relatorios.router)
