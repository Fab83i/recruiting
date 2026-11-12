# Suivi Entretiens — application web

Outil de prise de notes d'entretien de recrutement (trame cycle en V + banque
de questions techniques). Version web : **FastAPI + PostgreSQL + front HTML**,
avec **authentification JWT** et **rôles** (admin / recruteur). Les données
candidats ne sont accessibles qu'après connexion.

> Évolution de l'outil single-file d'origine (localStorage) vers une vraie
> application 3-tiers, conteneurisée, prête pour Kubernetes / CI-CD.

## Architecture

```
[Recruteur] → login → [Front HTML (nginx)]
                           │ proxy /api  (même origine, pas de CORS)
                           ▼
                      [API FastAPI]  ── vérifie le JWT à chaque requête
                           │
                      [PostgreSQL]   ── users + candidates (interne, jamais exposé)
```

- **Front** : l'interface d'origine, adaptée (écran de login, appels API au lieu
  de localStorage, écran admin de gestion des comptes).
- **API** : CRUD candidats + auth JWT + gestion des utilisateurs (admin only).
- **DB** : table `users` (emails + mots de passe hashés bcrypt) et `candidates`
  (champs fixes + colonne JSONB `data` pour scores/notes/infos/présentation).

## Contenu

```
suivi-entretiens/
├── docker-compose.yml      Orchestration locale (postgres + api + front)
├── .env.example            Modèle de configuration (→ .env)
├── backend/                API FastAPI (Dockerfile inclus)
│   └── app/
│       ├── main.py         Point d'entrée + création admin au démarrage
│       ├── models.py       Tables SQLAlchemy
│       ├── schemas.py      Validation Pydantic
│       ├── security.py     Hash bcrypt + JWT
│       ├── deps.py         Dépendances d'auth (get_current_user / admin)
│       └── routers/        auth, users, candidates
└── frontend/               Front HTML + nginx (Dockerfile inclus)
    └── index.html
```

## Démarrage local (docker-compose)

```bash
cp .env.example .env
nano .env        # génère JWT_SECRET et choisis les mots de passe
docker compose up -d --build
```

- Application : http://localhost:8080
- Au premier démarrage, le compte admin (ADMIN_EMAIL / ADMIN_PASSWORD du .env)
  est créé automatiquement. Connecte-toi avec, puis crée les autres comptes
  depuis l'écran **Comptes**.

## API (routes principales)

| Méthode | Route | Rôle requis | Description |
|---|---|---|---|
| POST | `/auth/login` | — | login (form OAuth2) → JWT |
| GET | `/auth/me` | connecté | profil courant |
| GET/POST | `/candidates` | connecté | lister / créer |
| GET/PUT/DELETE | `/candidates/{id}` | connecté | détail / maj / suppr |
| GET/POST | `/users` | **admin** | lister / créer un compte |
| DELETE | `/users/{id}` | **admin** | supprimer un compte |
| GET | `/health` | — | sonde de santé (probes K8s) |

## Sécurité

- Mots de passe hashés **bcrypt**, jamais stockés en clair.
- **JWT** signé (HS256) exigé sur toutes les routes de données.
- Rôle **admin** requis pour gérer les comptes (403 sinon).
- Secrets (clé JWT, mot de passe DB) via variables d'environnement, **hors Git**.
- PostgreSQL non exposé à l'extérieur (réseau Docker interne / ClusterIP en K8s).
- En production : servir en **HTTPS** (Ingress + certificat).

## Prochaines étapes (roadmap DevOps)

Cette app est le support du parcours : manifests Kubernetes (Deployment /
Service / Ingress + Secret pour la clé JWT + StatefulSet PostgreSQL), pipeline
CI/CD (build → test → scan → push image → déploiement), GitOps (ArgoCD) et
monitoring (Prometheus / Grafana).
