from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Corrida(Base):
    __tablename__ = "corridas"

    id = Column(Integer, primary_key=True, index=True)

    # Coordenadas
    origem_lat = Column(Float)
    origem_lon = Column(Float)
    destino_lat = Column(Float)
    destino_lon = Column(Float)

    # Rota
    distancia_km = Column(Float)
    duracao_min = Column(Float)

    # Horário
    hora = Column(Integer)
    dia_semana = Column(Integer)

    # Plataforma
    plataforma = Column(String)
    categoria = Column(String)

    # Cenário de demanda
    cenario = Column(String)
    demanda = Column(Integer)
    motoristas = Column(Integer)

    # Região
    multiplicador_regiao = Column(Float)
    multiplicador_hora = Column(Float)
    multiplicador_demanda = Column(Float)

    # Preços
    preco_estimado = Column(Float)
    preco_real = Column(Float)

    # Probabilidade
    prob_aceitacao = Column(Float)

    criado_em = Column(DateTime, default=datetime.utcnow)