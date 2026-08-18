from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from database.connection import get_session
from services.cliente_service import ClienteService, ValidationError
from api.security import get_current_user

class ClienteCreate(BaseModel):
    nome: str
    cpf: str
    telefone: Optional[str] = ""
    email: Optional[str] = ""
    cep: Optional[str] = ""
    endereco: Optional[str] = ""
    doc_identidade: Optional[str] = ""
    doc_endereco: Optional[str] = ""

router = APIRouter(prefix="/clientes", tags=["Clientes"])
cliente_service = ClienteService()

@router.get("/")
def listar_clientes(db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    clientes = cliente_service.get_all(db)
    
    result = []
    for c in clientes:
        result.append({
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "telefone": c.telefone,
            "tem_doc_identidade": bool(c.doc_identidade),
            "tem_doc_endereco": bool(c.doc_endereco)
        })
        
    return result

@router.post("/")
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        novo_cliente = cliente_service.save_cliente(db, cliente.model_dump())
        return {"id": novo_cliente.id, "nome": novo_cliente.nome, "cpf": novo_cliente.cpf}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cliente_id}/metrics")
def cliente_metrics(cliente_id: int, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        metrics = cliente_service.get_cliente_metrics(db, cliente_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{cliente_id}")
def obter_cliente(cliente_id: int, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    cliente = cliente_service.repo.get(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "telefone": cliente.telefone,
        "email": cliente.email,
        "cep": cliente.cep,
        "endereco": cliente.endereco,
        "cidade": cliente.cidade,
        "doc_identidade": cliente.doc_identidade,
        "doc_endereco": cliente.doc_endereco
    }

@router.put("/{cliente_id}")
def atualizar_cliente(cliente_id: int, cliente: ClienteCreate, db: Session = Depends(get_session), _user: dict = Depends(get_current_user)):
    try:
        atualizado = cliente_service.save_cliente(db, cliente.model_dump(), cliente_id)
        return {"id": atualizado.id, "nome": atualizado.nome, "cpf": atualizado.cpf}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
