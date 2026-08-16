# Limites geográficos de São Paulo
GEO = {
    "lat_min": -23.7,
    "lat_max": -23.4,
    "lon_min": -46.8,
    "lon_max": -46.4,
}

# Regiões com multiplicadores diferentes
REGIOES = {
    "centro":     { "lat": (-23.55, -23.52), "lon": (-46.65, -46.62), "multiplicador": 1.2 },
    "aeroporto":  { "lat": (-23.44, -23.42), "lon": (-46.50, -46.47), "multiplicador": 1.4 },
    "periferia":  { "lat": (-23.68, -23.62), "lon": (-46.78, -46.72), "multiplicador": 0.85 },
    "geral":      { "lat": (-23.7,  -23.4 ), "lon": (-46.8,  -46.4 ), "multiplicador": 1.0 },
}

# Plataformas e categorias
PLATFORMS = [
    { "plataforma": "uber",    "categoria": "uber-moto",   "base": 3.5,  "per_km": 1.1, "per_min": 0.15 },
    { "plataforma": "uber",    "categoria": "uber-x",      "base": 4.5,  "per_km": 1.9, "per_min": 0.25 },
    { "plataforma": "uber",    "categoria": "uber-confort", "base": 7.5, "per_km": 2.8, "per_min": 0.45 },
    { "plataforma": "uber",    "categoria": "uber-black",  "base": 12.0, "per_km": 4.2, "per_min": 0.70 },
    { "plataforma": "99",      "categoria": "99-moto",     "base": 3.2,  "per_km": 1.0, "per_min": 0.12 },
    { "plataforma": "99",      "categoria": "99-pop",      "base": 4.0,  "per_km": 1.8, "per_min": 0.22 },
    { "plataforma": "99",      "categoria": "99-plus",     "base": 6.5,  "per_km": 2.4, "per_min": 0.38 },
]

# Multiplicadores por horário
HORA_MULTIPLICADOR = {
    range(0,  5):  0.80,  # madrugada — baixa demanda
    range(5,  7):  0.90,  # manhã cedo
    range(7, 10):  1.40,  # pico manhã
    range(10, 16): 1.00,  # horário normal
    range(16, 20): 1.35,  # pico tarde
    range(20, 24): 1.10,  # noite
}

# Multiplicadores por dia da semana
DIA_MULTIPLICADOR = {
    0: 1.10,  # segunda
    1: 1.00,  # terça
    2: 1.00,  # quarta
    3: 1.00,  # quinta
    4: 1.15,  # sexta
    5: 1.20,  # sábado
    6: 0.90,  # domingo
}

# Cenários de demanda e oferta
CENARIOS = [
    { "nome": "baixa_demanda",    "demanda": 30,  "motoristas": 80,  "peso": 0.10 },
    { "nome": "demanda_normal",   "demanda": 80,  "motoristas": 70,  "peso": 0.35 },
    { "nome": "alta_demanda",     "demanda": 150, "motoristas": 60,  "peso": 0.25 },
    { "nome": "pico_extremo",     "demanda": 300, "motoristas": 40,  "peso": 0.10 },
    { "nome": "poucos_motoristas","demanda": 100, "motoristas": 20,  "peso": 0.10 },
    { "nome": "excesso_motorista","demanda": 40,  "motoristas": 120, "peso": 0.10 },
]

# Faixa de variação do preço real em relação ao estimado
VARIACAO_PRECO = {
    "min": 0.92,
    "max": 1.12,
}

# Limite de preço para evitar valores absurdos
PRECO_MINIMO = 5.0
PRECO_MAXIMO = 300.0