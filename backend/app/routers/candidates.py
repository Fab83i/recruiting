"""Routes CRUD des candidats — toutes protégées par authentification."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate, User
from ..schemas import CandidateCreate, CandidateUpdate, CandidateOut
from ..deps import get_current_user

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateOut])
def list_candidates(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Liste tous les candidats (tout recruteur authentifié y a accès)."""
    return db.query(Candidate).order_by(Candidate.date.desc()).all()


@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Crée une nouvelle fiche candidat."""
    cand = Candidate(**payload.model_dump(), owner_id=user.id)
    db.add(cand)
    db.commit()
    db.refresh(cand)
    return cand


@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if cand is None:
        raise HTTPException(status_code=404, detail="Candidat introuvable")
    return cand


@router.put("/{candidate_id}", response_model=CandidateOut)
def update_candidate(
    candidate_id: str,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Met à jour une fiche candidat (remplacement complet)."""
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if cand is None:
        raise HTTPException(status_code=404, detail="Candidat introuvable")
    for field, value in payload.model_dump().items():
        setattr(cand, field, value)
    db.commit()
    db.refresh(cand)
    return cand


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if cand is None:
        raise HTTPException(status_code=404, detail="Candidat introuvable")
    db.delete(cand)
    db.commit()
