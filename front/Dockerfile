FROM node:18-alpine as build

WORKDIR /app

# Install dependencies with npm install instead of npm ci
COPY package.json package-lock.json* ./
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