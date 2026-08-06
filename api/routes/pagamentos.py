from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_session
from services.pagamento_service import PagamentoService

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
pagamento_service = PagamentoService()

class PagamentoRequest(BaseModel):
    parcela_id: int
    valor_pago: float
    metodo_pagamento: str
    observacao: str = ""
    taxa_servico: float = 0.0

@router.post("/baixa")
def registrar_baixa(req: PagamentoRequest, db: Session = Depends(get_session)):
    try:
        resultado = pagamento_service.registrar_pagamento(
            db=db,
            parcela_id=req.parcela_id,
            valor_pago=req.valor_pago,
            metodo_pagamento=req.metodo_pagamento,
            observacao=req.observacao,
            taxa_servico=req.taxa_servico
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from services.dashboard_service import DashboardService
dashboard_service = DashboardService()

@router.get("/pendentes")
def listar_parcelas_pendentes(db: Session = Depends(get_session)):
    try:
        # Puxamos até 1000 parcelas pendentes para a tela de recebimentos
        parcelas = dashboard_service.get_proximas_parcelas(db, limite=1000)
        return [
            {
                "id": p.id,
                "cliente": p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "-",
                "numero_contrato": p.emprestimo.numero_contrato if p.emprestimo else "-",
                "parcela_num": p.numero,
                "vencimento": p.data_vencimento.isoformat() if p.data_vencimento else None,
                "valor_atualizado": p.valor_atualizado,
                "status": p.status
            }
            for p in parcelas
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
