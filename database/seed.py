"""Script de seed — cria o usuário administrador padrão se não existir."""

import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database.connection import SessionLocal
from services.auth_service import AuthService
from repositories.usuario_repository import UsuarioRepository


def seed_admin():
    """Cria o usuário administrador padrão se ainda não existir."""
    db = SessionLocal()
    try:
        repo = UsuarioRepository()
        auth = AuthService()

        admin = repo.get_by_login(db, "admin")
        if admin is None:
            auth.create_user(
                db=db,
                nome="Administrador",
                login="admin",
                password="admin123",
                tipo="ADMIN"
            )
            print("[SEED] Usuário administrador criado com sucesso.")
            print("       Login: admin")
            print("       Senha: admin123")
        else:
            print("[SEED] Usuário administrador já existe. Nenhuma ação necessária.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
