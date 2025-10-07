from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from .services.assessment_service import (
    create_assessment,
    get_assessments,
    get_assessment,
    update_assessment,
    delete_assessment
)
from schema.assessment import AssessmentCreate, AssessmentOut, AssessmentUpdate
from typing import List, Optional


router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.post("/", response_model=AssessmentOut)
def create_assessment_endpoint(data: AssessmentCreate, db: Session = Depends(get_db)):
    return create_assessment(db, data)

@router.get("/", response_model=List[AssessmentOut])
def list_assessments(
    skill: Optional[str] = None,
    difficulty: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_assessments(db, skill, difficulty, role)

@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment_endpoint(assessment_id: int, db: Session = Depends(get_db)):
    assessment = get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.put("/{assessment_id}", response_model=AssessmentOut)
def update_assessment_endpoint(assessment_id: int, data: AssessmentUpdate, db: Session = Depends(get_db)):
    update_dict = data.dict(exclude_unset=True)
    updated = update_assessment(db, assessment_id, update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return updated

@router.delete("/{assessment_id}")
def delete_assessment_endpoint(assessment_id: int, db: Session = Depends(get_db)):
    delete_assessment(db, assessment_id)
    return {"message": "Assessment deleted"}
