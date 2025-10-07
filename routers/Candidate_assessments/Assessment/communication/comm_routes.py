from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from routers.Candidate_assessments.Assessment.communication.utils_comm import (
    generate_otp,
    send_email,
    generate_full_exam,
    score_text,
    generate_candidate_email,
    otp_store
)

from database import DATABASE_URL
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime, json, time

# ---------------- Database Setup ----------------
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

# ---------------- Models ----------------
class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)

    reading_paragraph = Column(Text)
    reading_mcqs = Column(Text)
    writing_prompt = Column(Text)
    listening_paragraph = Column(Text)

    writing_answer = Column(Text)
    listening_answer = Column(Text)
    mcq_answers = Column(Text)

    writing_score = Column(Float)
    listening_score = Column(Float)
    mcq_score = Column(Float)
    total_score = Column(Float)
    passed = Column(Boolean)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---------------- Router ----------------
router = APIRouter()

# ---------------- Request Models ----------------
class OTPRequest(BaseModel):
    name: str
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class CommSubmission(BaseModel):
    name: str
    email: str
    writing_answer: str
    listening_answer: str
    mcq_answers: dict

# #---------------- Mock OTP Endpoint ----------------
# @router.get("/mock-otp")
# def mock_otp(email: str):
#     """
#     Returns existing OTP for testing or generates a new one if not exist.
#     """
#     record = otp_store.get(email)
#     if record and time.time() < record["expires"]:
#         otp = record["otp"]
#     else:
#         otp = generate_otp()
#         otp_store[email] = {"otp": otp, "expires": time.time() + 300}  # 5 min
#     return {"email": email, "otp": otp, "message": "Mock OTP returned for testing."}

# ---------------- Send OTP ----------------
@router.post("/send-otp")
def send_otp_route(data: OTPRequest):
    otp = generate_otp()
    otp_store[data.email] = {"otp": otp, "expires": time.time() + 300}  # 5 min expiry
    print(f"[DEBUG] OTP for {data.email}: {otp}")

    success, msg = send_email(
        data.email,
        "Levitica Communication OTP",
        f"Hello {data.name},\n\nYour OTP is: {otp}\nIt is valid for 5 minutes."
    )
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"message": f"OTP sent successfully to {data.email}"}

# ---------------- Verify OTP ----------------
@router.post("/verify-otp")
def verify_otp_route(data: VerifyOTPRequest):
    record = otp_store.get(data.email)
    if not record:
        return {"verified": False, "reason": "No OTP found. Request a new one."}
    if time.time() > record["expires"]:
        otp_store.pop(data.email, None)
        return {"verified": False, "reason": "OTP expired. Request a new one."}
    if record["otp"] == data.otp:
        otp_store.pop(data.email, None)
        return {"verified": True}
    return {"verified": False, "reason": "Invalid OTP"}

# ---------------- Exam Routes ----------------
@router.get("/exam")
def get_exam(name: str, email: str):
    try:
        exam_data = generate_full_exam(email, name)
        if not exam_data:
            raise HTTPException(status_code=500, detail="Failed to generate exam")
        with SessionLocal() as session:
            existing = session.query(ExamAttempt).filter_by(email=email).first()
            if not existing:
                attempt = ExamAttempt(
                    name=name,
                    email=email,
                    reading_paragraph=exam_data.get("reading_paragraph", ""),
                    reading_mcqs=json.dumps(exam_data.get("reading_mcqs", [])),
                    writing_prompt=exam_data.get("writing_prompt", ""),
                    listening_paragraph=exam_data.get("listening_paragraph", "")
                )
                session.add(attempt)
                session.commit()
        return {"exam": exam_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/submit")
def submit_answers(data: CommSubmission):
    try:
        with SessionLocal() as session:
            attempt = session.query(ExamAttempt).filter_by(email=data.email).first()
            if not attempt:
                raise HTTPException(status_code=404, detail="Exam not found")

            writing_score = score_text(data.writing_answer, attempt.writing_prompt, 10)
            listening_score = score_text(data.listening_answer, attempt.listening_paragraph, 5)
            mcq_questions = json.loads(attempt.reading_mcqs or "[]")
            mcq_answers = data.mcq_answers or {}
            mcq_score = sum(
                1 for i, q in enumerate(mcq_questions)
                if mcq_answers.get(str(i)) == q.get("answer")
            )

            total_score = writing_score + listening_score + mcq_score
            passed = total_score >= 9

            attempt.writing_answer = data.writing_answer
            attempt.listening_answer = data.listening_answer
            attempt.mcq_answers = json.dumps(mcq_answers)
            attempt.writing_score = writing_score
            attempt.listening_score = listening_score
            attempt.mcq_score = mcq_score
            attempt.total_score = total_score
            attempt.passed = passed
            attempt.submitted_at = datetime.datetime.utcnow()
            session.commit()

        email_data = generate_candidate_email(data.name, passed)
        success, msg = send_email(data.email, email_data["subject"], email_data["body"])
        if not success:
            print(f"[EMAIL ERROR] {msg}")

        return {"total_score": total_score, "max_score": 10 + 5 + len(mcq_questions), "passed": passed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# ---------------- Admin Route ----------------
@router.get("/all-exams")
def get_all_exams():
    try:
        with SessionLocal() as session:
            attempts = session.query(ExamAttempt).all()
            results = []
            for a in attempts:
                results.append({
                    "name": a.name,
                    "email": a.email,
                    "reading_paragraph": a.reading_paragraph,
                    "reading_mcqs": json.loads(a.reading_mcqs) if a.reading_mcqs else [],
                    "writing_prompt": a.writing_prompt,
                    "listening_paragraph": a.listening_paragraph,
                    "writing_answer": a.writing_answer,
                    "listening_answer": a.listening_answer,
                    "mcq_answers": json.loads(a.mcq_answers) if a.mcq_answers else {},
                    "writing_score": a.writing_score,
                    "listening_score": a.listening_score,
                    "mcq_score": a.mcq_score,
                    "total_score": a.total_score,
                    "passed": a.passed,
                    "submitted_at": a.submitted_at
                })
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
