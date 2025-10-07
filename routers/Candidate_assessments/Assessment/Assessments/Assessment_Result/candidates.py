from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(
    prefix="/api/candidates",
    tags=["candidates"]
)

@router.get("/", response_model=list[schemas.CandidateSchema])
def read_candidates(db: Session = Depends(get_db)):
    return db.query(models.Candidate).all()

@router.get("/{candidate_id}", response_model=schemas.CandidateSchema)
def read_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
