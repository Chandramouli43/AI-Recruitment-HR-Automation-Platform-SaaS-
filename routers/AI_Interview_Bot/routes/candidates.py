from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Candidate
from ..utils.email_utils import generate_otp, send_otp
import datetime

router = APIRouter()

@router.post("/login")
def login_candidate(name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if not candidate:
        candidate = Candidate(name=name, email=email)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    otp = generate_otp()
    candidate.otp = otp
    candidate.otp_created_at = datetime.datetime.utcnow()
    db.commit()

    send_otp(candidate.email, otp)
    return {"message": "OTP sent to your email", "candidate_id": candidate.id}

@router.post("/verify_otp")
def verify_otp(candidate_id: int = Form(...), otp: str = Form(...), db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return {"error": "Candidate not found"}

    time_diff = datetime.datetime.utcnow() - candidate.otp_created_at
    if str(candidate.otp) == otp and time_diff.total_seconds() <= 300:
        candidate.otp = None
        db.commit()
        return {"message": "OTP verified"}
    else:
        return {"error": "Invalid or expired OTP"}
