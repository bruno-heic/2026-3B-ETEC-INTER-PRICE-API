from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Corrida
from schemas import CorridaCreate
from datetime import datetime
import joblib

app = FastAPI()

Base.metadata.create_all(bind=engine)

model = joblib.load("model.pkl")
le_plataforma = joblib.load("le_plataforma.pkl")
le_categoria = joblib.load("le_categoria.pkl")
le_cenario = joblib.load("le_cenario.pkl")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return { "status": "Price API running!" }

@app.post("/rides")
def save_ride(corrida: CorridaCreate, db: Session = Depends(get_db)):
    nova_corrida = Corrida(
        origem_lat=corrida.origem_lat,
        origem_lon=corrida.origem_lon,
        destino_lat=corrida.destino_lat,
        destino_lon=corrida.destino_lon,
        distancia_km=corrida.distancia_km,
        duracao_min=corrida.duracao_min,
        hora=corrida.hora,
        dia_semana=corrida.dia_semana,
        plataforma=corrida.plataforma,
        categoria=corrida.categoria,
        cenario=corrida.cenario,
        demanda=corrida.demanda,
        motoristas=corrida.motoristas,
        multiplicador_regiao=corrida.multiplicador_regiao,
        multiplicador_hora=corrida.multiplicador_hora,
        multiplicador_demanda=corrida.multiplicador_demanda,
        preco_estimado=corrida.preco_estimado,
        preco_real=corrida.preco_real,
        prob_aceitacao=corrida.prob_aceitacao,
        criado_em=datetime.utcnow()
    )
    db.add(nova_corrida)
    db.commit()
    db.refresh(nova_corrida)
    return { "id": nova_corrida.id, "status": "ride saved" }


@app.get("/rides/total")
def total_rides(db: Session = Depends(get_db)):
    total = db.query(Corrida).count()
    return { "total": total }

@app.get("/rides")
def list_rides(limit: int = 10, db: Session = Depends(get_db)):
    corridas = db.query(Corrida).limit(limit).all()
    return corridas

@app.post("/predict")
def predict_price(corrida: CorridaCreate):
    # Transforma texto em número
    plataforma_enc = le_plataforma.transform([corrida.plataforma])[0]
    categoria_enc = le_categoria.transform([corrida.categoria])[0]
    cenario_enc = le_cenario.transform([corrida.cenario or "desconhecido"])[0]

    # Calcula multiplicador de demanda
    demanda = corrida.demanda or 80
    motoristas = corrida.motoristas or 70
    ratio = demanda / max(motoristas, 1)

    if ratio < 0.5:   mult_demanda = 0.85
    elif ratio < 1.0: mult_demanda = 1.00
    elif ratio < 1.5: mult_demanda = 1.15
    elif ratio < 2.0: mult_demanda = 1.30
    elif ratio < 3.0: mult_demanda = 1.50
    else:             mult_demanda = 1.70

    features = [[
        corrida.distancia_km,
        corrida.duracao_min,
        corrida.hora,
        corrida.dia_semana,
        plataforma_enc,
        categoria_enc,
        cenario_enc,
        demanda,
        motoristas,
        corrida.multiplicador_regiao or 1.0,
        corrida.multiplicador_hora or 1.0,
        mult_demanda,
        corrida.prob_aceitacao or 0.85,
        corrida.preco_estimado,
    ]]

    preco = float(model.predict(features)[0])

    # Faixa de preço — ±10% do previsto
    preco_min = round(max(5.0, preco * 0.90), 2)
    preco_max = round(min(300.0, preco * 1.10), 2)
    preco_previsto = round(preco, 2)

    # Probabilidade de aceitação
    preco_por_km = preco / max(corrida.distancia_km, 0.1)
    aceitacao = 0.85
    if preco_por_km > 5: aceitacao -= 0.20
    elif preco_por_km > 3: aceitacao -= 0.10
    if ratio > 2: aceitacao += 0.10
    elif ratio < 0.5: aceitacao -= 0.15
    aceitacao = round(max(0.1, min(aceitacao, 0.99)), 2)

    # Confiança baseada no R² do modelo (0.9914)
    confidence = round(0.9914 * aceitacao, 4)

    return {
        "predicted_price": preco_previsto,
        "price_min": preco_min,
        "price_max": preco_max,
        "acceptance_probability": aceitacao,
        "demand_multiplier": mult_demanda,
        "confidence": confidence,
    }