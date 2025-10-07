import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import SessionLocal, init_db
from models import CandidateRecord
from routers.Resume_parsing.routers.utils import extract_text, ai_extract_fields, ai_generate_jd, ai_similarity_score, send_email_smtp
from routers.Resume_parsing.routers.config import SCORE_THRESHOLD

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def root():
    return {"status": "ok"}

@router.get("/candidates")
def list_candidates(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    rows = db.query(CandidateRecord).order_by(CandidateRecord.id.desc()).offset(offset).limit(limit).all()
    return [
        {"id": r.id, "name": r.candidate_name, "email": r.candidate_email,
         "role": r.role, "experience_level": r.experience_level,
         "score": r.score, "email_sent": r.email_sent,
         "created_at": r.created_at.isoformat()}
        for r in rows
    ]

@router.post("/process")
async def process_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    experience_level: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1) Extract resume text
    content = await file.read()
    try:
        resume_text = extract_text(file.filename, content)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # 2) Extract fields with AI
    fields = ai_extract_fields(resume_text)
    name, email, skills, exp_summary = (
        fields["name"], fields["email"], fields["skills"], fields["experience_summary"]
    )

    # 3) Generate JD with AI
    jd_text = ai_generate_jd(role, experience_level)

    # 4) Compare & Score
    score = ai_similarity_score(resume_text, jd_text)

    # 5) Save if above threshold
    email_status = "skipped"
    rec_id = None
    if score >= SCORE_THRESHOLD:
        save_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(content)

        rec = CandidateRecord(
            role=role, experience_level=experience_level,
            candidate_name=name, candidate_email=email,
            candidate_skills=", ".join(skills) if isinstance(skills, list) else str(skills),
            candidate_experience_text=exp_summary,
            resume_text=resume_text[:25000], jd_text=jd_text[:25000],
            score=score, resume_filename=file.filename, email_sent="no"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        rec_id = rec.id

        # 6) Send email if available
        if email:
            ok, msg = send_email_smtp(name, email, score, role)
            rec.email_sent = "yes" if ok else f"error: {msg}"
            db.add(rec)
            db.commit()
            email_status = rec.email_sent

    return JSONResponse({
        "id": rec_id,
        "role": role,
        "experience_level": experience_level,
        "candidate": {"name": name, "email": email, "skills": skills, "experience_summary": exp_summary},
        "jd_preview": jd_text[:600],
        "score": score,
        "threshold": SCORE_THRESHOLD,
        "status": "shortlisted" if score >= SCORE_THRESHOLD else "rejected",
        "email_status": email_status
    })
