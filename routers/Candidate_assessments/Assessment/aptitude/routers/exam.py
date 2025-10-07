from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import LegacyQuestion as Question
from models import LegacyCandidate as Candidate
from ..schemas.exam import ExamStartRequest, SubmitExam
from ..schemas.candidate import CandidateCreate, OTPVerify
from ..utils import generate_otp, send_email, assign_questions

router = APIRouter()

# In-memory storage for OTPs
TEMP_OTPS = {}

# ---------------- OTP Endpoints ----------------
@router.post("/send")
def send_otp(data: CandidateCreate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter_by(email=data.email).first()
    if not candidate:
        candidate = Candidate(
            name=data.name,
            email=data.email,
            status="Pending",
            score=0,
            verified=0,          # LegacyCandidate uses Integer
            answers={}
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    otp_code = generate_otp()
    TEMP_OTPS[candidate.email] = otp_code
    send_email(candidate.email, "Your OTP", f"Your OTP is: {otp_code}")
    return {"message": "OTP sent successfully"}


@router.post("/verify")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter_by(email=data.email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if TEMP_OTPS.get(data.email) != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    candidate.verified = 1  # ⚡ LegacyCandidate uses Integer
    db.commit()
    TEMP_OTPS.pop(data.email, None)
    return {"message": "OTP verified successfully"}

# ---------------- Exam Endpoints ----------------
@router.get("/instructions")
def instructions():
    return {
        "round_name": "Aptitude Test",
        "time_limit_seconds": 1800,
        "total_questions": 25,
        "instructions": "Answer all 25 MCQs in 30 minutes. Do not refresh the page."
    }

@router.get("/get_set/{set_no}")
def get_set(set_no: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.set_no == set_no).all()
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions found for set {set_no}")
    return questions

@router.post("/start")
def start_exam(data: ExamStartRequest, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter_by(id=data.student_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    question_objs = assign_questions(data.student_id)
    if not question_objs:
        raise HTTPException(status_code=404, detail="No questions available for this student")

    # Store question IDs in candidate.answers
    candidate.answers = {str(i + 1): q.id for i, q in enumerate(question_objs)}
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    exam_view = [{"no": i + 1, "question": q.question, "options": q.options} for i, q in enumerate(question_objs)]
    return {"questions": exam_view}

@router.post("/submit")
def submit_exam(data: SubmitExam, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter_by(id=data.student_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    assigned_qids = candidate.answers
    if not assigned_qids:
        raise HTTPException(status_code=400, detail="Exam not started or questions missing")

    score = 0
    for q_no_str, selected_option in data.answers.items():
        q_id = assigned_qids.get(str(q_no_str))
        if not q_id:
            continue
        q_obj = db.query(Question).filter_by(id=q_id).first()
        if q_obj and selected_option == q_obj.answer:
            score += 1

    candidate.score = score
    candidate.status = "Qualified" if score >= 15 else "Regret"
    candidate.answers = data.answers

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {"score": score, "status": candidate.status}
