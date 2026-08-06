"""Ponto de entrada exclusivo para rodar o Servidor Web do Capital Credity."""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente antes de tudo
load_dotenv()

import uvicorn
from database.base import Base
from database.connection import engine
from database.seed import seed_admin

def main():
    print("Iniciando o Servidor Web do Capital Credity...")
    
    # Garantir que as tabelas existam
    Base.metadata.create_all(bind=engine)
    
    # Seed: criar admin padrão se não existir
    seed_admin()

    print("=========================================================")
    print("Servidor rodando! Acesse: http://localhost:8000")
    print("Para desligar o site, feche esta janela.")
    print("=========================================================")
    
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
