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

@router.post("/", response_model=schemas.Applications)
def create_application(application: schemas.ApplicationsCreate, db: Session = Depends(get_db)):
    db_app = models.Applications(
        job_title=application.job_title,
        company=application.company,
        status=application.status,
        applied_days_ago=application.applied_days_ago
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.get("/", response_model=list[schemas.Applications])
def read_applications(db: Session = Depends(get_db)):
    return db.query(models.Applications).all()

@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(models.Applications).filter(models.Applications.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
