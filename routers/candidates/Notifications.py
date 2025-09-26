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

@router.post("/", response_model=schemas.Notifications)
def create_notification(notification: schemas.NotificationsCreate, db: Session = Depends(get_db)):
    notif = models.Notifications(message=notification.message, is_read=notification.is_read)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

@router.get("/", response_model=list[schemas.Notifications])
def read_notifications(db: Session = Depends(get_db)):
    return db.query(models.Notifications).all()

@router.put("/{notif_id}", response_model=schemas.Notifications)
def mark_as_read(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notifications).filter(models.Notifications.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = 1
    db.commit()
    db.refresh(notif)
    return notif
