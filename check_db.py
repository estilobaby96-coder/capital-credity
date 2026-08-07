from database.connection import get_session
from models.cliente import Cliente
from models.emprestimo import Emprestimo

db = next(get_session())
clientes = db.query(Cliente).all()
emprestimos = db.query(Emprestimo).all()
print(f"Clientes: {len(clientes)}")
print(f"Emprestimos: {len(emprestimos)}")
db.close()
