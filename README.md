# F1 Race Intelligence — Pipeline de Dados, Machine Learning & Cloud
 
Plataforma *end-to-end* de engenharia e ciência de dados voltada para ingestão, processamento em arquitetura de Data Lakehouse e inferência analítica sobre telemetria da Fórmula 1.
 
O sistema coleta dados brutos via API, estrutura as camadas de dados (*Medallion Architecture*) em formato colunar Apache Parquet com persistência nativa no Amazon S3, treina modelos preditivos/analíticos de Machine Learning e disponibiliza os resultados por meio de uma API RESTful e um Dashboard interativo em Streamlit.
 
---
 
## Links de Acesso (Aplicações em Produção)
 
Os serviços estão ativos na AWS sob tráfego seguro com terminação SSL/TLS (HTTPS):
 
- **Dashboard Interativo (Streamlit):** [https://f1-race-intelligence.duckdns.org](https://f1-race-intelligence.duckdns.org)
- **Documentação OpenAPI / Swagger (API Flask):** [https://f1-race-intelligence.duckdns.org/apidocs/](https://f1-race-intelligence.duckdns.org/apidocs/)
---
 
## Arquitetura da Solução
 
O ecossistema foi projetado de forma modular e desacoplada em uma esteira de dados em nuvem:
 
```text
[ FastF1 API ]
      │ (Ingestão ELT)
      ▼
[ Amazon S3 Data Lakehouse ] ──> Raw Layer (Parquet / Particionamento Hive)
      │                               │
      │                               ▼
      │                         Silver Layer (Sanitização & Outlier Removal)
      │                               │
      │                               ▼
      │                         Gold Layer (Features Agregadas por Piloto/GP)
      ▼
[ Modelos de ML ] ──> Classificação (Top 10) | Regressão (Pneus) | K-Means (Clusters)
      │
      ▼
[ Backend Flask ] ──> Validação Pydantic & Documentação Swagger (/apidocs/)
      │
      ├──> [ Dashboard Streamlit ] (Simulação e Análises em Tempo Real)
      └──> [ Nginx Reverse Proxy ] (Roteamento Seguro com SSL/TLS via Certbot)
```
 
---
 
## Componentes Chave
 
### Ingestão & Data Lakehouse (ELT Cloud-Native)
 
- **Raw:** coleta automatizada de tempos de volta, telemetria, resultados e meteorologia via biblioteca FastF1, persistida em Apache Parquet com particionamento Hive (`year=YYYY/round=RR`) diretamente no Amazon S3.
- **Silver:** sanitização, descarte de voltas anômalas (pit-in/out, voltas sob Safety Car ou bandeiras amarelas) e padronização de tipos temporais com `fsspec` e PyArrow.
- **Gold:** matriz consolidada de features por piloto/corrida, modelando consistência (`std_lap_time_early`), delta de ritmo e contexto de pista.
### Machine Learning & Estratégia
 
- **Classificação (Top 10):** Random Forest Classifier modelado exclusivamente com métricas de voltas iniciais (*early laps*) para prevenir *data leakage* (vazamento de dados do resultado final da corrida).
- **Regressão Linear:** estimativa das taxas de degradação temporal por composto de pneu (Soft vs. Hard).
- **Clusterização (K-Means):** segmentação de perfis de pilotagem empacotada com `StandardScaler` para garantir consistência de escala na inferência.
### Backend & Segurança Web
 
- API RESTful em Flask com arquitetura em camadas (Services, Routes, Schemas).
- Validação estrita de contratos e tipos de entrada via Pydantic.
- Documentação interativa OpenAPI/Swagger via Flasgger.
- Camada de borda gerenciada por Proxy Reverso Nginx com certificado SSL/TLS automatizado via Certbot (Let's Encrypt).
### Frontend & DevOps
 
- Dashboard analítico em Streamlit com visualizações dinâmicas em Plotly.
- Orquestração multi-container via Docker Compose utilizando imagens enxutas baseadas em `python:3.11-slim`.
- Esteira automatizada de CI/CD no GitHub Actions com análise estática (Ruff), testes automatizados (Pytest) e rotina contínua de deploy via SSH no AWS EC2 com expurgo de volumes órfãos.
---
 
## Tecnologias Utilizadas
 
| Camada | Tecnologias / Bibliotecas |
|---|---|
| Linguagem Principal | Python 3.11 |
| Engenharia de Dados | FastF1, Pandas, PyArrow (Parquet), fsspec, Particionamento Hive |
| Machine Learning | Scikit-Learn, Joblib, NumPy |
| Backend & API | Flask, Flask-CORS, Pydantic, Flasgger (Swagger UI) |
| Frontend & Analytics | Streamlit, Plotly, Requests |
| Infraestrutura & Nuvem | AWS (EC2, S3), Docker, Docker Compose, Nginx, Certbot / DuckDNS |
| Qualidade & CI/CD | Pytest, Pytest-cov, Ruff, GitHub Actions |
 
---
 
## Estrutura do Repositório
 
```text
f1-race-intelligence/
├── .github/
│   └── workflows/             # Esteiras de CI (Ruff/Pytest) e CD (SSH Deploy)
├── data/                      # Estrutura do Data Lakehouse (espelhada no S3)
│   ├── raw/                   # Dados brutos coletados via FastF1
│   ├── silver/                # Dados tratados e sanitizados
│   └── gold/                  # Features analíticas consolidadas
├── models/                    # Modelos de Machine Learning treinados (.pkl)
├── scripts/                   # Scripts de execução da pipeline, treinamento e S3
├── src/
│   ├── api/                   # Aplicação Flask (Routes, Schemas e Services)
│   ├── data_processing/       # Cleaners e Feature Engineering
│   ├── frontend/               # Dashboard interativo em Streamlit
│   ├── ingestion/              # Coleta e ingestão de telemetria via FastF1
│   ├── ml/                     # Algoritmos de Machine Learning e inferência
│   └── utils/                  # Conexão e integração com Amazon S3
├── tests/                     # Testes unitários e de integração (Pytest)
├── .env.example               # Template das variáveis de ambiente necessárias
├── docker-compose.yml         # Orquestração multi-container da aplicação
├── Dockerfile                  # Configuração otimizada da imagem Docker
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação do projeto
```
 
---
 
## Endpoints da API
 
A documentação interativa completa dos esquemas e rotas está disponível via Swagger em `/apidocs/`:
 
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/predictions/top10` | Estima a probabilidade de um piloto pontuar com base no grid e ritmo inicial |
| `GET` | `/api/v1/analytics/tires/{compound}` | Retorna os coeficientes da curva de degradação do composto informado (`SOFT` ou `HARD`) |
| `POST` | `/api/v1/analytics/drivers/cluster` | Classifica o perfil de pilotagem a partir do tempo médio e consistência das voltas |
 
---
 
## Instruções de Execução Local
 
### Pré-requisitos
 
- Git
- Docker e Docker Compose instalados
### 1. Clonar o Repositório
 
```bash
git clone https://github.com/lomaloma11/f1-race-intelligence.git
cd f1-race-intelligence
```
 
### 2. Configurar Variáveis de Ambiente
 
Crie o arquivo `.env` na raiz do projeto com base no template de exemplo:
 
```bash
cp .env.example .env
```
 
### 3. Iniciar os Serviços com Docker Compose
 
Suba toda a infraestrutura multi-container em segundo plano:
 
```bash
docker compose up -d --build
```
 
### 4. Acessar os Serviços Localmente
 
| Serviço | URL Local |
|---|---|
| Dashboard Streamlit | http://localhost:8501 |
| Documentação da API (Swagger) | http://localhost:5000/apidocs/ |
 
---
 
## Pipeline de Execução Manual (Opcional)
 
Para executar etapas específicas do fluxo de dados ou testes sem depender da interface gráfica:
 
```bash
# 1. Ingestão e Processamento Medallion (Raw -> Silver -> Gold)
python -m scripts.process_data -y 2023 -m R
 
# 2. Treinamento de todos os modelos de Machine Learning
python -m scripts.train_model -m all
 
# 3. Execução da suíte de testes com cobertura de código
pytest -v --cov=src tests/
```
