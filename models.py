from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Corrida(Base):
    __tablename__ = "corridas"

    id = Column(Integer, primary_key=True, index=True)

    # Coordenadas de origem e destino
    origem_lat = Column(Float)
    origem_lon = Column(Float)
    destino_lat = Column(Float)
    destino_lon = Column(Float)

    # Dados da rota calculada pelo OSRM
    distancia_km = Column(Float)
    duracao_min = Column(Float)

    # Horário da corrida
    hora = Column(Integer)        # 0 a 23
    dia_semana = Column(Integer)  # 0 = segunda, 6 = domingo

    # Dados da plataforma
    plataforma = Column(String)   # "uber", "99", "indrive"
    categoria = Column(String)    # "uber-x", "99-pop", etc

    # Preços
    preco_estimado = Column(Float)  # o que o app calculou
    preco_real = Column(Float)      # o que o usuário pagou de fato

    # Preenchida automaticamente no momento do registro
    criado_em = Column(DateTime, default=datetime.utcnow)