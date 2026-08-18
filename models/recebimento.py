from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Recebimento(Base):
    __tablename__ = "recebimentos"

    id = Column(Integer, primary_key=True, index=True)
    parcela_id = Column(Integer, ForeignKey("parcelas.id"), nullable=False)
    valor_pago = Column(Float, nullable=False)
    tipo_pagamento = Column(String(50), nullable=False) # INTEGRAL, PARCIAL, APENAS_JUROS, RENEGOCIACAO
    forma_pagamento = Column(String(50), nullable=False) # PIX, DINHEIRO, TRANSFERENCIA, CARTAO
    data_pagamento = Column(DateTime, nullable=False, default=func.now())
    observacoes = Column(Text)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    parcela = relationship("Parcela", back_populates="recebimentos")
    operador = relationship("Usuario")
    movimentacoes = relationship("Movimentacao", back_populates="recebimento", cascade="all, delete-orphan")
