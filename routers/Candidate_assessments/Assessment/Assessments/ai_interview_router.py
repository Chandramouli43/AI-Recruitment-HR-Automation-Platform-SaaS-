from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schema.ai_interview import (
    AIInterviewTemplateCreate,
    AIInterviewTemplateUpdate,
    AIInterviewTemplateOut,
)
from routers.Candidate_assessments.Assessment.Assessments.services import ai_interview_service


router = APIRouter(prefix="/ai-interviews", tags=["AI Interviews"])

@router.post("/", response_model=AIInterviewTemplateOut)
def create_template(data: AIInterviewTemplateCreate, db: Session = Depends(get_db)):
    return ai_interview_service.create_template(db, data)

@router.get("/{template_id}", response_model=AIInterviewTemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = ai_interview_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=AIInterviewTemplateOut)
def update_template(template_id: int, data: AIInterviewTemplateUpdate, db: Session = Depends(get_db)):
    return ai_interview_service.update_template(db, template_id, data)

@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    return ai_interview_service.delete_template(db, template_id)
