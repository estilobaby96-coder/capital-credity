from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String(10), unique=True, nullable=True, index=True)  # Ex: 001/2026
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    valor_emprestado = Column(Float, nullable=False)
    valor_liberado = Column(Float, nullable=False)
    taxa_juros = Column(Float, nullable=False)
    data_vencimento = Column(DateTime, nullable=False)
    garantia = Column(Text)
    tipo_garantia = Column(String(50), default="SEM_GARANTIA")
    promissoria_status = Column(String(50), default="NAO_EXIGIDA") # NAO_EXIGIDA, PENDENTE, ASSINADA
    fiador = Column(String(150))
    observacoes = Column(Text)
    status = Column(String(50), nullable=False, default="ATIVO") # ATIVO, QUITADO, RENEGOCIADO, CANCELADO
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="emprestimos")
    parcelas = relationship("Parcela", back_populates="emprestimo", cascade="all, delete-orphan")
    renegociacoes = relationship("Renegociacao", back_populates="emprestimo", cascade="all, delete-orphan")
