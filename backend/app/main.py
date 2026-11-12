"""Point d'entrée de l'API Suivi Entretiens."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password
from .routers import auth, users, candidates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("suivi")

app = FastAPI(title="Suivi Entretiens API", version="1.0.0")

# CORS : autorise le front à appeler l'API
origins = ["*"] if settings.cors_origins == "*" else settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(candidates.router)


@app.on_event("startup")
def on_startup():
    """Au démarrage : crée les tables et le compte admin initial s'il manque."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.admin_email).first()
        if existing is None:
            admin = User(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Compte admin initial créé : %s", settings.admin_email)
        else:
            logger.info("Compte admin déjà présent : %s", settings.admin_email)
    finally:
        db.close()


@app.get("/health", tags=["health"])
def health():
    """Sonde de santé (utile pour Kubernetes liveness/readiness probes)."""
    return {"status": "ok"}
