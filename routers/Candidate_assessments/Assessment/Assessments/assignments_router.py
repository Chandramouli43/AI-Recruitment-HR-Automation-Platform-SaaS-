from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schema.assignment import AssignmentCreate, AssignmentOut
from routers.Candidate_assessments.Assessment.Assessments.services import assignment_service
from typing import List

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("/", response_model=AssignmentOut)
def assign(data: AssignmentCreate, db: Session = Depends(get_db)):
    return assignment_service.create_assignment(db, data)

@router.get("/", response_model=List[AssignmentOut])
def list_assignments(db: Session = Depends(get_db)):
    return assignment_service.get_assignments(db)
