from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    cpf = Column(String(20), unique=True, index=True, nullable=False)
    rg = Column(String(30))
    telefone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(100))
    nascimento = Column(DateTime)
    profissao = Column(String(100))
    empresa = Column(String(100))
    renda = Column(String(50))
    estado_civil = Column(String(50))
    endereco = Column(String(200))
    cidade = Column(String(100))
    cep = Column(String(20))
    referencias = Column(Text)
    observacoes = Column(Text)
    foto_path = Column(String(255))
    doc_identidade = Column(Text) # Base64 da imagem/pdf do RG/CPF
    doc_endereco = Column(Text) # Base64 da imagem/pdf do comprovante de endereco
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    emprestimos = relationship("Emprestimo", back_populates="cliente", cascade="all, delete-orphan")
