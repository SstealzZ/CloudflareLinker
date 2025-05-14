FROM node:18-alpine as build

WORKDIR /app

# Récupération des arguments de construction
ARG REACT_APP_API_URL

# Définition des variables d'environnement pour la phase de build
ENV REACT_APP_API_URL=$REACT_APP_API_URL

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Récupération des arguments de construction
ARG FRONTEND_PORT

# Définition des variables d'environnement
ENV PORT=$FRONTEND_PORT

RUN npm install -g serve

COPY --from=build /app/build ./build

# Exposition du port dynamique
EXPOSE $PORT

CMD ["sh", "-c", "serve -s build -l $PORT"]