import random
import requests
from datetime import datetime
from config import (
    GEO, REGIOES, PLATFORMS, HORA_MULTIPLICADOR,
    DIA_MULTIPLICADOR, CENARIOS, VARIACAO_PRECO,
    PRECO_MINIMO, PRECO_MAXIMO
)

# URL da API local
API_URL = "http://127.0.0.1:8000/rides"

# Seed para reprodutibilidade — sempre gera os mesmos dados
random.seed(42)

def gerar_coordenada_regiao(regiao: dict) -> tuple:
    # Gera coordenada dentro dos limites de uma região específica
    lat = random.uniform(regiao["lat"][0], regiao["lat"][1])
    lon = random.uniform(regiao["lon"][0], regiao["lon"][1])
    return lat, lon

def gerar_coordenada_geral() -> tuple:
    lat = random.uniform(GEO["lat_min"], GEO["lat_max"])
    lon = random.uniform(GEO["lon_min"], GEO["lon_max"])
    return lat, lon

def escolher_regiao() -> dict:
    # Escolhe uma região aleatória — aeroporto e periferia aparecem menos
    pesos = [0.30, 0.10, 0.20, 0.40]  # centro, aeroporto, periferia, geral
    return random.choices(list(REGIOES.values()), weights=pesos)[0]

def buscar_rota(origem_lat, origem_lon, destino_lat, destino_lon) -> dict | None:
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{origem_lon},{origem_lat};{destino_lon},{destino_lat}?overview=false"
    )
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

def get_multiplicador_hora(hora: int) -> float:
    for intervalo, mult in HORA_MULTIPLICADOR.items():
        if hora in intervalo:
            return mult
    return 1.0

def calcular_multiplicador_demanda(demanda: int, motoristas: int) -> float:
    # Relação demanda/oferta — limitada para evitar valores absurdos
    ratio = demanda / max(motoristas, 1)
    if ratio < 0.5:   return 0.85
    if ratio < 1.0:   return 1.00
    if ratio < 1.5:   return 1.15
    if ratio < 2.0:   return 1.30
    if ratio < 3.0:   return 1.50
    return 1.70  # máximo

def calcular_preco_estimado(platform, distancia_km, duracao_min, hora, dia_semana, regiao, cenario) -> float:
    # Preço base
    preco = (
        platform["base"] +
        platform["per_km"] * distancia_km +
        platform["per_min"] * duracao_min
    )

    # Aplica multiplicadores
    preco *= get_multiplicador_hora(hora)
    preco *= DIA_MULTIPLICADOR[dia_semana]
    preco *= regiao["multiplicador"]
    preco *= calcular_multiplicador_demanda(cenario["demanda"], cenario["motoristas"])

    # Garante limites
    return round(max(PRECO_MINIMO, min(preco, PRECO_MAXIMO)), 2)

def calcular_probabilidade_aceitacao(preco, distancia_km, demanda, motoristas) -> float:
    # Quanto maior o preço relativo à distância, menor a aceitação
    preco_por_km = preco / max(distancia_km, 0.1)
    ratio_demanda = demanda / max(motoristas, 1)

    # Base de aceitação
    aceitacao = 0.85

    # Penaliza preço alto
    if preco_por_km > 5: aceitacao -= 0.20
    elif preco_por_km > 3: aceitacao -= 0.10

    # Alta demanda aumenta aceitação
    if ratio_demanda > 2: aceitacao += 0.10
    elif ratio_demanda < 0.5: aceitacao -= 0.15

    return round(max(0.1, min(aceitacao, 0.99)), 2)

def simular(quantidade: int = 100):
    salvos = 0

    for i in range(quantidade):
        # Escolhe região e gera coordenadas
        regiao_origem = escolher_regiao()
        regiao_destino = escolher_regiao()

        origem_lat, origem_lon = gerar_coordenada_regiao(regiao_origem)
        destino_lat, destino_lon = gerar_coordenada_regiao(regiao_destino)

        # Busca rota real via OSRM
        rota = buscar_rota(origem_lat, origem_lon, destino_lat, destino_lon)
        if not rota:
            print(f"[{i+1}] Rota não encontrada, pulando...")
            continue

        # Horário e dia aleatórios
        hora = random.randint(0, 23)
        dia_semana = random.randint(0, 6)

        # Cenário de demanda — respeita os pesos definidos no config
        cenario = random.choices(
            CENARIOS,
            weights=[c["peso"] for c in CENARIOS]
        )[0]

        # Plataforma aleatória
        platform = random.choice(PLATFORMS)

        # Calcula preço estimado com todos os multiplicadores
        preco_estimado = calcular_preco_estimado(
            platform,
            rota["distancia_km"],
            rota["duracao_min"],
            hora,
            dia_semana,
            regiao_origem,
            cenario
        )

        # Preço real com variação realista
        variacao = random.uniform(VARIACAO_PRECO["min"], VARIACAO_PRECO["max"])
        preco_real = round(max(PRECO_MINIMO, preco_estimado * variacao), 2)

        # Probabilidade de aceitação
        prob_aceitacao = calcular_probabilidade_aceitacao(
            preco_estimado,
            rota["distancia_km"],
            cenario["demanda"],
            cenario["motoristas"]
        )

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
            "cenario": cenario["nome"],
            "demanda": cenario["demanda"],
            "motoristas": cenario["motoristas"],
            "multiplicador_regiao": regiao_origem["multiplicador"],
            "multiplicador_hora": get_multiplicador_hora(hora),
            "multiplicador_demanda": calcular_multiplicador_demanda(cenario["demanda"], cenario["motoristas"]),
            "preco_estimado": preco_estimado,
            "preco_real": preco_real,
            "prob_aceitacao": prob_aceitacao,
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=5)
            if res.status_code == 200:
                salvos += 1
                print(f"[{i+1}] {platform['categoria']} · R$ {preco_real} · aceitação: {prob_aceitacao} · cenário: {cenario['nome']}")
            else:
                print(f"[{i+1}] Erro: {res.status_code}")
        except:
            print(f"[{i+1}] Erro de conexão")

    print(f"\nConcluído — {salvos}/{quantidade} corridas salvas")

if __name__ == "__main__":
    import sys

    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    simular(quantidade)
