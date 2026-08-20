from repositories.base_repository import BaseRepository
from models.garantia import Garantia
from sqlalchemy.orm import Session
from typing import List


class GarantiaRepository(BaseRepository[Garantia]):
    def __init__(self):
        super().__init__(Garantia)

    def get_by_emprestimo(self, db: Session, emprestimo_id: int) -> List[Garantia]:
        """Retorna todas as garantias de um empréstimo específico."""
        return db.query(Garantia).filter(Garantia.emprestimo_id == emprestimo_id).all()
