from database.connection import get_session
from models.cliente import Cliente
from models.emprestimo import Emprestimo
from models.parcela import Parcela
from models.recebimento import Recebimento

def clear_db():
    db = next(get_session())
    try:
        db.query(Recebimento).delete()
        db.query(Parcela).delete()
        db.query(Emprestimo).delete()
        db.query(Cliente).delete()
        db.commit()
        print("Registros apagados com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_db()
