from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Renegociacao(Base):
    __tablename__ = "renegociacoes"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    novo_valor = Column(Float, nullable=False)
    nova_taxa = Column(Float, nullable=False)
    novo_prazo = Column(Integer, nullable=False)
    observacoes = Column(Text)
    operador_id = Column(Integer, ForeignKey("usuarios.id"))
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    emprestimo = relationship("Emprestimo", back_populates="renegociacoes")
    operador = relationship("Usuario")
