from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from database.connection import get_session
from services.cliente_service import ClienteService, ValidationError

class ClienteCreate(BaseModel):
    nome: str
    cpf: str
    telefone: Optional[str] = ""
    email: Optional[str] = ""
    cep: Optional[str] = ""
    endereco: Optional[str] = ""

router = APIRouter(prefix="/clientes", tags=["Clientes"])
cliente_service = ClienteService()

@router.get("/")
def listar_clientes(db: Session = Depends(get_session)):
    clientes = cliente_service.get_all(db)
    # Convert models to dict for JSON serialization
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "telefone": c.telefone,
            "nivel_score": "Prata" # Stub para evitar erro, caso seja calculado
        }
        for c in clientes
    ]

@router.post("/")
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_session)):
    try:
        novo_cliente = cliente_service.save_cliente(db, cliente.model_dump())
        return {"id": novo_cliente.id, "nome": novo_cliente.nome, "cpf": novo_cliente.cpf}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cliente_id}/metrics")
def cliente_metrics(cliente_id: int, db: Session = Depends(get_session)):
    try:
        metrics = cliente_service.get_cliente_metrics(db, cliente_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
