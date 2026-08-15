from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Corrida
from schemas import CorridaCreate
from datetime import datetime
import joblib

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Load model and encoders on startup
model = joblib.load("model.pkl")
le_plataforma = joblib.load("le_plataforma.pkl")
le_categoria = joblib.load("le_categoria.pkl")

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
        preco_estimado=corrida.preco_estimado,
        preco_real=corrida.preco_real,
        criado_em=datetime.utcnow()
    )
    db.add(nova_corrida)
    db.commit()
    db.refresh(nova_corrida)
    return { "id": nova_corrida.id, "status": "ride saved" }

# Total must come before limit to avoid FastAPI confusing it with a parameter
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
    # Transform platform and category into numbers
    plataforma_enc = le_plataforma.transform([corrida.plataforma])[0]
    categoria_enc = le_categoria.transform([corrida.categoria])[0]

    # Build features array in the same order as training
    features = [[
        corrida.distancia_km,
        corrida.duracao_min,
        corrida.hora,
        corrida.dia_semana,
        plataforma_enc,
        categoria_enc,
        corrida.preco_estimado,
    ]]

    preco = model.predict(features)[0]
    return { "predicted_price": round(float(preco), 2) }