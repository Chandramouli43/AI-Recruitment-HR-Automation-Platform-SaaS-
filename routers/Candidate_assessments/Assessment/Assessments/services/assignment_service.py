from sqlalchemy.orm import Session
from schema.assignment import AssignmentCreate
from models import Assignment          # instead of 'app.models.assessment'

def create_assignment(db: Session, data: AssignmentCreate):
    assignment = Assignment(**data.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def get_assignments(db: Session):
    return db.query(Assignment).all()
