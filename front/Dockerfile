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

# Installation des dépendances (incluant les devDependencies nécessaires pour le build)
RUN npm install --include=dev

# Copie des fichiers de configuration avant le code source
COPY postcss.config.js tailwind.config.js vite.config.js ./

# Copie du code source
COPY . .

# Construction de l'application
RUN npm run build

# Étape 2: Servir l'application avec Nginx
FROM nginx:alpine

# Récupération des arguments de construction
ARG FRONTEND_PORT
ARG API_HOST

# Définition des variables d'environnement
ENV PORT=$FRONTEND_PORT
ENV API_HOST=$API_HOST

# Copie des fichiers de build depuis l'étape de build
COPY --from=build /app/dist /usr/share/nginx/html

# Copie de la configuration nginx
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Configuration de l'environnement Nginx
RUN echo 'env PORT=$PORT;' >> /etc/nginx/nginx.conf && \
    echo 'env API_HOST=$API_HOST;' >> /etc/nginx/nginx.conf

# Exposition du port
EXPOSE $PORT

# Démarrage de Nginx
CMD [ "sh", "-c", "envsubst '$PORT $API_HOST' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'" ]