import random
import requests
from datetime import datetime

# URL da sua API local
API_URL = "http://127.0.0.1:8000/corridas"

# Tarifas por categoria — igual ao platforms.ts do app
PLATFORMS = [
    { "plataforma": "uber", "categoria": "uber-moto", "base": 3.5, "per_km": 1.1, "per_min": 0.15 },
    { "plataforma": "uber", "categoria": "uber-x", "base": 4.5, "per_km": 1.9, "per_min": 0.25 },
    { "plataforma": "uber", "categoria": "uber-confort", "base": 7.5, "per_km": 2.8, "per_min": 0.45 },
    { "plataforma": "uber", "categoria": "uber-black", "base": 12.0, "per_km": 4.2, "per_min": 0.7 },
    { "plataforma": "99", "categoria": "99-moto", "base": 3.2, "per_km": 1.0, "per_min": 0.12 },
    { "plataforma": "99", "categoria": "99-pop", "base": 4.0, "per_km": 1.8, "per_min": 0.22 },
    { "plataforma": "99", "categoria": "99-plus", "base": 6.5, "per_km": 2.4, "per_min": 0.38 },
]

# Limites geográficos de São Paulo
SP_LAT_MIN, SP_LAT_MAX = -23.7, -23.4
SP_LON_MIN, SP_LON_MAX = -46.8, -46.4

def gerar_coordenada():
    # Gera um ponto aleatório dentro de São Paulo
    lat = random.uniform(SP_LAT_MIN, SP_LAT_MAX)
    lon = random.uniform(SP_LON_MIN, SP_LON_MAX)
    return lat, lon

def buscar_rota(origem_lat, origem_lon, destino_lat, destino_lon):
    # Chama o OSRM para pegar distância e tempo reais
    url = f"https://router.project-osrm.org/route/v1/driving/{origem_lon},{origem_lat};{destino_lon},{destino_lat}?overview=false"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data["code"] != "Ok":
            return None
        rota = data["routes"][0]
        return {
            "distancia_km": rota["distance"] / 1000,
            "duracao_min": rota["duration"] / 60,
        }
    except:
        return None

def calcular_preco(platform, distancia_km, duracao_min, hora):
    # Surge em horário de pico
    peak = (7 <= hora <= 9) or (17 <= hora <= 20)
    surge = 1.4 if peak else 1.0

    preco = platform["base"] + platform["per_km"] * distancia_km + platform["per_min"] * duracao_min
    return round(preco * surge, 2)

def simular(quantidade=100):
    salvos = 0

    for i in range(quantidade):
        # Coordenadas aleatórias
        origem_lat, origem_lon = gerar_coordenada()
        destino_lat, destino_lon = gerar_coordenada()

        # Rota real via OSRM
        rota = buscar_rota(origem_lat, origem_lon, destino_lat, destino_lon)
        if not rota:
            print(f"[{i+1}] Rota não encontrada, pulando...")
            continue

        # Horário e dia aleatórios
        hora = random.randint(0, 23)
        dia_semana = random.randint(0, 6)

        # Plataforma aleatória
        platform = random.choice(PLATFORMS)

        # Preço estimado
        preco_estimado = calcular_preco(platform, rota["distancia_km"], rota["duracao_min"], hora)

        # Preço real com variação de -15% a +25%
        preco_real = round(preco_estimado * random.uniform(0.95, 1.10), 2)

        # Monta o payload
        payload = {
            "origem_lat": origem_lat,
            "origem_lon": origem_lon,
            "destino_lat": destino_lat,
            "destino_lon": destino_lon,
            "distancia_km": rota["distancia_km"],
            "duracao_min": rota["duracao_min"],
            "hora": hora,
            "dia_semana": dia_semana,
            "plataforma": platform["plataforma"],
            "categoria": platform["categoria"],
            "preco_estimado": preco_estimado,
            "preco_real": preco_real,
        }

        # Salva na API
        try:
            res = requests.post(API_URL, json=payload, timeout=5)
            if res.status_code == 200:
                salvos += 1
                print(f"[{i+1}] Salvo — {platform['categoria']} · R$ {preco_real}")
            else:
                print(f"[{i+1}] Erro ao salvar: {res.status_code}")
        except:
            print(f"[{i+1}] Erro de conexão")

    print(f"\nConcluído — {salvos}/{quantidade} corridas salvas")

# Roda o script — muda o número para quantas corridas quiser
simular(1000)