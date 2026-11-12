"""Sécurité : hachage des mots de passe (bcrypt) et gestion des tokens JWT."""
from datetime import datetime, timedelta

import bcrypt
from jose import jwt, JWTError

from .config import settings

# bcrypt limite le mot de passe à 72 octets : on tronque proprement au besoin.
_BCRYPT_MAX = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_BCRYPT_MAX]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8")[:_BCRYPT_MAX]
    try:
        return bcrypt.checkpw(pw, hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, is_admin: bool) -> str:
    """Crée un JWT signé contenant l'identité et le rôle de l'utilisateur."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": subject,          # l'email de l'utilisateur
        "is_admin": is_admin,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Décode et vérifie un JWT. Renvoie le payload, ou None si invalide/expiré."""
    try:
        return jwt.decode(token, settings.jwt_secret,
                          algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
