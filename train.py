import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib

# Conecta direto no banco para ler os dados
# Pensa nisso como um SELECT * FROM corridas
engine = create_engine("sqlite:///./rideless.db")

print("Lendo dados do banco...")
df = pd.read_sql("SELECT * FROM corridas", engine)
print(f"Total de registros: {len(df)}")

# LabelEncoder transforma texto em número
# O modelo não entende "uber" ou "99-pop" — só números
# Então "uber" vira 2, "99" vira 0, "indrive" vira 1, por exemplo
le_plataforma = LabelEncoder()
le_categoria = LabelEncoder()

df["plataforma_enc"] = le_plataforma.fit_transform(df["plataforma"])
df["categoria_enc"] = le_categoria.fit_transform(df["categoria"])

# Features são as variáveis que o modelo usa para prever o preço
# Target é o que queremos prever — o preço real
features = [
    "distancia_km",
    "duracao_min",
    "hora",
    "dia_semana",
    "plataforma_enc",
    "categoria_enc",
    "preco_estimado",  # inclui o estimado como referência
]
target = "preco_real"

X = df[features]
y = df[target]

# Divide os dados em treino (80%) e teste (20%)
# O modelo aprende com os 80% e é avaliado nos 20% que nunca viu
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Treinando modelo...")
model = GradientBoostingRegressor(
    n_estimators=500,    # mais árvores
    learning_rate=0.05,  # passo menor = aprende melhor
    max_depth=6,         # árvores mais profundas
    random_state=42
)
model.fit(X_train, y_train)

# Avalia o modelo — MAE é o erro médio em reais
# Ex: MAE de 2.50 significa que o modelo erra em média R$ 2,50
predicoes = model.predict(X_test)
mae = mean_absolute_error(y_test, predicoes)
print(f"Erro médio (MAE): R$ {mae:.2f}")

# Salva o modelo e os encoders em arquivos
# joblib é como um "JSON" para modelos de ML
joblib.dump(model, "model.pkl")
joblib.dump(le_plataforma, "le_plataforma.pkl")
joblib.dump(le_categoria, "le_categoria.pkl")

print("Modelo salvo em model.pkl")