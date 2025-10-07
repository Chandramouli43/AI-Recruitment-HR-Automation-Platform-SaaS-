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

@router.get("/", response_model=schemas.Profile)
def read_profile(db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/", response_model=schemas.Profile)
def create_profile(profile: schemas.Profile, db: Session = Depends(get_db)):
    existing = db.query(models.Profile).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    db_profile = models.Profile(
        name=profile.name,
        role=profile.role,
        profile_image_url=profile.profile_image_url
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile
