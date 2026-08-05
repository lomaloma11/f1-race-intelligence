# 1. Imagem base oficial do Python super leve (slim)
FROM python:3.14-slim

# 2. Evita que o Python gere arquivos .pyc e força o log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Define a pasta de trabalho dentro do container
WORKDIR /app

# 4. Instala dependências do sistema operacional necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia o requirements.txt e instala as dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo o código-fonte do projeto para dentro do container
COPY . /app/

# 7. Expõe as portas da API (5000) e do Streamlit (8501)
EXPOSE 5000
EXPOSE 8501