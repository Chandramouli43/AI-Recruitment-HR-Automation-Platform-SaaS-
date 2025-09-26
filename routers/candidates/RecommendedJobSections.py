from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.RecommendedJobSections)
def create_recommended_job(job: schemas.RecommendedJobSectionsCreate, db: Session = Depends(get_db)):
    db_job = models.RecommendedJobSections(title=job.title, company=job.company, location=job.location)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/", response_model=list[schemas.RecommendedJobSections])
def read_recommended_jobs(db: Session = Depends(get_db)):
    return db.query(models.RecommendedJobSections).all()

@router.delete("/{job_id}", status_code=204)
def delete_recommended_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.RecommendedJobSections).filter(models.RecommendedJobSections.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Recommended job not found")
    db.delete(job)
    db.commit()
