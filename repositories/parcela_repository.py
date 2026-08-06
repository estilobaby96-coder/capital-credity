"""Repositório de Parcelas."""

from typing import List
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.parcela import Parcela


class ParcelaRepository(BaseRepository[Parcela]):
    def __init__(self):
        super().__init__(Parcela)

    def get_by_emprestimo(self, db: Session, emprestimo_id: int) -> List[Parcela]:
        """Retorna as parcelas de um empréstimo específico, ordenadas pelo número."""
        return db.query(Parcela).filter(
            Parcela.emprestimo_id == emprestimo_id
        ).order_by(Parcela.numero).all()
