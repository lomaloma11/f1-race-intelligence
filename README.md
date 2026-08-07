# F1 Race Intelligence - Pipeline de Dados, Machine Learning e API

## Visão Geral

O **F1 Race Intelligence** é uma plataforma end-to-end de engenharia e ciência de dados projetada para coletar, processar e analisar dados de telemetria da Fórmula 1. O sistema consome dados brutos via API, transforma-os em uma arquitetura Medallion (Data Lakehouse em formato Parquet), treina modelos preditivos e analíticos de Machine Learning e disponibiliza os resultados por meio de uma API RESTful e um Dashboard interativo em Streamlit.

## Links de Acesso (Aplicações em Produção)

* **Dashboard Interativo (Streamlit):** http://13.58.103.10:8501
* **Documentação OpenAPI / Swagger (API Flask):** http://13.58.103.10:5000/apidocs/

---

## Arquitetura do Sistema

A solução foi desenvolvida em uma arquitetura **Multi-Container com Docker**, dividida nas seguintes etapas:

1. **Camada de Ingestão (Raw):** Coleta automatizada de dados de telemetria, tempos de volta, resultados e condições de clima via biblioteca FastF1.

2. **Engenharia de Dados (Medallion Architecture):**

   * **Silver:** Sanitização, remoção de voltas anômalas (pit stops, Safety Car) e padronização de tipos.
   * **Gold:** Agregação de métricas de ritmo, consistência (desvio padrão) e variáveis de sessão em formato Parquet particionado.

3. **Machine Learning:**

   * **Classificação:** Random Forest Classifier para estimar a probabilidade de um piloto terminar no Top 10.
   * **Regressão:** Estimativa das taxas de degradação temporal por composto de pneu (Soft e Hard).
   * **Clusterização:** Agrupamento não-supervisionado (K-Means) para identificação de perfis de pilotagem com base em ritmo e regularidade.

4. **Backend (API RESTful):** Servidor Flask estruturado com validação de dados via Pydantic e documentação interativa via Flasgger (Swagger).

5. **Frontend:** Dashboard analítico em Streamlit integrado à API para simulação em tempo real.

---

## Tecnologias Utilizadas

| Camada                     | Tecnologias                                             |
| :------------------------- | :------------------------------------------------------ |
| **Linguagem Principal**    | Python 3.11                                             |
| **Engenharia de Dados**    | FastF1, Pandas, PyArrow (Parquet), Particionamento Hive |
| **Machine Learning**       | Scikit-Learn, Joblib, NumPy                             |
| **API & Backend**          | Flask, Flask-CORS, Pydantic, Flasgger (Swagger UI)      |
| **Frontend & Analytics**   | Streamlit, Plotly                                       |
| **Infraestrutura & Cloud** | Docker, Docker Compose, AWS EC2, AWS S3                 |

---

## Estrutura do Projeto

```text
f1-race-intelligence/
├── data/
│   ├── raw/                   # Dados brutos coletados via FastF1
│   ├── silver/                # Dados tratados e sanitizados
│   └── gold/                  # Dados agregados para análise e ML
│
├── models/                    # Modelos de Machine Learning treinados
│
├── scripts/                   # Scripts de execução da pipeline e treinamento
│
├── src/
│   ├── api/
│   │   ├── routes/            # Endpoints da API Flask
│   │   ├── schemas/           # Validação e estruturas dos dados
│   │   └── services/          # Regras de negócio e serviços da API
│   │
│   ├── data_processing/       # Processamento e transformação dos dados
│   │
│   ├── frontend/              # Dashboard interativo em Streamlit
│   │
│   ├── ingestion/             # Coleta e ingestão dos dados via FastF1
│   │
│   ├──ml/                     # Algoritmos e treino de ML
│   │
│   └── utils/                 # Conexão com a AWS 
│
├── .env.example               # Exemplo das variáveis de ambiente
├── docker-compose.yml         # Orquestração dos containers
├── Dockerfile                 # Configuração da imagem Docker
├── requirements.txt           # Dependências do projeto
└── README.md                  # Documentação do projeto
```

---

## Endpoints da API

A documentação interativa completa dos endpoints pode ser consultada via Swagger em `/apidocs/`. Abaixo estão os principais serviços disponíveis:

### `POST /api/v1/predictions/top10`

**Descrição:** Recebe dados do cenário da corrida e retorna a probabilidade de o piloto pontuar no Top 10.

### `GET /api/v1/analytics/tires/<compound>`

**Descrição:** Retorna os coeficientes do modelo de regressão para a curva de degradação do pneu informado (`SOFT` ou `HARD`).

### `POST /api/v1/analytics/drivers/cluster`

**Descrição:** Classifica o perfil de pilotagem (Cluster 0, 1 ou 2) a partir do tempo médio e desvio padrão das voltas.

---

## Instruções de Execução Local

### Pré-requisitos

* Git
* Docker
* Docker Compose

### Execução via Docker Compose

1. **Clone o repositório:**

```bash
git clone https://github.com/SEU_USUARIO/f1-race-intelligence.git
cd f1-race-intelligence
```

2. **Crie o arquivo `.env`** na raiz do projeto com as variáveis de ambiente necessárias. Consulte o arquivo `.env.example` para verificar as variáveis esperadas.

3. **Suba os containers do sistema:**

```bash
docker compose up -d --build
```

4. **Acesse os serviços no navegador:**

| Serviço                       | URL                              |
| :---------------------------- | :------------------------------- |
| Dashboard Streamlit           | `http://localhost:8501`          |
| Documentação da API (Swagger) | `http://localhost:5000/apidocs/` |

---

## Serviços em Execução

Após executar o `docker compose up -d --build`, o projeto disponibilizará:

* **Streamlit:** Dashboard interativo para análise e simulação dos modelos.
* **Flask API:** Backend responsável por disponibilizar os modelos e serviços analíticos.
* **Swagger UI:** Interface para consulta e teste dos endpoints da API.

> **Nota:** Para acessar os serviços em produção, utilize os links disponibilizados na seção [Links de Acesso](#links-de-acesso-aplicações-em-produção). Para execução local, utilize `localhost` conforme indicado na seção [Instruções de Execução Local](#instruções-de-execução-local).

```
```
