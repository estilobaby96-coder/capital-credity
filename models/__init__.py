from database.base import Base
from .usuario import Usuario
from .cliente import Cliente
from .emprestimo import Emprestimo
from .parcela import Parcela
from .recebimento import Recebimento
from .renegociacao import Renegociacao
from .movimentacao import Movimentacao
from .garantia import Garantia

# Isso garante que todos os modelos sejam registrados no Base.metadata
__all__ = [
    "Base",
    "Usuario",
    "Cliente",
    "Emprestimo",
    "Parcela",
    "Recebimento",
    "Renegociacao",
    "Movimentacao",
    "Garantia"
]
