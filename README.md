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

- Docker et Docker Compose (pour l'installation avec Docker)
- Python 3.12+ (pour l'installation manuelle du backend)
- Node.js 18+ (pour l'installation manuelle du frontend)
- Clé API Cloudflare

## Installation et démarrage

### Option 1: Déploiement avec Docker Compose

1. Clonez ce dépôt :
```bash
git clone https://github.com/votreusername/cloudflare-linker.git
cd cloudflare-linker
```

2. Créez un fichier `.env` basé sur `.env.example` avec les variables d'environnement requises :
```bash
cp .env.example .env
# Puis modifiez le fichier .env avec vos propres valeurs
```

3. Démarrez l'application avec Docker Compose :
```bash
docker-compose up -d
```

4. Accédez à l'application dans votre navigateur :
```
http://localhost:3000
```

### Option 2: Installation manuelle (pour développement)

#### Backend
1. Accédez au répertoire backend:
```bash
cd fastapi
```

2. Créez un environnement virtuel et activez-le:
```bash
# Sous Windows
python -m venv venv
venv\Scripts\activate

# Sous Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. Créez un fichier `.env` à la racine du projet basé sur `.env.example`

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

5. Lancez le serveur de développement:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
1. Dans un autre terminal, accédez au répertoire frontend:
```bash
cd front
```

2. Installez les dépendances:
```bash
npm install
```

3. Lancez le serveur de développement:
```bash
npm start
```

4. Accédez à l'application dans votre navigateur:
```
http://localhost:3000
```

## Variables d'environnement

Les variables suivantes doivent être configurées dans le fichier `.env` :

```
# Configuration des ports
BACKEND_PORT=8000        # Port pour le backend FastAPI
FRONTEND_PORT=3000       # Port pour le frontend React

# URL de l'API pour le frontend
REACT_APP_API_URL=http://localhost:8000

# Clé d'encryption pour chiffrer les données sensibles
ENCRYPTION_KEY=votre_clé_d_encryption

# Configuration de l'API
API_V1_STR=/api/v1

# Clé secrète pour la génération de jetons JWT
SECRET_KEY=votre_clé_secrète

# Durée de validité des jetons d'accès (en minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 jours

# Algorithme utilisé pour les jetons JWT
ALGORITHM=HS256
```

## Première configuration

Lors de la première connexion, vous devrez:
1. Créer un compte administrateur
2. Saisir votre clé API Cloudflare et l'email associé
3. Configurer vos zones DNS et enregistrements

## Structure du projet

```
cloudflare-linker/
├── docker-compose.yml       # Configuration Docker Compose
├── .env.example             # Exemple de fichier de variables d'environnement
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
    └── Dockerfile           # Configuration Docker pour le frontend
```

## Sécurité

- Les mots de passe utilisateurs sont hachés avec bcrypt
- Les clés API Cloudflare sont chiffrées avant d'être stockées
- Authentification via JWT (JSON Web Tokens)
- HTTPS recommandé en production

## Licence

MIT 