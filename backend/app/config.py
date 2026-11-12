"""Configuration de l'application, chargée depuis les variables d'environnement."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de données
    database_url: str = "postgresql://suivi:suivi@localhost:5432/suivi"

    # JWT — la clé secrète DOIT être fournie via l'environnement en production
    jwt_secret: str = "CHANGER_CETTE_CLE_EN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # 8 h

    # Compte admin initial (créé au démarrage s'il n'existe pas)
    admin_email: str = "fabiencalvo@gmail.com"
    admin_password: str = "changeme"  # à surcharger via l'environnement

    # CORS — origine(s) autorisée(s) pour le front
    cors_origins: str = "*"


settings = Settings()
