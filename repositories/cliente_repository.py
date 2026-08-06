"""Repositório de Clientes."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from repositories.base_repository import BaseRepository
from models.cliente import Cliente


class ClienteRepository(BaseRepository[Cliente]):
    """Repositório especializado para operações com Clientes."""

    def __init__(self):
        super().__init__(Cliente)

    def get_by_cpf(self, db: Session, cpf: str) -> Optional[Cliente]:
        """Busca um cliente pelo CPF exato."""
        return db.query(Cliente).filter(Cliente.cpf == cpf).first()

    def search(self, db: Session, term: str) -> List[Cliente]:
        """Busca clientes por nome, cpf, email ou telefone que contenham o termo."""
        search_term = f"%{term}%"
        return db.query(Cliente).filter(
            or_(
                Cliente.nome.ilike(search_term),
                Cliente.cpf.ilike(search_term),
                Cliente.email.ilike(search_term),
                Cliente.telefone.ilike(search_term)
            )
        ).all()
