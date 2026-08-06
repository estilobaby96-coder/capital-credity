from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_session
from services.auth_service import AuthService

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
    # Em um app real usaríamos JWT. Aqui retornamos um token simulado e info do usuário.
    return {
        "access_token": f"simulated-token-for-{user.id}",
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
    from models.usuario import Usuario
    from models.cliente import Cliente
    from models.emprestimo import Emprestimo
    from models.parcela import Parcela
    from models.recebimento import Recebimento
    from models.renegociacao import Renegociacao
    from models.movimentacao import Movimentacao
    
    Base.metadata.create_all(bind=engine)
    seed_admin()
    
    return {"message": "Banco de dados inicializado com sucesso e usuário admin criado."}
