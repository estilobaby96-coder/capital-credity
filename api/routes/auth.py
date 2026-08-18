from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_session
from services.auth_service import AuthService
from api.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_session)):
    user = auth_service.authenticate(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )
    # Gerar token JWT criptografado com dados do usuário
    access_token = create_access_token(data={
        "sub": str(user.id),
        "nome": user.nome,
        "role": user.tipo
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "login": user.login,
            "tipo": user.tipo
        }
    }

@router.get("/init-db")
def init_db(secret: str = ""):
    # Simples proteção para não deixar qualquer um resetar/recriar o banco
    if secret != "capitalcredity2026":
        raise HTTPException(status_code=403, detail="Não autorizado")
    
    from database.base import Base
    from database.connection import engine
    from database.seed import seed_admin
    
    # Importar todos os modelos para o SQLAlchemy reconhecê-los antes do create_all
    
    Base.metadata.create_all(bind=engine)
    seed_admin()
    
    return {"message": "Banco de dados inicializado com sucesso e usuário admin criado."}
