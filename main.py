from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Corrida
from schemas import CorridaCreate
from datetime import datetime

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return { "status": "Rideless API funcionando" }

@app.post("/corridas")
def salvar_corrida(corrida: CorridaCreate, db: Session = Depends(get_db)):
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
    return { "id": nova_corrida.id, "status": "corrida salva" }

# Total precisa vir antes do limit para o FastAPI não confundir com parâmetro
@app.get("/corridas/total")
def total_corridas(db: Session = Depends(get_db)):
    total = db.query(Corrida).count()
    return { "total": total }

@app.get("/corridas")
def listar_corridas(limit: int = 10, db: Session = Depends(get_db)):
    corridas = db.query(Corrida).limit(limit).all()
    return corridas