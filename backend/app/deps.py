"""Dépendances d'authentification réutilisables dans les routes."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_token

# tokenUrl = l'endpoint qui délivre le token (pour la doc Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Vérifie le token JWT et renvoie l'utilisateur correspondant.

    Lève 401 si le token est absent, invalide, expiré, ou si l'utilisateur
    n'existe plus. C'est le verrou : toute route qui en dépend est protégée.
    """
    cred_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non authentifié",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise cred_error
    email = payload.get("sub")
    if not email:
        raise cred_error
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise cred_error
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Comme get_current_user, mais exige en plus le rôle admin (403 sinon)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs",
        )
    return user
