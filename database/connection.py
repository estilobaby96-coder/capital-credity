import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define o caminho do banco de dados dependendo do ambiente
if getattr(sys, 'frozen', False):
    # Rodando via PyInstaller (produção)
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    db_dir = os.path.join(appdata, "Capital_Credity", "database")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "neto_gestor.db")
else:
    # Rodando via código fonte (desenvolvimento)
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "neto_gestor.db")

db_url = "postgresql+psycopg2://neondb_owner:npg_jyOR1Ae9HKJM@ep-divine-pine-ac71arap-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"

# Cria o engine
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Retorna uma sessão do banco de dados (deve ser fechada após o uso)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
