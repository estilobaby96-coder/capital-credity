from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database.connection import get_session
from services.relatorio_service import RelatorioService

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])
relatorio_service = RelatorioService()

@router.get("/mensal")
def get_controle_mensal(mes: int = None, ano: int = None, db: Session = Depends(get_session)):
    try:
        hoje = date.today()
        if mes is None:
            mes = hoje.month
        if ano is None:
            ano = hoje.year
            
        dados = relatorio_service.controle_mensal(db, mes=mes, ano=ano)
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/extrato/{cliente_id}")
def get_extrato(cliente_id: int, db: Session = Depends(get_session)):
    try:
        dados = relatorio_service.extrato_cliente(db, cliente_id)
        if not dados["cliente"]:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
            
        return {
            "cliente": {
                "id": dados["cliente"].id,
                "nome": dados["cliente"].nome,
                "cpf": dados["cliente"].cpf,
                "telefone": dados["cliente"].telefone
            },
            "emprestimos": [
                {
                    "id": emp["emprestimo"].id,
                    "numero_contrato": emp["emprestimo"].numero_contrato,
                    "valor": emp["emprestimo"].valor_emprestado,
                    "status": emp["emprestimo"].status,
                    "parcelas": [
                        {
                            "numero": p.numero,
                            "vencimento": p.data_vencimento.isoformat() if p.data_vencimento else None,
                            "valor": p.valor_atualizado,
                            "status": p.status
                        } for p in emp["parcelas"]
                    ]
                } for emp in dados["emprestimos"]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/inadimplencia")
def get_inadimplencia(db: Session = Depends(get_session)):
    try:
        dados = relatorio_service.inadimplencia(db)
        # Format the date explicitly
        for row in dados:
            if 'vencimento' in row and row['vencimento']:
                row['vencimento'] = row['vencimento'].isoformat()
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/fluxo_caixa")
def get_fluxo_caixa(data_inicio: date, data_fim: date, db: Session = Depends(get_session)):
    try:
        dados = relatorio_service.fluxo_caixa(db, data_inicio, data_fim)
        # format date explicitly
        for row in dados:
            if 'data' in row and row['data']:
                row['data'] = row['data'].isoformat()
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
