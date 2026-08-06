"""Ponto de entrada principal do Capital Credity."""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente antes de tudo
load_dotenv()

import threading
import uvicorn
from database.base import Base
from database.connection import engine
from models.usuario import Usuario
from models.cliente import Cliente
from models.emprestimo import Emprestimo
from models.parcela import Parcela
from models.recebimento import Recebimento
from models.renegociacao import Renegociacao
from models.movimentacao import Movimentacao
from database.seed import seed_admin
from utils.theme import apply_theme
from views.app import App


def run_web_server():
    """Roda o servidor web (FastAPI) em uma porta fixa."""
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, log_level="error")

def main():
    """Inicializa o sistema: tema, banco de dados, login, interface principal e web server."""
    app_name = os.getenv("APP_NAME", "Capital Credity")
    print(f"Iniciando {app_name}...")

    # Garantir que as tabelas existam
    Base.metadata.create_all(bind=engine)

    # Seed: criar admin padrão se não existir
    seed_admin()

    # Inicializar o tema
    apply_theme()


    # Iniciar a aplicação com a tela de login
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
