from pydantic import BaseModel

# Pydantic valida os dados que chegam na API
# Pensa nele como o TypeScript do Python —
# garante que os dados têm o tipo certo antes de salvar no banco

class CorridaCreate(BaseModel):
    # Coordenadas
    origem_lat: float
    origem_lon: float
    destino_lat: float
    destino_lon: float

    # Rota
    distancia_km: float
    duracao_min: float

    # Horário — o app vai calcular e mandar pronto
    hora: int
    dia_semana: int

    # Plataforma
    plataforma: str
    categoria: str

    # Preços
    preco_estimado: float
    preco_real: float