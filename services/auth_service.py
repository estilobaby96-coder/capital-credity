"""Serviço de Autenticação — hash de senhas com bcrypt e verificação de credenciais."""

from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from repositories.usuario_repository import UsuarioRepository
from models.usuario import Usuario


class AuthService:
    """Gerencia autenticação: hash de senha, verificação e login."""

    def __init__(self):
        self.usuario_repo = UsuarioRepository()

    @staticmethod
    def hash_password(password: str) -> str:
        """Gera o hash bcrypt de uma senha em texto plano."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica se a senha em texto plano corresponde ao hash armazenado."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def authenticate(self, db: Session, login: str, password: str) -> Optional[Usuario]:
        """
        Tenta autenticar um usuário.
        Retorna o objeto Usuario se as credenciais forem válidas, ou None.
        """
        user = self.usuario_repo.get_by_login(db, login)
        if user is None:
            return None
        if not user.ativo:
            return None
        if not self.verify_password(password, user.senha_hash):
            return None
        return user

    def create_user(self, db: Session, nome: str, login: str, password: str, tipo: str = "FUNCIONARIO") -> Usuario:
        """Cria um novo usuário com a senha já criptografada."""
        senha_hash = self.hash_password(password)
        user_data = {
            "nome": nome,
            "login": login,
            "senha_hash": senha_hash,
            "tipo": tipo,
            "ativo": True,
        }
        return self.usuario_repo.create(db, user_data)
