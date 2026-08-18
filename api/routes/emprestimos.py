from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database.connection import get_session
from services.emprestimo_service import EmprestimoService
from api.security import get_current_user

class EmprestimoCreate(BaseModel):
    cliente_id: int
    valor_solicitado: float
    taxa_juros: float
    data_vencimento: date
    tipo_garantia: Optional[str] = "SEM_GARANTIA"
    garantia_desc: Optional[str] = ""
    promissoria_status: Optional[str] = "NAO_EXIGIDA"
    fiador: Optional[str] = ""
    observacoes: Optional[str] = ""

router = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])
emprestimo_service = EmprestimoService()

@router.get("/")
def listar_emprestimos(db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    emprestimos = emprestimo_service.get_all(db)
    return [
        {
            "id": e.id,
            "numero_contrato": e.numero_contrato,
            "cliente_id": e.cliente_id,
            "cliente_nome": e.cliente.nome if e.cliente else "N/A",
            "valor_principal": e.valor_emprestado,
            "valor_total": e.valor_emprestado * (1 + (e.taxa_juros/100)), # Stub aproximado
            "status": e.status,
            "data_emprestimo": e.criado_em.isoformat() if e.criado_em else None
        }
        for e in emprestimos
    ]

@router.post("/")
def criar_emprestimo(emprestimo: EmprestimoCreate, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        novo = emprestimo_service.create_loan(
            db=db,
            cliente_id=emprestimo.cliente_id,
            valor_solicitado=emprestimo.valor_solicitado,
            taxa_juros=emprestimo.taxa_juros,
            data_vencimento=emprestimo.data_vencimento,
            tipo_garantia=emprestimo.tipo_garantia,
            garantia_desc=emprestimo.garantia_desc,
            promissoria_status=emprestimo.promissoria_status,
            fiador=emprestimo.fiador,
            observacoes=emprestimo.observacoes
        )
        return {"id": novo.id, "numero_contrato": novo.numero_contrato, "status": novo.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{emprestimo_id}/parcelas")
def listar_parcelas(emprestimo_id: int, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        emprestimo = emprestimo_service.get_by_id(db, emprestimo_id)
        if not emprestimo:
            raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
        return [
            {
                "id": p.id,
                "numero_parcela": p.numero_parcela,
                "data_vencimento": p.data_vencimento.isoformat() if p.data_vencimento else None,
                "capital": p.capital,
                "juros": p.juros,
                "valor_atualizado": p.valor_atualizado,
                "status": p.status
            }
            for p in emprestimo.parcelas
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class EmprestimoUpdate(BaseModel):
    valor_solicitado: float
    taxa_juros: float
    data_vencimento: date

@router.put("/{emprestimo_id}")
def atualizar_emprestimo(emprestimo_id: int, dados: EmprestimoUpdate, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        atualizado = emprestimo_service.update_loan(
            db=db,
            emprestimo_id=emprestimo_id,
            valor=dados.valor_solicitado,
            taxa_juros=dados.taxa_juros,
            data_vencimento=dados.data_vencimento
        )
        return {"id": atualizado.id, "numero_contrato": atualizado.numero_contrato, "status": atualizado.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{emprestimo_id}/cancelar")
def cancelar_emprestimo(emprestimo_id: int, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        cancelado = emprestimo_service.cancel_loan(db, emprestimo_id)
        return {"id": cancelado.id, "numero_contrato": cancelado.numero_contrato, "status": cancelado.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

