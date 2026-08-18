"""Serviço de Relatórios — Consultas especializadas por tipo."""

from datetime import date, datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from models.emprestimo import Emprestimo
from models.parcela import Parcela
from models.cliente import Cliente
from models.movimentacao import Movimentacao
from services.pagamento_service import PagamentoService


class RelatorioService:

    # ------------------------------------------------------------------ #
    #  Extrato do Cliente                                                  #
    # ------------------------------------------------------------------ #
    def extrato_cliente(self, db: Session, cliente_id: int) -> Dict[str, Any]:
        """Retorna dados completos de um cliente: info pessoal + empréstimos + parcelas."""
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            return {"cliente": None, "emprestimos": []}

        emprestimos = db.query(Emprestimo).options(
            joinedload(Emprestimo.parcelas)
        ).filter(
            Emprestimo.cliente_id == cliente_id,
            Emprestimo.status != "CANCELADO"
        ).all()

        resultado = {
            "cliente": cliente,
            "emprestimos": []
        }

        for emp in emprestimos:
            parcelas_list = sorted(emp.parcelas, key=lambda p: p.numero)
            resultado["emprestimos"].append({
                "emprestimo": emp,
                "parcelas": parcelas_list
            })

        return resultado

    # ------------------------------------------------------------------ #
    #  Relatório de Inadimplência                                          #
    # ------------------------------------------------------------------ #
    def inadimplencia(self, db: Session) -> List[Dict[str, Any]]:
        """Retorna todas as parcelas atrasadas com dados do cliente e empréstimo."""
        PagamentoService().atualizar_todas_parcelas_pendentes(db)
        
        parcelas = db.query(Parcela).join(Emprestimo).options(
            joinedload(Parcela.emprestimo).joinedload(Emprestimo.cliente)
        ).filter(
            Parcela.status == "ATRASADA",
            Parcela.status != "CANCELADA",
            Emprestimo.status != "CANCELADO"
        ).order_by(Parcela.data_vencimento).all()

        rows = []
        for p in parcelas:
            nome = p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "—"
            cpf = p.emprestimo.cliente.cpf if p.emprestimo and p.emprestimo.cliente else "—"
            rows.append({
                "cliente": nome,
                "cpf": cpf,
                "emprestimo_id": p.emprestimo_id,
                "numero_contrato": p.emprestimo.numero_contrato if p.emprestimo and p.emprestimo.numero_contrato else f"#{p.emprestimo_id}",
                "parcela_num": p.numero,
                "vencimento": p.data_vencimento,
                "valor_original": p.capital + p.juros,
                "multa": p.multa or 0.0,
                "juros_mora": p.juros_mora or 0.0,
                "valor": p.valor_atualizado,
                "dias_atraso": p.dias_atraso or 0,
                "status": p.status,
            })
        return rows

    # ------------------------------------------------------------------ #
    #  Fluxo de Caixa                                                      #
    # ------------------------------------------------------------------ #
    def fluxo_caixa(self, db: Session, data_inicio: date, data_fim: date) -> List[Dict[str, Any]]:
        """Retorna movimentações no período informado, ordenadas por data."""
        inicio = datetime.combine(data_inicio, datetime.min.time())
        fim = datetime.combine(data_fim, datetime.max.time())

        movimentacoes = db.query(Movimentacao).filter(
            and_(
                Movimentacao.data >= inicio,
                Movimentacao.data <= fim
            )
        ).order_by(Movimentacao.data).all()

        rows = []
        saldo_acumulado = 0.0
        for m in movimentacoes:
            if m.tipo == "ENTRADA":
                saldo_acumulado += m.valor
            else:
                saldo_acumulado -= m.valor

            rows.append({
                "data": m.data,
                "tipo": m.tipo,
                "descricao": m.descricao or "—",
                "forma_pagamento": m.forma_pagamento or "—",
                "valor": m.valor,
                "saldo_acumulado": saldo_acumulado,
            })
        return rows

    # ------------------------------------------------------------------ #
    #  Controle Mensal Financeiro (Previsto vs. Realizado)                 #
    # ------------------------------------------------------------------ #
    def controle_mensal(self, db: Session, mes: int, ano: int) -> Dict[str, Any]:
        """
        Gera relatório mensal robusto comparando Previsto (o que tinha que entrar)
        com Realizado (o que efetivamente entrou no caixa).
        """
        import calendar
        from models.recebimento import Recebimento

        PagamentoService().atualizar_todas_parcelas_pendentes(db)

        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dt_ini = datetime(ano, mes, 1, 0, 0, 0)
        dt_fim = datetime(ano, mes, ultimo_dia, 23, 59, 59)

        # 1. Parcelas previstas para o mês
        parcelas_previstas = db.query(Parcela).join(Emprestimo).options(
            joinedload(Parcela.emprestimo).joinedload(Emprestimo.cliente)
        ).filter(
            and_(
                Parcela.data_vencimento >= dt_ini,
                Parcela.data_vencimento <= dt_fim,
                Parcela.status != "CANCELADA",
                Emprestimo.status != "CANCELADO"
            )
        ).order_by(Parcela.data_vencimento).all()

        total_previsto = sum(p.capital + p.juros for p in parcelas_previstas)
        total_juros_previsto = sum(p.juros for p in parcelas_previstas)
        total_capital_previsto = sum(p.capital for p in parcelas_previstas)

        # 2. Recebimentos realizados para essas parcelas
        parcela_ids = [p.id for p in parcelas_previstas]
        if parcela_ids:
            recebimentos_mes = db.query(Recebimento).options(
                joinedload(Recebimento.parcela).joinedload(Parcela.emprestimo).joinedload(Emprestimo.cliente)
            ).filter(
                Recebimento.parcela_id.in_(parcela_ids)
            ).all()
        else:
            recebimentos_mes = []

        total_realizado = sum(r.valor_pago for r in recebimentos_mes)

        # 3. Categorização dos Recebimentos & Lucro Bruto (Juros/Taxas)
        total_lucro_juros = 0.0
        for r in recebimentos_mes:
            if "JUROS" in (r.tipo_pagamento or ""):
                total_lucro_juros += r.valor_pago
            elif r.parcela:
                # Proporção dos juros no pagamento integral
                total_parc = r.parcela.capital + r.parcela.juros
                if total_parc > 0:
                    prop_juros = r.parcela.juros / total_parc
                    total_lucro_juros += (r.valor_pago * prop_juros)

        # 4. Inadimplência do Mês
        hoje = date.today()
        parcelas_inadimplentes = [
            p for p in parcelas_previstas 
            if p.status in ("ATRASADA", "PENDENTE", "A VENCER") and p.data_vencimento.date() < hoje
        ]
        total_inadimplencia = sum(p.valor_atualizado for p in parcelas_inadimplentes)

        # 5. Taxa de Eficiência (%)
        eficiencia = (total_realizado / total_previsto * 100.0) if total_previsto > 0 else (100.0 if total_realizado > 0 else 0.0)

        # 6. Montar Linhas Detalhadas da Tabela Comparativa
        rows = []
        for p in parcelas_previstas:
            cliente_nome = p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "—"
            num_contrato = p.emprestimo.numero_contrato if p.emprestimo and p.emprestimo.numero_contrato else f"#{p.emprestimo_id}"
            rec_relacionado = next((r for r in recebimentos_mes if r.parcela_id == p.id), None)
            
            val_previsto = p.capital + p.juros
            venc_str = p.data_vencimento.strftime("%d/%m/%Y")
            
            if rec_relacionado:
                dt_pgto_str = rec_relacionado.data_pagamento.strftime("%d/%m/%Y")
                val_pago = rec_relacionado.valor_pago
                tipo_pgto = rec_relacionado.tipo_pagamento or "INTEGRAL"
                st_desc = "🟢 PAGO NO PRAZO" if rec_relacionado.data_pagamento.date() <= p.data_vencimento.date() else "🟡 PAGO COM ATRASO"
                if "JUROS" in tipo_pgto:
                    st_desc = "🔄 ROLADO (JUROS)"
            else:
                dt_pgto_str = "—"
                val_pago = 0.0
                tipo_pgto = "—"
                if p.status == "ATRASADA" or p.data_vencimento.date() < hoje:
                    st_desc = "🔴 EM ATRASO"
                else:
                    st_desc = "⏳ A VENCER"

            rows.append({
                "cliente": cliente_nome,
                "numero_contrato": num_contrato,
                "emprestimo_id": p.emprestimo_id,
                "parcela_num": p.numero,
                "vencimento": venc_str,
                "valor_previsto": val_previsto,
                "data_pagamento": dt_pgto_str,
                "valor_pago": val_pago,
                "tipo_pagamento": tipo_pgto,
                "status_rotulo": st_desc
            })

        return {
            "mes": mes,
            "ano": ano,
            "total_previsto": total_previsto,
            "total_juros_previsto": total_juros_previsto,
            "total_capital_previsto": total_capital_previsto,
            "total_realizado": total_realizado,
            "total_inadimplencia": total_inadimplencia,
            "total_lucro_juros": round(total_lucro_juros, 2),
            "eficiencia_percentual": round(eficiencia, 1),
            "rows": rows
        }

