from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from models import Job, User
from database import get_db
from .dependencies import require_roles

router = APIRouter()

@router.get("/list", response_model=List[Job])
def list_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(["company", "recruiter"]))
):
    statement = select(Job).where(Job.recruiter_id == user.id)
    jobs = db.exec(statement).all()

    # Ensure optional fields have defaults
    for job in jobs:
        job.skills = job.skills or []
        job.benefits = job.benefits or []
        job.employment_type = job.employment_type or "Full-time"
        job.salary_min = job.salary_min or 0
        job.salary_max = job.salary_max or 0
        job.currency = job.currency or "USD"
        job.location = job.location or "N/A"
        job.status = job.status or "Draft"
        job.is_remote = job.is_remote if job.is_remote is not None else False
        job.department = job.department or "General"
        job.responsibilities = job.responsibilities or "N/A"
        job.requirements = job.requirements or "N/A"
        job.reference_id = job.reference_id or "N/A"
        job.jd_file = job.jd_file or "N/A"
        job.expiry_date = job.expiry_date or None

    return jobs
