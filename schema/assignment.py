from pydantic import BaseModel
from datetime import date
from typing import Optional

class AssignmentBase(BaseModel):
    candidate_id: int
    assessment_id: int
    due_date: Optional[date] = None
    status: Optional[str] = "Assigned"

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentOut(AssignmentBase):
    id: int

    class Config:
        from_attributes = True
