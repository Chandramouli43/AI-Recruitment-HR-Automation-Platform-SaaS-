from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db


router = APIRouter(prefix="/api/pipeline/candidates", tags=["Pipeline"])


@router.get("/", response_model=List[schemas.CandidateOut])
def list_candidates(db: Session = Depends(get_db)):
    return db.query(models.Candidate).all()


@router.post("/", response_model=schemas.CandidateOut, status_code=201)
def create_candidate(payload: schemas.CandidateCreate, db: Session = Depends(get_db)):
    stage = db.get(models.Stage, payload.stage_id)
    if not stage:
        raise HTTPException(status_code=400, detail="Invalid stage_id")
    candidate = models.Candidate(
        name=payload.name,
        role=payload.role,
        status=payload.status,
        stage_id=payload.stage_id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.patch("/{candidate_id}", response_model=schemas.CandidateOut)
def update_candidate(candidate_id: int, payload: schemas.CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if payload.stage_id is not None:
        stage = db.get(models.Stage, payload.stage_id)
        if not stage:
            raise HTTPException(status_code=400, detail="Invalid stage_id")
        candidate.stage_id = payload.stage_id
    if payload.name is not None:
        candidate.name = payload.name
    if payload.role is not None:
        candidate.role = payload.role
    if payload.status is not None:
        candidate.status = payload.status
    db.commit()
    db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return None


