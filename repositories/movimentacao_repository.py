"""Repositório de Movimentações (Caixa)."""

from typing import List
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.movimentacao import Movimentacao


class MovimentacaoRepository(BaseRepository[Movimentacao]):
    def __init__(self):
        super().__init__(Movimentacao)

    def get_entradas(self, db: Session) -> List[Movimentacao]:
        """Retorna todas as movimentações de entrada."""
        return db.query(Movimentacao).filter(Movimentacao.tipo == "ENTRADA").all()
