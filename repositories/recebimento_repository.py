"""Repositório de Recebimentos."""

from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.recebimento import Recebimento


class RecebimentoRepository(BaseRepository[Recebimento]):
    def __init__(self):
        super().__init__(Recebimento)

    def get_by_parcela(self, db: Session, parcela_id: int) -> Recebimento:
        """Busca o recebimento associado a uma parcela específica."""
        return db.query(Recebimento).filter(Recebimento.parcela_id == parcela_id).first()
