FROM python:3.12-slim

# Installation de curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Récupération des arguments de construction
ARG BACKEND_PORT

# Définition des variables d'environnement
ENV PORT=$BACKEND_PORT

WORKDIR /app

# Copie des fichiers de l'application
COPY . /app/

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port dynamique
EXPOSE $PORT

# La commande de démarrage est définie dans docker-compose.yml