from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_session
from services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
dashboard_service = DashboardService()

@router.get("/resumo")
def get_resumo(db: Session = Depends(get_session)):
    try:
        metrics = dashboard_service.get_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/proximas_parcelas")
def get_proximas_parcelas(limite: int = 10, db: Session = Depends(get_session)):
    try:
        parcelas = dashboard_service.get_proximas_parcelas(db, limite=limite)
        return [
            {
                "id": p.id,
                "cliente": p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "—",
                "numero_contrato": p.emprestimo.numero_contrato if p.emprestimo else "",
                "parcela_num": p.numero,
                "vencimento": p.data_vencimento.isoformat() if p.data_vencimento else None,
                "valor_atualizado": p.valor_atualizado,
                "status": p.status
            }
            for p in parcelas
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
