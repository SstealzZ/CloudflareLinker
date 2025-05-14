FROM node:18-alpine as build

WORKDIR /app

# Récupération des arguments de construction
ARG FRONTEND_PORT
ARG API_HOST

# Définition des variables d'environnement
ENV FRONTEND_PORT=$FRONTEND_PORT
ENV API_HOST=$API_HOST
ENV NODE_ENV=production

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY . .

# Construction de l'application
RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Récupération des arguments de construction
ARG FRONTEND_PORT

# Définition des variables d'environnement
ENV PORT=$FRONTEND_PORT

# Installation de serve
RUN npm install -g serve

# Copie des fichiers de build
COPY --from=build /app/dist ./dist

# Exposition du port
EXPOSE $PORT

# Commande par défaut
CMD ["sh", "-c", "serve -s dist -l $PORT"]