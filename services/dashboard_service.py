"""Serviço de Dashboard — Consultas agregadas para métricas financeiras."""

from datetime import date, datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func, and_

from models.emprestimo import Emprestimo
from models.parcela import Parcela
from models.cliente import Cliente
from models.movimentacao import Movimentacao
from services.pagamento_service import PagamentoService

class DashboardService:

    def get_metrics(self, db: Session) -> Dict[str, Any]:
        """Retorna todas as métricas para o Dashboard em uma única chamada."""
        # Garante que os status de atraso estão atualizados para hoje
        PagamentoService().atualizar_todas_parcelas_pendentes(db)
        
        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        
        # --- Contadores Gerais ---
        total_clientes = db.query(sa_func.count(Cliente.id)).scalar() or 0
        total_emprestimos_ativos = db.query(sa_func.count(Emprestimo.id)).filter(
            Emprestimo.status == "ATIVO"
        ).scalar() or 0
        total_emprestimos_quitados = db.query(sa_func.count(Emprestimo.id)).filter(
            Emprestimo.status == "QUITADO"
        ).scalar() or 0

        # --- Capital Emprestado (Total Liberado ATIVO) ---
        capital_emprestado = db.query(sa_func.sum(Emprestimo.valor_emprestado)).filter(
            Emprestimo.status == "ATIVO"
        ).scalar() or 0.0

        # --- Parcelas (A Vencer / Atrasadas / Pagas) ---
        parcelas_a_vencer = db.query(sa_func.count(Parcela.id)).filter(
            Parcela.status == "A VENCER"
        ).scalar() or 0
        
        parcelas_atrasadas = db.query(sa_func.count(Parcela.id)).filter(
            Parcela.status == "ATRASADA"
        ).scalar() or 0

        # --- Valor A Receber (parcelas pendentes) ---
        valor_a_receber = db.query(sa_func.sum(Parcela.valor_atualizado)).filter(
            Parcela.status.in_(["A VENCER", "ATRASADA"])
        ).scalar() or 0.0

        # --- Valor Recebido no Mês (Movimentações de Entrada no mês atual) ---
        valor_recebido_mes = db.query(sa_func.sum(Movimentacao.valor)).filter(
            and_(
                Movimentacao.tipo == "ENTRADA",
                Movimentacao.data >= primeiro_dia_mes
            )
        ).scalar() or 0.0

        # --- Valor Recebido Hoje ---
        inicio_hoje = datetime.combine(hoje, datetime.min.time())
        fim_hoje = datetime.combine(hoje, datetime.max.time())
        valor_recebido_hoje = db.query(sa_func.sum(Movimentacao.valor)).filter(
            and_(
                Movimentacao.tipo == "ENTRADA",
                Movimentacao.data >= inicio_hoje,
                Movimentacao.data <= fim_hoje
            )
        ).scalar() or 0.0

        return {
            "total_clientes": total_clientes,
            "emprestimos_ativos": total_emprestimos_ativos,
            "emprestimos_quitados": total_emprestimos_quitados,
            "capital_emprestado": capital_emprestado,
            "parcelas_a_vencer": parcelas_a_vencer,
            "parcelas_atrasadas": parcelas_atrasadas,
            "valor_a_receber": valor_a_receber,
            "valor_recebido_mes": valor_recebido_mes,
            "valor_recebido_hoje": valor_recebido_hoje,
        }

    def get_proximas_parcelas(self, db: Session, limite: int = 10) -> List[Parcela]:
        """Retorna as próximas parcelas a vencer (para a tabela do Dashboard)."""
        # Garante que os status de atraso estão atualizados para hoje
        PagamentoService().atualizar_todas_parcelas_pendentes(db)
        
        return db.query(Parcela).options(
            joinedload(Parcela.emprestimo).joinedload(Emprestimo.cliente)
        ).filter(
            Parcela.status.in_(["A VENCER", "ATRASADA"])
        ).order_by(Parcela.data_vencimento).limit(limite).all()
