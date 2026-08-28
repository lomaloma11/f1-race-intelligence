FROM python:3.11-slim

# Evita criação de arquivos .pyc e força flush imediato de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia e instala apenas as dependências pré-compiladas sem gerar cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip /tmp/*

# Copia o código da aplicação
COPY . /app/

# Expõe as portas dos serviços
EXPOSE 5000
EXPOSE 8501