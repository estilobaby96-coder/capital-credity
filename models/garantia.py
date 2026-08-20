from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class Garantia(Base):
    __tablename__ = "garantias"

    id = Column(Integer, primary_key=True, index=True)
    emprestimo_id = Column(Integer, ForeignKey("emprestimos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False, default="OUTRO")  # VEICULO, IMOVEL, EQUIPAMENTO, JOIA, OUTRO
    descricao = Column(Text, nullable=False)  # Ex: "Fiat Uno 2018 Prata, Placa ABC-1234"
    valor_estimado = Column(Float, nullable=True)
    observacoes = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="RETIDO")  # RETIDO, DEVOLVIDO, EXECUTADO

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    emprestimo = relationship("Emprestimo", back_populates="garantias")
