from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Question, Answer
from ..utils.ai_analysis import score_answer
import os
import shutil

router = APIRouter()
UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/get_questions")
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    return [{"id": q.id, "text": q.question_text, "type": q.question_type} for q in questions]

@router.post("/submit_answer")
def submit_answer(
    candidate_id: int = Form(...),
    question_id: int = Form(...),
    answer_text: str = Form(None),
    video: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    video_path = None
    if video:
        video_path = os.path.join(UPLOAD_DIR, video.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

    question = db.query(Question).filter(Question.id == question_id).first()
    score = None
    if answer_text:
        score = score_answer(question.question_text, answer_text)

    ans = Answer(
        candidate_id=candidate_id,
        question_id=question_id,
        answer_text=answer_text,
        video_path=video_path,
        score=score
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)

    return {"message": "Answer submitted successfully", "score": score}
