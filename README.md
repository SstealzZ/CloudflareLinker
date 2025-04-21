# Cloudflare Linker

Une application web minimaliste pour automatiser la gestion des DNS via l'API Cloudflare, en fonction d'IPs tournantes.

## Fonctionnalités

- Authentification sécurisée
- Gestion des enregistrements DNS via l'API Cloudflare
- Mise à jour automatique des DNS en fonction des changements d'IP
- Interface utilisateur moderne avec thème sombre
- Journalisation des activités et erreurs

## Architecture

### Backend
- FastAPI (Python)
- SQLite pour le stockage des données
- SQLAlchemy ORM
- JWT pour l'authentification

### Frontend
- React
- Tailwind CSS
- Radix UI
- React Router

## Prérequis

- Docker et Docker Compose
- Clé API Cloudflare

## Installation et démarrage rapide

1. Clonez ce dépôt :
```bash
git clone https://github.com/votreusername/cloudflare-linker.git
cd cloudflare-linker
```

2. Démarrez l'application avec Docker Compose :
```bash
docker-compose up -d
```

3. Accédez à l'application dans votre navigateur :
```
http://localhost
```

4. Lors de la première connexion, créez un compte et saisissez votre clé API Cloudflare.

## Structure du projet

```
cloudflare-linker/
├── docker-compose.yml       # Configuration Docker Compose
├── fastapi/                 # Backend (FastAPI)
│   ├── app/                 # Code source du backend
│   │   ├── api/             # Endpoints API
│   │   ├── core/            # Configuration et utilitaires
│   │   ├── models/          # Modèles de base de données
│   │   ├── schemas/         # Schémas Pydantic
│   │   ├── services/        # Services métier
│   │   └── main.py          # Point d'entrée de l'application
│   ├── Dockerfile           # Configuration Docker pour le backend
│   └── requirements.txt     # Dépendances Python
└── front/                   # Frontend (React)
    ├── public/              # Fichiers statiques
    ├── src/                 # Code source du frontend
    │   ├── api/             # Services API
    │   ├── components/      # Composants React
    │   ├── context/         # Contextes React
    │   ├── hooks/           # Hooks personnalisés
    │   ├── lib/             # Utilitaires
    │   ├── pages/           # Pages de l'application
    │   └── App.js           # Composant principal
    ├── Dockerfile           # Configuration Docker pour le frontend
    └── nginx.conf           # Configuration Nginx
```

## Sécurité

- Les mots de passe utilisateurs sont hachés avec bcrypt
- Les clés API Cloudflare sont chiffrées avant d'être stockées
- Authentification via JWT (JSON Web Tokens)
- HTTPS recommandé en production

## Développement

Pour développer localement sans Docker :

### Backend
```bash
cd fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd front
npm install
npm start
```

## Licence

MIT 