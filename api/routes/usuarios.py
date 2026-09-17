from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from database.connection import get_session
from services.auth_service import AuthService
from api.security import get_current_user

class UsuarioCreate(BaseModel):
    nome: str
    login: str
    senha: str
    tipo: Optional[str] = "FUNCIONARIO"

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    login: Optional[str] = None
    senha: Optional[str] = None
    tipo: Optional[str] = None
    ativo: Optional[bool] = None

router = APIRouter(prefix="/usuarios", tags=["Usuários"])
auth_service = AuthService()

@router.get("/")
def listar_usuarios(db: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    usuarios = auth_service.usuario_repo.get_all(db)
    
    return [
        {
            "id": u.id,
            "nome": u.nome,
            "login": u.login,
            "tipo": u.tipo,
            "ativo": u.ativo
        }
        for u in usuarios
    ]

@router.post("/")
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    existente = auth_service.usuario_repo.get_by_login(db, usuario.login)
    if existente:
        raise HTTPException(status_code=400, detail="Login já está em uso")

    novo_user = auth_service.create_user(
        db=db,
        nome=usuario.nome,
        login=usuario.login,
        password=usuario.senha,
        tipo=usuario.tipo
    )
    return {"id": novo_user.id, "nome": novo_user.nome, "login": novo_user.login}

@router.put("/{usuario_id}")
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    usuario_db = auth_service.usuario_repo.get(db, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if dados.login and dados.login != usuario_db.login:
        existente = auth_service.usuario_repo.get_by_login(db, dados.login)
        if existente:
            raise HTTPException(status_code=400, detail="Login já está em uso")
            
    update_data = {}
    if dados.nome is not None:
        update_data["nome"] = dados.nome
    if dados.login is not None:
        update_data["login"] = dados.login
    if dados.tipo is not None:
        update_data["tipo"] = dados.tipo
    if dados.ativo is not None:
        update_data["ativo"] = dados.ativo
    if dados.senha is not None and dados.senha.strip() != "":
        update_data["senha_hash"] = auth_service.hash_password(dados.senha)

    if update_data:
        usuario_db = auth_service.usuario_repo.update(db, update_data, usuario_id)
        
    return {"id": usuario_db.id, "nome": usuario_db.nome, "login": usuario_db.login, "ativo": usuario_db.ativo}

@router.delete("/{usuario_id}")
def desativar_usuario(usuario_id: int, db: Session = Depends(get_session), user: dict = Depends(get_current_user)):
    usuario_db = auth_service.usuario_repo.get(db, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if str(usuario_id) == str(user.get("id")) or usuario_db.login == user.get("sub"):
        raise HTTPException(status_code=400, detail="Não é possível desativar o próprio usuário logado")
        
    auth_service.usuario_repo.update(db, {"ativo": False}, usuario_id)
    return {"status": "success", "message": "Usuário desativado"}
