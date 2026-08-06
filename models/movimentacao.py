from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False) # ENTRADA, SAIDA
    valor = Column(Float, nullable=False)
    descricao = Column(String(200), nullable=False)
    forma_pagamento = Column(String(50)) # PIX, DINHEIRO, TRANSFERENCIA, CARTAO
    data = Column(DateTime, nullable=False, default=func.now())
    observacoes = Column(Text)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    # Opcional: Relacionamento com recebimento caso a entrada seja originada de um recebimento
    recebimento_id = Column(Integer, ForeignKey("recebimentos.id"), nullable=True)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    operador = relationship("Usuario")
    recebimento = relationship("Recebimento")
