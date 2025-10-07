from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import Job, User
from database import get_db
from .dependencies import require_roles

router = APIRouter()

@router.delete("/delete/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(["company", "recruiter"]))
):
    job = db.exec(select(Job).where(Job.id == job_id, Job.recruiter_id == user.id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or unauthorized")

    db.delete(job)
    db.commit()
    return {"detail": "Job deleted"}
