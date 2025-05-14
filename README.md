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
- Python 3.11+ (pour l'installation manuelle du backend)
- Node.js 18+ (pour l'installation manuelle du frontend)
- Clé API Cloudflare

## Installation et démarrage

### Option 1: Déploiement avec Docker Compose

1. Clonez ce dépôt :
```bash
git clone https://github.com/votreusername/cloudflare-linker.git
cd cloudflare-linker
```

2. Configuration des variables d'environnement:

Deux méthodes sont possibles:
   
a) Créer un fichier `.env` dans le dossier `fastapi` avec le contenu suivant:
```
# Clé d'encryption pour chiffrer les données sensibles (générée aléatoirement)
ENCRYPTION_KEY="votre_clé_d'encryption"

# Configuration de l'API
API_V1_STR="/api/v1"

# Clé secrète pour la génération de jetons JWT (ne pas modifier une fois configurée)
SECRET_KEY="votre_clé_secrète"

# Durée de validité des jetons d'accès (en minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 jours

# Algorithme utilisé pour les jetons JWT
ALGORITHM="HS256"

# Configuration CORS (origines autorisées séparées par des virgules)
CORS_ORIGINS="http://localhost:3000,http://localhost"
```

b) Définir les variables d'environnement lors du lancement (voir commande ci-dessous)

3. Démarrez l'application avec Docker Compose :
```bash
# Avec les variables d'environnement définies dans le fichier .env
docker-compose up -d

# OU en spécifiant les variables directement
SECRET_KEY="votre_clé_secrète" ENCRYPTION_KEY="votre_clé_d'encryption" docker-compose up -d
```

4. Accédez à l'application dans votre navigateur :
```
http://localhost
```

### Option 2: Déploiement avec Portainer

1. Accédez à votre interface Portainer et créez une nouvelle stack

2. Copiez le contenu du fichier `docker-compose.yml` dans l'éditeur

3. Dans la section "Environment variables" de Portainer, définissez au minimum ces variables:
   - `SECRET_KEY` - Clé secrète pour les tokens JWT
   - `ENCRYPTION_KEY` - Clé pour le chiffrement des données sensibles

4. Autres variables optionnelles que vous pouvez personnaliser:
   - `DATABASE_URL` (par défaut: sqlite:///data/cloudflare_linker.db)
   - `API_V1_STR` (par défaut: /api/v1)
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (par défaut: 10080)
   - `ALGORITHM` (par défaut: HS256)
   - `CORS_ORIGINS` (par défaut: *)
   - `FIRST_TIME_SETUP` (par défaut: false)

5. Déployez la stack et accédez à l'application à l'URL configurée dans Portainer

### Option 3: Installation manuelle (pour développement)

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

3. Créez un fichier `.env` dans le dossier `fastapi/app/core` avec le contenu décrit plus haut

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

## Première configuration

Lors de la première connexion, vous devrez:
1. Créer un compte administrateur
2. Saisir votre clé API Cloudflare et l'email associé
3. Configurer vos zones DNS et enregistrements

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

## Licence

MIT 