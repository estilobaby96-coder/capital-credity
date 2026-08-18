"""Serviço de Empréstimos — Core financeiro."""

from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.emprestimo import Emprestimo
from repositories.emprestimo_repository import EmprestimoRepository
from repositories.parcela_repository import ParcelaRepository


class EmprestimoService:
    def __init__(self):
        self.emprestimo_repo = EmprestimoRepository()
        self.parcela_repo = ParcelaRepository()

    def simulate_installments(self, valor_principal: float, taxa_juros_percentual: float,
                              data_vencimento: date) -> List[Dict[str, Any]]:
        taxa = taxa_juros_percentual / 100.0
        
        juros = round(valor_principal * taxa, 2)
        valor_total = round(valor_principal + juros, 2)

        parcelas = [{
            "numero": 1,
            "data_vencimento": data_vencimento,
            "capital": valor_principal,
            "juros": juros,
            "valor_atualizado": valor_total,
        }]

        return parcelas

    def create_loan(self, db: Session, cliente_id: int, valor_solicitado: float, 
                    taxa_juros: float, data_vencimento: date, 
                    tipo_garantia: str = "SEM_GARANTIA",
                    garantia_desc: str = "", promissoria_status: str = "NAO_EXIGIDA",
                    fiador: str = "", observacoes: str = "") -> Emprestimo:
        
        # ── 1. Validações de Segurança e Score ──────────────────
        from services.cliente_service import ClienteService
        cliente_service = ClienteService()
        metrics = cliente_service.get_cliente_metrics(db, cliente_id)

        # Validação 1: Bloqueio de Inadimplente
        if metrics["has_inadimplencia"]:
            qtd = metrics["qtd_parcelas_atrasadas"]
            raise ValueError(
                f"OPERACAO BLOQUEADA! O cliente possui {qtd} parcela(s) em ATRASO.\n"
                f"Regularize as pendências anteriores antes de conceder um novo empréstimo."
            )

        # Validação 2: Limite do Nível (Score) - REMOVIDO a pedido do usuário
        # if valor_solicitado > metrics["limite_disponivel"]:
        #     lim_fmt = f"R$ {metrics['limite_disponivel']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        #     max_fmt = f"R$ {metrics['limite_max']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        #     sol_fmt = f"R$ {valor_solicitado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        #     nivel = metrics['nivel']
        #     raise ValueError(
        #         f"LIMITE EXCEDIDO! Cliente nível '{nivel}' possui limite máximo de {max_fmt}.\n"
        #         f"Saldo limite disponível para novo empréstimo: {lim_fmt}.\n"
        #         f"Valor solicitado: {sol_fmt}."
        #     )

        parcelas_simuladas = self.simulate_installments(valor_solicitado, taxa_juros, data_vencimento)

        # Gerar número do contrato sequencial (001/2026)
        numero_contrato = self.emprestimo_repo.gerar_numero_contrato(db)

        emprestimo_data = {
            "cliente_id": cliente_id,
            "numero_contrato": numero_contrato,
            "valor_emprestado": valor_solicitado,
            "valor_liberado": valor_solicitado,
            "taxa_juros": taxa_juros,
            "data_vencimento": data_vencimento,
            "tipo_garantia": tipo_garantia,
            "garantia": garantia_desc,
            "promissoria_status": promissoria_status,
            "fiador": fiador,
            "observacoes": observacoes,
            "status": "ATIVO"
        }

        emprestimo = self.emprestimo_repo.create(db, emprestimo_data)

        for p in parcelas_simuladas:
            parcela_data = {
                "emprestimo_id": emprestimo.id,
                "numero": p["numero"],
                "data_vencimento": p["data_vencimento"],
                "capital": p["capital"],
                "juros": p["juros"],
                "valor_atualizado": p["valor_atualizado"],
                "status": "A VENCER"
            }
            self.parcela_repo.create(db, parcela_data)
            
        return emprestimo

    def get_all(self, db: Session) -> List[Emprestimo]:
        return self.emprestimo_repo.get_all_with_cliente(db)

    def get_by_id(self, db: Session, emprestimo_id: int) -> Emprestimo:
        return db.query(Emprestimo).filter(Emprestimo.id == emprestimo_id).first()

    def update_loan(self, db: Session, emprestimo_id: int, valor: float, taxa_juros: float, data_vencimento: date) -> Emprestimo:
        """Atualiza valor, taxa de juros e data de vencimento de um empréstimo e recalcula a parcela."""
        emprestimo = self.get_by_id(db, emprestimo_id)
        if not emprestimo:
            raise ValueError("Empréstimo não encontrado.")
        if emprestimo.status not in ("ATIVO",):
            raise ValueError(f"Não é possível editar um empréstimo com status '{emprestimo.status}'.")

        emprestimo.valor_emprestado = valor
        emprestimo.valor_liberado = valor
        emprestimo.taxa_juros = taxa_juros
        emprestimo.data_vencimento = data_vencimento

        # Recalcula a parcela (se ainda estiver A VENCER)
        for p in emprestimo.parcelas:
            if p.status == "A VENCER":
                juros = round(valor * (taxa_juros / 100.0), 2)
                p.capital = valor
                p.juros = juros
                p.valor_atualizado = round(valor + juros, 2)
                p.data_vencimento = data_vencimento

        db.commit()
        db.refresh(emprestimo)
        return emprestimo

    def cancel_loan(self, db: Session, emprestimo_id: int) -> Emprestimo:
        """Cancela um empréstimo apagando-o definitivamente do sistema."""
        emprestimo = self.get_by_id(db, emprestimo_id)
        if not emprestimo:
            raise ValueError("Empréstimo não encontrado.")
        if emprestimo.status not in ("ATIVO", "CANCELADO"):
            raise ValueError(f"Não é possível cancelar um empréstimo com status '{emprestimo.status}'.")

        class CanceladoReturn:
            id = emprestimo.id
            numero_contrato = emprestimo.numero_contrato
            status = "DELETADO"

        ret = CanceladoReturn()
        
        db.delete(emprestimo)
        db.commit()
        
        return ret
