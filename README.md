# Rideless API

API de **previsão de preço** do [Rideless](https://github.com/bruno-heic/2026-3B-ETEC-INTER-APP). Ela guarda corridas, treina um modelo de machine learning e o serve por HTTP para refinar o preço estimado pelo algoritmo estático do app.

> Existe uma segunda API no ecossistema, a [Location Risk API](https://github.com/bruno-heic/2026-3B-ETEC-INTER-LOCATION-RISK-API), que cuida de risco de localização e recomendações de embarque. As duas são independentes e rodam em servidores separados.

## Índice

- [Visão geral](#visão-geral)
- [Requisitos](#requisitos)
- [Início rápido](#início-rápido)
- [Instalação passo a passo](#instalação-passo-a-passo)
- [Rodando a API](#rodando-a-api)
- [Gerando dados de treino](#gerando-dados-de-treino)
- [Treinando o modelo](#treinando-o-modelo)
- [Testando a API](#testando-a-api)
- [Conectando o app mobile](#conectando-o-app-mobile)
- [Referência da API](#referência-da-api)
- [Como funciona a estimativa](#como-funciona-a-estimativa)
- [Configuração dos dados simulados](#configuração-dos-dados-simulados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Estado atual (MVP)](#estado-atual-mvp)
- [Solução de problemas](#solução-de-problemas)
- [Licença](#licença)

## Visão geral

O fluxo completo tem cinco etapas:

```
simulate.py            gera corridas sintéticas e envia para POST /rides
      ↓
rideless.db            banco SQLite com as corridas
      ↓
train.py               compara 4 modelos e salva o melhor
      ↓
model.pkl + .pkl       modelo e encoders carregados pela API ao iniciar
      ↓
POST /predict          o app envia a corrida e recebe o preço refinado
```

Hoje o banco é populado pelo `simulate.py`. O endpoint `POST /rides` já está pronto para receber corridas reais quando o app passar a enviá-las, e o modelo poderá ser retreinado com elas.

## Requisitos

| Item | Versão / detalhe |
|---|---|
| Python | 3.12 ou superior (`python --version`) |
| pip | 24 ou superior (`pip --version`) |
| Internet | necessária só para o `simulate.py` (consulta o OSRM) |

## Início rápido

```bash
git clone https://github.com/bruno-heic/2026-3B-ETEC-INTER-PRICE-API.git
cd 2026-3B-ETEC-INTER-PRICE-API
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Depois, em **dois terminais** (ambos com o `venv` ativo, na raiz do projeto):

```bash
# Terminal 1: sobe a API (cria o banco na primeira execução)
uvicorn main:app --host 0.0.0.0

# Terminal 2: gera 1000 corridas e treina o modelo
python simulate.py 1000
python train.py
```

Por fim, **reinicie a API** no terminal 1 (`Ctrl+C` e o comando `uvicorn` de novo) para ela carregar o modelo. Teste em http://127.0.0.1:8000/docs.

## Instalação passo a passo

**1. Clone o repositório e entre na pasta**

```bash
git clone https://github.com/bruno-heic/2026-3B-ETEC-INTER-PRICE-API.git
cd 2026-3B-ETEC-INTER-PRICE-API
```

**2. Crie o ambiente virtual**

```bash
python -m venv venv
```

**3. Ative o ambiente virtual**

| Sistema | Comando |
|---|---|
| Linux / macOS | `source venv/bin/activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Windows (cmd) | `venv\Scripts\activate.bat` |

O terminal deve mostrar `(venv)` no início da linha. Se o PowerShell bloquear o script, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**4. Instale as dependências**

```bash
pip install -r requirements.txt
```

Sem o arquivo:

```bash
pip install fastapi uvicorn sqlalchemy pandas numpy scikit-learn xgboost joblib requests
```

> Rode **todos** os comandos a partir da raiz do projeto. O banco (`rideless.db`) e os arquivos do modelo são lidos e gravados com caminhos relativos.

## Rodando a API

### Desenvolvimento local (só o seu computador)

```bash
uvicorn main:app --reload
```

Fica em `http://127.0.0.1:8000`.

### Acessível pelo celular

```bash
uvicorn main:app --reload --host 0.0.0.0
```

O `--host 0.0.0.0` faz a API aceitar conexões de outros dispositivos da rede.

### Outra porta

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Se mudar a porta, ajuste também o `API_URL` do `simulate.py` (`http://127.0.0.1:8000/rides`).

### Produção (sem recarga automática)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Estado do modelo

Ao iniciar, a API tenta carregar `model.pkl` e os encoders. Se eles não existirem, ela sobe normalmente, mas o `POST /predict` responde **503** até o modelo ser treinado.

> O `--reload` só observa arquivos `.py`. Depois de treinar um novo modelo, **reinicie a API manualmente** para ela carregar os `.pkl` atualizados.

## Gerando dados de treino

O `simulate.py` cria corridas sintéticas e as envia para `POST /rides`. **A API precisa estar rodando em `http://127.0.0.1:8000`.**

```bash
python simulate.py 1000     # quantidade de corridas (padrão: 10000)
```

Para cada corrida, o script:

1. escolhe uma região de origem e uma de destino
2. busca a rota real no OSRM (distância e duração)
3. sorteia horário, dia da semana, plataforma e cenário de demanda
4. calcula o preço estimado com as tarifas e multiplicadores do `config.py`
5. gera o preço "real" aplicando uma variação aleatória de 0,92× a 1,12×
6. envia tudo para a API

**Cuidados:**

- Ele consulta o servidor público do OSRM (`router.project-osrm.org`) uma vez por corrida. Para 10.000 corridas pode levar bastante tempo e o servidor demo pode limitar o uso. **Comece com 500 a 1000.**
- Corridas cuja rota não foi encontrada são puladas (o script avisa e continua).
- O gerador usa `random.seed(42)`, então **rodar o script duas vezes insere as mesmas corridas de novo** e duplica os dados. Para recomeçar do zero, pare a API e apague o banco:

```bash
rm rideless.db        # Windows: del rideless.db
```

Confira quantas corridas foram salvas:

```bash
curl http://127.0.0.1:8000/rides/total
```

## Treinando o modelo

Com o banco populado:

```bash
python train.py
```

O script:

1. lê todas as corridas de `rideless.db`
2. descarta linhas com campos obrigatórios nulos
3. converte plataforma, categoria e cenário em números (`LabelEncoder`)
4. separa 80% para treino e 20% para teste
5. treina e compara quatro modelos
6. escolhe o de **menor MAE** e salva os arquivos

| Modelo | Descrição |
|---|---|
| Linear Regression | Baseline simples e interpretável |
| Random Forest | Ensemble de árvores de decisão |
| Gradient Boosting | Boosting com árvores sequenciais |
| XGBoost | Boosting otimizado e eficiente |

### Features usadas (14)

`distancia_km`, `duracao_min`, `hora`, `dia_semana`, `plataforma`, `categoria`, `cenario`, `demanda`, `motoristas`, `multiplicador_regiao`, `multiplicador_hora`, `multiplicador_demanda`, `prob_aceitacao` e `preco_estimado`. O alvo é o `preco_real`.

### Métricas

- **MAE:** erro médio absoluto, em reais. Quanto o modelo erra, em média, por corrida.
- **RMSE:** como o MAE, mas penaliza mais os erros grandes.
- **R²:** quanto da variação dos preços o modelo explica (de 0 a 1).

### Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `model.pkl` | Melhor modelo treinado |
| `le_plataforma.pkl` | Encoder de plataformas |
| `le_categoria.pkl` | Encoder de categorias |
| `le_cenario.pkl` | Encoder de cenários |
| `features.pkl` | Lista de features usadas no treino |

Esses arquivos e o `rideless.db` não são versionados no repositório. Cada pessoa precisa gerá-los localmente. Depois de treinar, **reinicie a API**.

## Testando a API

### Pela documentação interativa

Abra http://127.0.0.1:8000/docs, escolha um endpoint, clique em **Try it out** e execute.

### Pelo terminal

Status da API:

```bash
curl http://127.0.0.1:8000/
```

Total de corridas salvas:

```bash
curl http://127.0.0.1:8000/rides/total
```

Previsão de preço:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origem_lat": -23.5505, "origem_lon": -46.6333,
    "destino_lat": -23.6273, "destino_lon": -46.6566,
    "distancia_km": 12.4, "duracao_min": 18.0,
    "hora": 8, "dia_semana": 1,
    "plataforma": "uber", "categoria": "uber-x",
    "cenario": "demanda_normal", "demanda": 80, "motoristas": 70,
    "multiplicador_regiao": 1.0, "multiplicador_hora": 1.4,
    "preco_estimado": 45.58, "preco_real": 45.58
  }'
```

No **Windows PowerShell**:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict `
  -ContentType "application/json" `
  -Body '{"origem_lat":-23.5505,"origem_lon":-46.6333,"destino_lat":-23.6273,"destino_lon":-46.6566,"distancia_km":12.4,"duracao_min":18.0,"hora":8,"dia_semana":1,"plataforma":"uber","categoria":"uber-x","cenario":"demanda_normal","demanda":80,"motoristas":70,"multiplicador_regiao":1.0,"multiplicador_hora":1.4,"preco_estimado":45.58,"preco_real":45.58}'
```

## Conectando o app mobile

O app precisa de uma URL que o celular alcance. Configure em `services/predict.ts`, sem barra no final:

```typescript
const API_URL = "http://192.168.0.10:8000"; // use o seu IP
```

### Opção 1: mesma rede Wi-Fi

1. Rode a API com `--host 0.0.0.0`.
2. Descubra o IP do computador:

| Sistema | Comando |
|---|---|
| Windows | `ipconfig` (campo "Endereço IPv4") |
| macOS | `ipconfig getifaddr en0` |
| Linux | `hostname -I` |

3. No Windows, permita o Python no firewall para **redes privadas** quando o aviso aparecer.
4. Teste no navegador do celular: `http://SEU_IP:8000/docs`.

### Opção 2: GitHub Codespaces

1. Inicie a API: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Abra a aba **Ports** no VS Code.
3. Clique com o botão direito na porta **8000** e escolha **Port Visibility → Public**.
4. Use a URL gerada (`https://...-8000.app.github.dev`) como `API_URL`.

Se o Codespace reiniciar, confira a visibilidade da porta de novo. O modelo e o banco também precisam ser gerados dentro do Codespace.

### Opção 3: túnel (ngrok, Cloudflare Tunnel etc.)

Exponha a porta 8000 e use a URL `https` gerada.

> Para builds de produção do app, use sempre **HTTPS**.

Se a API estiver fora do ar ou responder erro, o app usa o preço do algoritmo estático automaticamente.

## Referência da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API |
| `POST` | `/rides` | Salva uma corrida |
| `GET` | `/rides` | Lista corridas (`?limit=10`, padrão 10) |
| `GET` | `/rides/total` | Total de corridas salvas |
| `POST` | `/predict` | Previsão de preço via modelo de ML |

### Corpo de `POST /rides` e `POST /predict`

Os dois endpoints usam o mesmo formato de entrada (`CorridaCreate`).

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `origem_lat`, `origem_lon` | número | sim | Coordenadas da origem |
| `destino_lat`, `destino_lon` | número | sim | Coordenadas do destino |
| `distancia_km` | número | sim | Distância da rota |
| `duracao_min` | número | sim | Duração da rota, em minutos |
| `hora` | inteiro | sim | Hora do dia (0 a 23) |
| `dia_semana` | inteiro | sim | 0 = segunda … 6 = domingo |
| `plataforma` | texto | sim | `uber` ou `99` |
| `categoria` | texto | sim | Uma das categorias da [tabela abaixo](#plataformas-e-categorias-válidas) |
| `preco_estimado` | número | sim | Preço do algoritmo estático |
| `preco_real` | número | sim | Preço real da corrida. No `/predict` é exigido pelo schema, mas **não é usado** (envie o mesmo valor de `preco_estimado`) |
| `cenario` | texto | não* | Nome de um [cenário de demanda](#cenários-de-demanda) |
| `demanda` | inteiro | não | Padrão no `/predict`: 80 |
| `motoristas` | inteiro | não | Padrão no `/predict`: 70 |
| `multiplicador_regiao` | número | não | Padrão no `/predict`: 1.0 |
| `multiplicador_hora` | número | não | Padrão no `/predict`: 1.0 |
| `multiplicador_demanda` | número | não | No `/predict` é recalculado a partir de `demanda` e `motoristas` |
| `prob_aceitacao` | número | não | Padrão no `/predict`: 0.85 |

\* No `/predict`, **envie sempre um cenário válido.** Se ele for omitido, a API usa `"desconhecido"`, valor que não existe nos dados simulados, e a chamada falha com 422.

Exemplo de `POST /rides`:

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

Resposta:

```json
{ "id": 1, "status": "ride saved" }
```

### Resposta de `POST /predict`

Valores ilustrativos:

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

| Campo | Descrição |
|---|---|
| `predicted_price` | Preço previsto pelo modelo |
| `price_min` | 90% do previsto (mínimo R$ 5,00) |
| `price_max` | 110% do previsto (máximo R$ 300,00) |
| `acceptance_probability` | Probabilidade de aceitação, calculada por regra (veja abaixo) |
| `demand_multiplier` | Multiplicador de demanda aplicado |
| `confidence` | Indicador de confiança, calculado por heurística (veja abaixo) |

### Erros do `/predict`

| Código | Causa |
|---|---|
| `503` | Modelo ainda não treinado. Rode `python train.py` e reinicie a API |
| `422` | Campo ausente ou com tipo errado, ou plataforma, categoria ou cenário que o modelo não conhece |

### Plataformas e categorias válidas

O modelo só conhece as combinações usadas no treino (definidas em `config.py`):

| Plataforma | Categoria | Base (R$) | Por km (R$) | Por min (R$) |
|---|---|---|---|---|
| `uber` | `uber-moto` | 3,50 | 1,10 | 0,15 |
| `uber` | `uber-x` | 4,50 | 1,90 | 0,25 |
| `uber` | `uber-confort` | 7,50 | 2,80 | 0,45 |
| `uber` | `uber-black` | 12,00 | 4,20 | 0,70 |
| `99` | `99-moto` | 3,20 | 1,00 | 0,12 |
| `99` | `99-pop` | 4,00 | 1,80 | 0,22 |
| `99` | `99-plus` | 6,50 | 2,40 | 0,38 |

Os nomes precisam ser **idênticos** (por exemplo `uber-confort`, sem o "m"). Para suportar uma nova categoria, adicione-a ao `config.py`, gere novos dados e retreine.

### Cenários de demanda

| Cenário | Demanda | Motoristas | Peso na simulação |
|---|---|---|---|
| `baixa_demanda` | 30 | 80 | 10% |
| `demanda_normal` | 80 | 70 | 35% |
| `alta_demanda` | 150 | 60 | 25% |
| `pico_extremo` | 300 | 40 | 10% |
| `poucos_motoristas` | 100 | 20 | 10% |
| `excesso_motorista` | 40 | 120 | 10% |

## Como funciona a estimativa

```
App calcula o preço estático  →  preco_estimado
        ↓
POST /predict com os dados da corrida
        ↓
O modelo recebe as 14 features e prevê o preço
        ↓
A API monta a resposta: previsto, faixa, aceitação e confiança
```

### Preço estático (usado na simulação e no app)

```
preço = (base + por_km × distância + por_min × duração)
        × multiplicador_hora × multiplicador_dia
        × multiplicador_região × multiplicador_demanda
```

limitado entre R$ 5,00 e R$ 300,00. O multiplicador de demanda vem da razão demanda/motoristas:

| Razão demanda/motoristas | Multiplicador |
|---|---|
| menor que 0,5 | 0,85 |
| 0,5 a 1,0 | 1,00 |
| 1,0 a 1,5 | 1,15 |
| 1,5 a 2,0 | 1,30 |
| 2,0 a 3,0 | 1,50 |
| 3,0 ou mais | 1,70 |

### Campos calculados por regra, não pelo modelo

- **Faixa de preço:** sempre ±10% do previsto, sem relação com a incerteza do modelo.
- **Probabilidade de aceitação:** começa em 0,85, cai 0,20 se o preço passa de R$ 5/km (ou 0,10 se passa de R$ 3/km), sobe 0,10 se a razão demanda/motoristas passa de 2 e cai 0,15 se for menor que 0,5.
- **Confiança:** `0,9914 × probabilidade de aceitação`. O 0,9914 é o R² obtido no treino e está fixo no código. Trate o valor como um indicador relativo, não como uma confiança estatística.

## Configuração dos dados simulados

O arquivo `config.py` controla toda a simulação:

| Parâmetro | O que define |
|---|---|
| `GEO` | Limites geográficos de São Paulo |
| `REGIOES` | Áreas (centro, aeroporto, periferia, geral) e seus multiplicadores (1,2 / 1,4 / 0,85 / 1,0) |
| `PLATFORMS` | Plataformas, categorias e tarifas |
| `HORA_MULTIPLICADOR` | Multiplicador por faixa de horário |
| `DIA_MULTIPLICADOR` | Multiplicador por dia da semana |
| `CENARIOS` | Cenários de demanda e seus pesos |
| `VARIACAO_PRECO` | Variação do preço real em relação ao estimado (0,92 a 1,12) |
| `PRECO_MINIMO`, `PRECO_MAXIMO` | Limites de preço (R$ 5,00 e R$ 300,00) |

Depois de alterar qualquer valor: apague o `rideless.db`, rode `simulate.py` de novo, rode `train.py` e reinicie a API.

## Estrutura do projeto

```
.
├── main.py            # Endpoints da API (FastAPI)
├── models.py          # Tabela `corridas` (SQLAlchemy)
├── schemas.py         # Validação dos dados de entrada (Pydantic)
├── database.py        # Conexão com o banco SQLite
├── config.py          # Tarifas, regiões, cenários e limites da simulação
├── simulate.py        # Geração de corridas sintéticas
├── train.py           # Treinamento e comparação de modelos
├── requirements.txt   # Dependências
├── LICENSE
└── README.md
```

Arquivos gerados localmente e não versionados: `rideless.db`, `model.pkl`, `le_plataforma.pkl`, `le_categoria.pkl`, `le_cenario.pkl` e `features.pkl`.

## Estado atual (MVP)

O modelo é treinado com **dados sintéticos** gerados pelo `simulate.py`. Resultados com 10.000 simulações:

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | R$ 4,99 | R$ 7,17 | 0,9914 |
| XGBoost | R$ 5,14 | R$ 7,52 | 0,9905 |
| Gradient Boosting | R$ 5,21 | R$ 7,65 | 0,9902 |
| Random Forest | R$ 5,22 | R$ 7,67 | 0,9901 |

**Como interpretar esses números:**

- O R² altíssimo mostra que o modelo aprendeu a **fórmula do simulador**, não o comportamento real das plataformas. O preço "real" simulado é o preço estimado multiplicado por um fator aleatório, e o próprio `preco_estimado` entra como feature. Por isso a regressão linear vence: a relação é quase linear.
- Com dados reais o R² tende a ser bem menor. As métricas atuais **não** representam a precisão que o modelo terá em corridas de verdade.
- Cobertura geográfica: apenas a cidade de São Paulo.

**Próxima etapa:** coletar corridas reais confirmadas pelos usuários (`POST /rides`), incorporá-las ao banco e retreinar o modelo, substituindo progressivamente os dados simulados.

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError` | `venv` inativo ou dependências não instaladas | Ative o `venv` e rode `pip install -r requirements.txt` |
| `FileNotFoundError: model.pkl` ao subir a API | Versão do `main.py` sem o carregamento tolerante | Aplique o ajuste do `main.py` ou rode `train.py` antes (exige o banco populado) |
| `/predict` responde 503 | Modelo ainda não treinado | Rode `python train.py` e **reinicie** a API |
| `/predict` responde 422 | Payload incompleto, ou plataforma, categoria ou cenário desconhecidos | Confira os campos e os valores das tabelas acima |
| `simulate.py` mostra "Erro de conexão" | API fora do ar ou em outra porta | Suba a API em `127.0.0.1:8000` antes de simular |
| `simulate.py` mostra "Rota não encontrada, pulando..." | Sem internet, OSRM indisponível ou limite de uso | Verifique a conexão, diminua a quantidade ou tente depois |
| `simulate.py` muito lento | Uma consulta ao OSRM por corrida | Comece com 500 a 1000 corridas |
| `train.py`: `no such table: corridas` | A API nunca foi iniciada, então a tabela não existe | Suba a API uma vez e gere dados |
| `train.py` falha com "0 registros" | Banco vazio | Rode `python simulate.py 1000` com a API ativa |
| Dados duplicados no banco | `simulate.py` rodado mais de uma vez (seed fixa) | Apague o `rideless.db` e gere de novo |
| Treinei, mas a API usa o modelo antigo | A API carrega os `.pkl` só ao iniciar | Reinicie a API |
| App não conecta, mas `/docs` abre no PC | API sem `--host 0.0.0.0` ou firewall bloqueando | Reinicie com `--host 0.0.0.0` e libere o Python no firewall |
| App não conecta no Codespaces | Porta 8000 privada | **Ports** → botão direito na 8000 → **Port Visibility → Public** |
| `Address already in use` | Porta 8000 ocupada | Use `--port 8001` |

## Licença

MIT
