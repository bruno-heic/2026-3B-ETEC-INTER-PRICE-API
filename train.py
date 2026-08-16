import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
import joblib

# Conecta no banco
engine = create_engine("sqlite:///./rideless.db")

print("Lendo dados do banco...")
df = pd.read_sql("SELECT * FROM corridas", engine)
print(f"Total de registros: {len(df)}")

# Remove registros com campos nulos
df = df.dropna(subset=[
    "distancia_km", "duracao_min", "hora", "dia_semana",
    "plataforma", "categoria", "preco_estimado", "preco_real",
    "multiplicador_regiao", "multiplicador_hora", "multiplicador_demanda",
    "demanda", "motoristas", "prob_aceitacao"
])
print(f"Registros após limpeza: {len(df)}")

# Transforma texto em número
le_plataforma = LabelEncoder()
le_categoria = LabelEncoder()
le_cenario = LabelEncoder()

df["plataforma_enc"] = le_plataforma.fit_transform(df["plataforma"])
df["categoria_enc"] = le_categoria.fit_transform(df["categoria"])
df["cenario_enc"] = le_cenario.fit_transform(df["cenario"].fillna("desconhecido"))

# Features completas — muito mais ricas que antes
features = [
    "distancia_km",
    "duracao_min",
    "hora",
    "dia_semana",
    "plataforma_enc",
    "categoria_enc",
    "cenario_enc",
    "demanda",
    "motoristas",
    "multiplicador_regiao",
    "multiplicador_hora",
    "multiplicador_demanda",
    "prob_aceitacao",
    "preco_estimado",
]
target = "preco_real"

X = df[features]
y = df[target]

# Divide em treino (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modelos para comparar
modelos = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42, verbosity=0),
}

print("\n--- Comparando modelos ---\n")

resultados = {}

for nome, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    pred = modelo.predict(X_test)

    mae  = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2   = r2_score(y_test, pred)

    resultados[nome] = { "modelo": modelo, "mae": mae, "rmse": rmse, "r2": r2 }

    print(f"{nome}")
    print(f"  MAE:  R$ {mae:.2f}")
    print(f"  RMSE: R$ {rmse:.2f}")
    print(f"  R²:   {r2:.4f}")
    print()

# Escolhe o melhor modelo pelo menor MAE
melhor_nome = min(resultados, key=lambda k: resultados[k]["mae"])
melhor = resultados[melhor_nome]

print(f"--- Melhor modelo: {melhor_nome} ---")
print(f"MAE: R$ {melhor['mae']:.2f}")
print(f"RMSE: R$ {melhor['rmse']:.2f}")
print(f"R²: {melhor['r2']:.4f}")

# Salva o melhor modelo e os encoders
joblib.dump(melhor["modelo"], "model.pkl")
joblib.dump(le_plataforma, "le_plataforma.pkl")
joblib.dump(le_categoria, "le_categoria.pkl")
joblib.dump(le_cenario, "le_cenario.pkl")
joblib.dump(features, "features.pkl")

print(f"\nModelo '{melhor_nome}' salvo em model.pkl")