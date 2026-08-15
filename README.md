# Price API

Backend da aplicação Rideless responsável por coletar corridas confirmadas, armazenar dados e treinar o modelo de estimativa de preços.



## Visão Geral

A API recebe corridas confirmadas pelo app, persiste os dados localmente e expõe endpoints para consulta. Os dados coletados alimentam o modelo de machine learning que substituirá futuramente o algoritmo estático de estimativa de preços.



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
pip install fastapi uvicorn sqlalchemy python-dotenv scikit-learn pandas joblib requests
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
| `POST` | `/predict` | Retorna o valor estimado de uma corrida |

### Exemplo de payload — POST /corridas

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
  "preco_estimado": 32.50,
  "preco_real": 35.00
}
```



## Estrutura do Projeto

```
rideless/
├── main.py         # Endpoints da API
├── models.py       # Modelo da tabela do banco de dados
├── schemas.py      # Validação dos dados de entrada
├── database.py     # Conexão com o banco SQLite
├── simulate.py     # Geração de corridas sintéticas
└── train.py        # Treinamento do modelo de ML
```



## Simulação de Dados

Para popular o banco com corridas sintéticas:

```bash
python simulate.py
```

Por padrão gera 100 corridas. Para alterar a quantidade, edite a última linha do arquivo:

```python
simular(100)  # substitua pelo número desejado
```



## Treinamento do Modelo

Com o banco populado, treine o modelo:

```bash
python train.py
```

O script exibe o erro médio absoluto (MAE) em reais ao final. Quanto menor, mais preciso o modelo.

Os arquivos gerados são:

- `model.pkl` — modelo treinado
- `le_plataforma.pkl` — encoder de plataformas
- `le_categoria.pkl` — encoder de categorias

> Esses arquivos não são versionados no repositório.



## Estado Atual

Esta é a versão MVP da API. O modelo de ML ainda é treinado com dados sintéticos. A precisão aumentará progressivamente conforme dados reais de usuários forem coletados e incorporados ao treinamento.



## Licença

MIT
