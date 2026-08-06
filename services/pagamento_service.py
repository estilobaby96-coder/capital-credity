"""Serviço de Pagamentos — Core transacional de baixas com rolagem."""

from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from models.parcela import Parcela
from models.emprestimo import Emprestimo
from models.recebimento import Recebimento
from models.movimentacao import Movimentacao
from repositories.parcela_repository import ParcelaRepository
from repositories.recebimento_repository import RecebimentoRepository
from repositories.movimentacao_repository import MovimentacaoRepository
from repositories.emprestimo_repository import EmprestimoRepository


class PagamentoService:
    def __init__(self):
        self.parcela_repo = ParcelaRepository()
        self.recebimento_repo = RecebimentoRepository()
        self.mov_repo = MovimentacaoRepository()
        self.emprestimo_repo = EmprestimoRepository()

    def get_parcelas_pendentes_by_cliente(self, db: Session, cliente_id: int) -> List[Parcela]:
        """Busca todas as parcelas pendentes de todos os empréstimos ativos de um cliente."""
        emprestimos = self.emprestimo_repo.get_by_cliente(db, cliente_id)
        pendentes = []
        for emp in emprestimos:
            if emp.status == "ATIVO":
                parcelas = db.query(Parcela).options(
                    joinedload(Parcela.emprestimo)
                ).filter(Parcela.emprestimo_id == emp.id).all()
                pendentes.extend([p for p in parcelas if p.status in ("PENDENTE", "A VENCER", "ATRASADA")])
        return sorted(pendentes, key=lambda x: x.data_vencimento)

    def registrar_pagamento(self, db: Session, parcela_id: int, valor_pago: float, 
                            metodo_pagamento: str, observacao: str = "",
                            taxa_servico: float = 0.0) -> dict:
        """
        Realiza a baixa da parcela com lógica de rolagem e taxa de serviço.
        """
        parcela = self.parcela_repo.get(db, parcela_id)
        if not parcela or parcela.status == "PAGA":
            raise ValueError("Parcela não encontrada ou já está paga.")

        tolerancia = 0.01
        valor_total_parcela = parcela.capital + parcela.juros  # Valor cheio original

        # ── Determinar tipo de pagamento ──────────────────────────
        if valor_pago >= (parcela.valor_atualizado - tolerancia):
            # PAGAMENTO INTEGRAL
            tipo_pagamento = "INTEGRAL"
            self.parcela_repo.update(db, parcela, {
                "status": "PAGA",
                "valor_atualizado": 0.0,
                "data_pagamento": date.today()
            })
            resultado_msg = "Empréstimo quitado integralmente."

        elif abs(valor_pago - parcela.juros) <= tolerancia:
            # ROLAGEM — pagou só os juros
            tipo_pagamento = "JUROS (ROLAGEM)"
            
            # A parcela volta ao valor cheio (capital + juros) e rola 1 mês
            nova_data = parcela.data_vencimento + relativedelta(months=1)
            self.parcela_repo.update(db, parcela, {
                "status": "A VENCER",
                "valor_atualizado": valor_total_parcela,
                "data_vencimento": nova_data
            })

            msg_taxa = f" (+ R$ {taxa_servico:.2f} Taxa de Servico)" if taxa_servico > 0 else ""
            resultado_msg = (
                f"Juros pagos{msg_taxa}! Empréstimo renovado para {nova_data.strftime('%d/%m/%Y')}."
            )

        else:
            # REGRA ESTRITA: Sem abatimentos parciais
            raise ValueError(
                f"Pagamento inválido! O sistema não permite abatimentos parciais.\n"
                f"Você deve pagar ou o valor exato dos JUROS (R$ {parcela.juros:.2f}) para renovar, "
                f"ou o TOTAL (R$ {parcela.valor_atualizado:.2f}) para quitar."
            )

        # ── Gerar Recebimento ──────────────────────────────────────
        valor_total_recebido = valor_pago + taxa_servico
        obs_full = f"{observacao} (Taxa Servico: R$ {taxa_servico:.2f})".strip() if taxa_servico > 0 else observacao
        
        rec_data = {
            "parcela_id": parcela.id,
            "data_pagamento": date.today(),
            "valor_pago": valor_total_recebido,
            "tipo_pagamento": tipo_pagamento,
            "forma_pagamento": metodo_pagamento,
            "observacoes": obs_full
        }
        recebimento = self.recebimento_repo.create(db, rec_data)

        # ── Gerar Movimentação (Caixa) ─────────────────────────────
        mov_data = {
            "tipo": "ENTRADA",
            "valor": valor_total_recebido,
            "data": date.today(),
            "descricao": f"Recebimento {tipo_pagamento} Parcela {parcela.numero} - Contrato {parcela.emprestimo.numero_contrato if parcela.emprestimo and parcela.emprestimo.numero_contrato else parcela.emprestimo_id}",
            "forma_pagamento": metodo_pagamento,
            "recebimento_id": recebimento.id
        }
        self.mov_repo.create(db, mov_data)

        # ── Verificar se quitou o empréstimo ───────────────────────
        todas_parcelas = self.parcela_repo.get_by_emprestimo(db, parcela.emprestimo_id)
        if all(p.status == "PAGA" for p in todas_parcelas):
            emprestimo_obj = self.emprestimo_repo.get(db, parcela.emprestimo_id)
            if emprestimo_obj:
                self.emprestimo_repo.update(db, emprestimo_obj, {"status": "QUITADO"})

        return {
            "tipo": tipo_pagamento,
            "mensagem": resultado_msg
        }
