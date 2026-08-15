# Rideless API

Backend da aplicação Rideless — responsável por coletar corridas confirmadas, armazenar dados, treinar e servir o modelo de estimativa de preços.


## Visão Geral

A API recebe corridas confirmadas pelo app, persiste os dados localmente e expõe endpoints para consulta e predição. Os dados coletados alimentam o modelo de machine learning que refina progressivamente as estimativas de preço geradas pelo algoritmo estático do app.


## Requisitos

- Python 3.12+
- pip 24+


## Instalação

Clone o repositório e ative o ambiente virtual:

```bash
git clone https://github.com/seu-usuario/rideless.git
cd rideless
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Instale as dependências:

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv scikit-learn pandas joblib requests xgboost lightgbm scipy numpy
```

## Uso

Inicie o servidor:

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.

Documentação interativa disponível em `http://127.0.0.1:8000/docs`.


## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API |
| `POST` | `/rides` | Salva uma corrida confirmada |
| `GET` | `/rides` | Lista corridas (padrão: 10) |
| `GET` | `/rides/total` | Retorna o total de corridas salvas |
| `DELETE` | `/rides/reset` | Apaga todas as corridas do banco |
| `POST` | `/predict` | Retorna estimativa de preço via modelo de ML |


## Exemplos de Payload

### POST /rides

```json
{
  "origem_lat": -23.5505,
  "origem_lon": -46.6333,
  "destino_lat": -23.6273,
  "destino_lon": -46.6566,
  "distancia_km": 12.4,
  "duracao_min": 18.0,
  "hora": 8,
  "dia_semana": 1,
  "plataforma": "uber",
  "categoria": "uber-x",
  "cenario": "demanda_normal",
  "demanda": 80,
  "motoristas": 70,
  "multiplicador_regiao": 1.0,
  "multiplicador_hora": 1.4,
  "multiplicador_demanda": 1.0,
  "preco_estimado": 45.58,
  "preco_real": 48.20,
  "prob_aceitacao": 0.85
}
```

### POST /predict — Resposta

```json
{
  "predicted_price": 46.20,
  "price_min": 41.58,
  "price_max": 50.82,
  "acceptance_probability": 0.75,
  "demand_multiplier": 1.15,
  "confidence": 0.7435
}
```


## Estrutura do Projeto

```
rideless/
├── main.py         # Endpoints da API
├── models.py       # Modelo da tabela do banco de dados
├── schemas.py      # Validação dos dados de entrada
├── database.py     # Conexão com o banco SQLite
├── config.py       # Parâmetros configuráveis (tarifas, regiões, cenários)
├── simulate.py     # Geração de corridas sintéticas
└── train.py        # Treinamento e comparação de modelos de ML
```

## Simulação de Dados

Para popular o banco com corridas sintéticas:

```bash
python simulate.py
```

As simulações variam automaticamente:

- Região (centro, aeroporto, periferia, geral)
- Horário e dia da semana
- Cenário de demanda (baixa, normal, alta, pico extremo)
- Plataforma e categoria
- Multiplicadores de preço

Para alterar a quantidade de simulações, edite a última linha do arquivo:

```python
simular(10000)  # substitua pelo número desejado
```


## Treinamento do Modelo

Com o banco populado, treine e compare os modelos:

```bash
python train.py
```

O script compara automaticamente quatro modelos:

| Modelo | Descrição |
|---|---|
| Linear Regression | Baseline simples e interpretável |
| Random Forest | Ensemble de árvores de decisão |
| Gradient Boosting | Boosting com árvores sequenciais |
| XGBoost | Boosting otimizado e eficiente |

O melhor modelo é selecionado automaticamente pelo menor MAE e salvo em `model.pkl`.

### Métricas avaliadas

- **MAE (Mean Absolute Error)** — erro médio absoluto em reais. Representa quanto o modelo erra em média por corrida. Um MAE de R$ 4,99 significa que o modelo erra em média R$ 4,99 para mais ou para menos. Quanto menor, melhor.

- **RMSE (Root Mean Squared Error)** — similar ao MAE, mas penaliza erros grandes com mais severidade. Se o modelo acerta quase sempre mas ocasionalmente erra muito, o RMSE será bem maior que o MAE. Indica a magnitude dos erros maiores. Quanto menor, melhor.

- **R² (Coeficiente de Determinação)** — mede o quanto o modelo consegue explicar a variação dos preços. Vai de 0 a 1, onde 1 é um modelo perfeito e 0 é um modelo inútil. Um R² de 0.9914 significa que o modelo explica 99,14% da variação dos preços. Com dados reais esse valor tende a ser menor, pois o mundo real é mais imprevisível que simulações.

### Arquivos gerados

- `model.pkl` — melhor modelo treinado
- `le_plataforma.pkl` — encoder de plataformas
- `le_categoria.pkl` — encoder de categorias
- `le_cenario.pkl` — encoder de cenários
- `features.pkl` — lista de features usadas no treino

> Esses arquivos não são versionados no repositório.


## Como Funciona a Estimativa

O modelo recebe o preço estimado pelo algoritmo estático do app como uma das features e aprende a corrigi-lo com base em padrões históricos:

```
Algoritmo estático → preco_estimado
        ↓
POST /predict com todos os dados da corrida
        ↓
Modelo refina baseado em distância, horário,
demanda, região e histórico
        ↓
Retorna predicted_price + faixa de preço + confiança
```


## Estado Atual — MVP

O modelo é treinado com dados sintéticos gerados pelo `simulate.py`. A precisão aumentará progressivamente conforme dados reais de usuários forem coletados e incorporados ao treinamento.

Resultados atuais com 10.000 simulações:

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | R$ 4.99 | R$ 7.17 | 0.9914 |
| XGBoost | R$ 5.14 | R$ 7.52 | 0.9905 |
| Gradient Boosting | R$ 5.21 | R$ 7.65 | 0.9902 |
| Random Forest | R$ 5.22 | R$ 7.67 | 0.9901 |


## Licença

MIT
