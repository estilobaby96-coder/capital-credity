from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Parcela(Base):
    __tablename__ = "parcelas"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    numero = Column(Integer, nullable=False)
    capital = Column(Float, nullable=False)
    juros = Column(Float, nullable=False)
    multa = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    dias_atraso = Column(Integer, default=0)
    valor_atualizado = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="A VENCER") # PAGA, ATRASADA, A VENCER, JUROS PAGOS, PARCIAL, RENEGOCIADA, CANCELADA
    data_vencimento = Column(DateTime, nullable=False)
    data_pagamento = Column(DateTime)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    emprestimo = relationship("Emprestimo", back_populates="parcelas")
    operador = relationship("Usuario")
    recebimentos = relationship("Recebimento", back_populates="parcela", cascade="all, delete-orphan")
