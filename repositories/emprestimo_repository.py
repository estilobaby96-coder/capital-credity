"""Repositório de Empréstimos."""

from datetime import date
from typing import List
from sqlalchemy.orm import Session, joinedload
from repositories.base_repository import BaseRepository
from models.emprestimo import Emprestimo


class EmprestimoRepository(BaseRepository[Emprestimo]):
    def __init__(self):
        super().__init__(Emprestimo)

    def gerar_numero_contrato(self, db: Session) -> str:
        """Gera o próximo número de contrato no formato 001/2026."""
        ano_atual = date.today().year
        sufixo = f"/{ano_atual}"
        
        # Busca o maior número de contrato deste ano
        ultimo = db.query(Emprestimo.numero_contrato).filter(
            Emprestimo.numero_contrato.like(f"%{sufixo}")
        ).order_by(Emprestimo.numero_contrato.desc()).first()
        
        if ultimo and ultimo[0]:
            try:
                seq = int(ultimo[0].split("/")[0]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        
        return f"{seq:03d}/{ano_atual}"

    def get_all_with_cliente(self, db: Session) -> List[Emprestimo]:
        """Retorna todos os empréstimos fazendo eager loading do cliente associado."""
        return db.query(Emprestimo).options(joinedload(Emprestimo.cliente)).all()

    def get_by_cliente(self, db: Session, cliente_id: int) -> List[Emprestimo]:
        """Retorna os empréstimos de um cliente específico."""
        return db.query(Emprestimo).filter(Emprestimo.cliente_id == cliente_id).all()
