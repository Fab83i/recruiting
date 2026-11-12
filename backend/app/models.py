"""Modèles SQLAlchemy (tables de la base)."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Un recruteur (ou admin) pouvant se connecter à l'outil."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Candidate(Base):
    """Une fiche candidat avec ses notes d'entretien.

    Les champs fixes (name, role, stage...) sont des colonnes dédiées ;
    le contenu souple de la trame (scores /5, notes par question, infos
    pratiques, présentation) est stocké dans la colonne JSONB `data`,
    ce qui reprend la structure du JSON d'origine sans multiplier les colonnes.
    """
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, default="", nullable=False)
    role = Column(String, default="", nullable=False)
    stage = Column(String, default="RV2", nullable=False)
    date = Column(String, default="", nullable=False)   # ISO "YYYY-MM-DD"
    decision = Column(String, default="", nullable=False)  # go|hold|nogo|""
    comment = Column(String, default="", nullable=False)

    # scores{}, notes{}, info{}, intro — la partie flexible
    data = Column(JSONB, default=dict, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User")
