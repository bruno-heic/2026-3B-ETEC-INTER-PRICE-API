from pydantic import BaseModel
from typing import Optional

class CorridaCreate(BaseModel):
    # Coordenadas
    origem_lat: float
    origem_lon: float
    destino_lat: float
    destino_lon: float

    # Rota
    distancia_km: float
    duracao_min: float

    # Horário
    hora: int
    dia_semana: int

    # Plataforma
    plataforma: str
    categoria: str

    # Cenário — Optional para não quebrar dados antigos
    cenario: Optional[str] = None
    demanda: Optional[int] = None
    motoristas: Optional[int] = None

    # Multiplicadores
    multiplicador_regiao: Optional[float] = None
    multiplicador_hora: Optional[float] = None
    multiplicador_demanda: Optional[float] = None

    # Preços
    preco_estimado: float
    preco_real: float

    # Probabilidade
    prob_aceitacao: Optional[float] = None