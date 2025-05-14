FROM python:3.12-slim

# Récupération des arguments de construction
ARG BACKEND_PORT

# Définition des variables d'environnement
ENV PORT=$BACKEND_PORT

# Installation de curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exposition du port dynamique
EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]