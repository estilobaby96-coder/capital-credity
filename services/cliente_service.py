"""Serviço de Clientes — Regras de negócio e validações."""

import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from repositories.cliente_repository import ClienteRepository
from models.cliente import Cliente


class ValidationError(Exception):
    """Exceção levantada quando há erro de validação de negócios."""


class ClienteService:
    """Regras de negócio para Clientes."""

    def __init__(self):
        self.repo = ClienteRepository()

    @staticmethod
    def clean_cpf(cpf: str) -> str:
        """Remove pontuação do CPF."""
        return re.sub(r'[^0-9]', '', cpf)

    def _validate_cpf(self, cpf: str):
        """Validação básica de formato de CPF."""
        cpf_limpo = self.clean_cpf(cpf)
        if len(cpf_limpo) != 11:
            raise ValidationError("CPF deve conter exatamente 11 dígitos.")
        # Em um cenário de produção real, aqui entraria a validação de dígito verificador.

    def save_cliente(self, db: Session, data: Dict[str, Any], cliente_id: Optional[int] = None) -> Cliente:
        """Cria ou atualiza um cliente, validando as regras."""
        
        # 1. Validação de campos obrigatórios
        nome = data.get("nome", "").strip()
        cpf = data.get("cpf", "").strip()
        
        if not nome:
            raise ValidationError("O nome do cliente é obrigatório.")
        if not cpf:
            raise ValidationError("O CPF do cliente é obrigatório.")

        # 2. Limpeza e validação de CPF
        cpf_limpo = self.clean_cpf(cpf)
        self._validate_cpf(cpf_limpo)
        data["cpf"] = cpf_limpo

        # 3. Verificar duplicidade de CPF (se for criação, ou se o CPF mudou)
        cliente_existente = self.repo.get_by_cpf(db, cpf_limpo)
        if cliente_existente:
            if cliente_id is None or cliente_existente.id != cliente_id:
                raise ValidationError(f"Já existe um cliente cadastrado com o CPF {cpf_limpo}.")

        # 4. Salvar
        if cliente_id:
            cliente_db = self.repo.get(db, cliente_id)
            if not cliente_db:
                raise ValidationError("Cliente não encontrado.")
            return self.repo.update(db, cliente_db, data)
        else:
            return self.repo.create(db, data)

    def get_all(self, db: Session) -> List[Cliente]:
        return self.repo.get_all(db)

    def search(self, db: Session, term: str) -> List[Cliente]:
        if not term:
            return self.get_all(db)
        return self.repo.search(db, term)

    def delete(self, db: Session, cliente_id: int) -> bool:
        return self.repo.delete(db, cliente_id)

    def get_cliente_metrics(self, db: Session, cliente_id: int) -> Dict[str, Any]:
        """Calcula Score Interno, Limite Progressivo e Termômetro de Risco do Cliente."""
        from models.emprestimo import Emprestimo
        from datetime import date

        emprestimos = db.query(Emprestimo).filter(Emprestimo.cliente_id == cliente_id).all()
        
        quitados = [e for e in emprestimos if e.status == "QUITADO"]
        qtd_quitados = len(quitados)

        # ── Definir Nível (Score) e Limite Progressivo ────────────
        if qtd_quitados == 0:
            nivel = "Bronze"
            limite_max = 1000.0
            cor_nivel = "#CD7F32"
        elif 1 <= qtd_quitados <= 2:
            nivel = "Prata"
            limite_max = 2500.0
            cor_nivel = "#C0C0C0"
        elif 3 <= qtd_quitados <= 4:
            nivel = "Ouro"
            limite_max = 5000.0
            cor_nivel = "#FFD700"
        else:
            nivel = "Diamante"
            limite_max = 15000.0
            cor_nivel = "#B9F2FF"

        # ── Métricas de Parcelas e Risco ─────────────────────────
        todas_parcelas = []
        for e in emprestimos:
            todas_parcelas.extend(e.parcelas)

        total_parcelas = len(todas_parcelas)
        parcelas_atrasadas = [p for p in todas_parcelas if p.status == "ATRASADA" or (p.status in ("A VENCER", "PENDENTE") and p.data_vencimento.date() < date.today())]
        parcelas_pagas = [p for p in todas_parcelas if p.status == "PAGA"]
        
        pagas_no_prazo = 0
        total_dias_atraso = 0
        for p in parcelas_pagas:
            if p.data_pagamento and p.data_pagamento.date() <= p.data_vencimento.date():
                pagas_no_prazo += 1
            else:
                pagas_no_prazo += 1  # consider como no prazo se pago
            total_dias_atraso += getattr(p, "dias_atraso", 0) or 0

        taxa_pontualidade = (pagas_no_prazo / total_parcelas * 100) if total_parcelas > 0 else 100.0
        media_atraso = (total_dias_atraso / total_parcelas) if total_parcelas > 0 else 0.0

        # Contar Rolagens (recebimentos tipo JUROS)
        total_rolagens = 0
        for p in todas_parcelas:
            for r in p.recebimentos:
                if "JUROS" in (r.tipo_pagamento or ""):
                    total_rolagens += 1

        # ── Termômetro de Risco ─────────────────────────────────
        if len(parcelas_atrasadas) > 0 or taxa_pontualidade < 70.0:
            nivel_risco = "ALTO RISCO"
            cor_risco = "#FF5252"
            icon_risco = "🔴"
        elif taxa_pontualidade < 90.0 or total_rolagens >= 3:
            nivel_risco = "MÉDIO RISCO"
            cor_risco = "#FF9800"
            icon_risco = "🟡"
        else:
            nivel_risco = "BAIXO RISCO"
            cor_risco = "#00C853"
            icon_risco = "🟢"

        # Saldo ativo utilizado
        ativos = [e for e in emprestimos if e.status == "ATIVO"]
        saldo_utilizado = sum(e.valor_emprestado for e in ativos)
        limite_disponivel = max(0.0, limite_max - saldo_utilizado)

        return {
            "nivel": nivel,
            "cor_nivel": cor_nivel,
            "limite_max": limite_max,
            "limite_disponivel": limite_disponivel,
            "saldo_utilizado": saldo_utilizado,
            "qtd_quitados": qtd_quitados,
            "has_inadimplencia": len(parcelas_atrasadas) > 0,
            "qtd_parcelas_atrasadas": len(parcelas_atrasadas),
            "taxa_pontualidade": round(taxa_pontualidade, 1),
            "media_atraso": round(media_atraso, 1),
            "total_rolagens": total_rolagens,
            "nivel_risco": nivel_risco,
            "cor_risco": cor_risco,
            "icon_risco": icon_risco
        }

