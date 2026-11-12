"""Schémas Pydantic (validation des entrées/sorties de l'API)."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Users ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    is_admin: bool
    created_at: datetime


# ---------- Candidates ----------
class CandidateBase(BaseModel):
    name: str = ""
    role: str = ""
    stage: str = "RV2"
    date: str = ""
    decision: str = ""
    comment: str = ""
    data: dict[str, Any] = {}


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(CandidateBase):
    pass


class CandidateOut(CandidateBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
