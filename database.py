from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# O banco vai ficar salvo num arquivo chamado rideless.db
# na raiz do projeto — simples assim
DATABASE_URL = "sqlite:///./rideless.db"

# O engine é a conexão com o banco
# connect_args é necessário para o SQLite funcionar com FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal é a fábrica de sessões
# Cada requisição vai abrir e fechar uma sessão
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)