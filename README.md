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

## Utilisation avec Docker

### Configuration des variables d'environnement (OBLIGATOIRE)
Avant de démarrer l'application, vous **devez** créer un fichier `.env` à la racine du projet ou définir ces variables dans votre environnement. Copiez le fichier `.env.example` pour créer votre `.env`:

```bash
cp .env.example .env
```

Liste des variables d'environnement requises:

| Variable | Description | Exemple |
|----------|-------------|---------|
| `BACKEND_PORT` | Port sur lequel le backend sera accessible | 8000 |
| `FRONTEND_PORT` | Port sur lequel le frontend sera accessible | 3000 |
| `REACT_APP_API_URL` | URL complète de l'API backend | http://localhost:8000 |
| `ENCRYPTION_KEY` | Clé utilisée pour chiffrer les données sensibles | NX2YxMdTw6YYq5JIrHfkBJpTRfvt5jY6RW3TxR7wovw= |
| `API_V1_STR` | Préfixe pour les routes de l'API | /api/v1 |
| `SECRET_KEY` | Clé secrète pour les jetons JWT | 6KqKHkcH8eZp/k2lZ8X78tmkVQ+6NzEu2lrPUXxTrpg= |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de validité des jetons d'accès | 10080 |
| `ALGORITHM` | Algorithme utilisé pour les jetons JWT | HS256 |

> ⚠️ **IMPORTANT**: Si vous ne définissez pas ces variables d'environnement, l'application ne démarrera pas correctement. Les erreurs suivantes peuvent apparaître:
> - `Variable d'environnement non définie` lors de la construction des conteneurs
> - `Port binding failed` si les ports ne sont pas définis
> - Dysfonctionnements de l'authentification si les clés de sécurité ne sont pas définies
> - Erreurs de connexion entre le frontend et le backend si `REACT_APP_API_URL` n'est pas correctement configuré

### Construction et démarrage des conteneurs
```bash
docker-compose up --build
```

### Démarrage des conteneurs en arrière-plan
```bash
docker-compose up -d
```

### Arrêt des conteneurs
```bash
docker-compose down
```

### Visualisation des logs
```bash
docker-compose logs -f
```

### Redémarrage d'un service spécifique
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Exemple: Changer les ports
Pour modifier les ports utilisés par les services, vous pouvez:

1. Créer ou modifier un fichier `.env` à la racine du projet:
```bash
BACKEND_PORT=9000
FRONTEND_PORT=4000
```

2. Reconstruire et démarrer les conteneurs:
```bash
docker-compose down
docker-compose up --build -d
```

L'application sera alors accessible sur http://localhost:4000 et l'API sur http://localhost:9000.

## Licence

MIT 