from sqlalchemy.orm import Session
import models, schemas

def get_candidates(db: Session):
    return db.query(models.Candidate).all()

def get_candidate(db: Session, candidate_id: int):
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
