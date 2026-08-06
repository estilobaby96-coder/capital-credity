"""Repositório de Usuários — acesso a dados da tabela 'usuarios'."""

from typing import Optional
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.usuario import Usuario


class UsuarioRepository(BaseRepository[Usuario]):
    """Repositório especializado para operações com Usuários."""

    def __init__(self):
        super().__init__(Usuario)

    def get_by_login(self, db: Session, login: str) -> Optional[Usuario]:
        """Busca um usuário pelo login."""
        return db.query(Usuario).filter(Usuario.login == login).first()

    def get_ativos(self, db: Session) -> list[Usuario]:
        """Retorna todos os usuários ativos."""
        return db.query(Usuario).filter(Usuario.ativo == True).all()
