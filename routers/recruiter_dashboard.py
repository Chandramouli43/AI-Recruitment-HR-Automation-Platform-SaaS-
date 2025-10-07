from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Job, Candidate, User
from schemas import JobCreate, JobRead, JobUpdate, CandidateRead
from dependencies import require_roles

router = APIRouter()

# --- Jobs Endpoints ---
@router.post("/jobs", response_model=JobRead)
def create_job(payload: JobCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    now = datetime.utcnow()
    job = Job(**payload.dict(), recruiter_id=user.id, created_at=now, updated_at=now)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/jobs", response_model=List[JobRead])
def list_jobs(
    status: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(["recruiter", "admin"]))
):
    statement = select(Job).where(Job.recruiter_id == user.id)
    if status:
        statement = statement.where(Job.status.ilike(f"%{status}%"))
    if title:
        statement = statement.where(Job.title.ilike(f"%{title}%"))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location}%"))
    if start_date:
        statement = statement.where(Job.created_at >= start_date)
    if end_date:
        statement = statement.where(Job.created_at <= end_date)
    return db.exec(statement).all()

@router.get("/jobs/{job_id}", response_model=JobRead)
def job_detail(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.recruiter_id != user.id and user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return job

@router.put("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    job = db.get(Job, job_id)
    if not job or (job.recruiter_id != user.id and user.role.lower() != "admin"):
        raise HTTPException(status_code=404, detail="Job not found or unauthorized")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(job, key, value)
    job.updated_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    job = db.get(Job, job_id)
    if not job or (job.recruiter_id != user.id and user.role.lower() != "admin"):
        raise HTTPException(status_code=404, detail="Job not found or unauthorized")
    db.delete(job)
    db.commit()
    return {"detail": "Job deleted"}

# --- Candidates Endpoints ---
@router.get("/candidates", response_model=List[CandidateRead])
def list_candidates(
    skills: Optional[str] = Query(None),
    job_id: Optional[int] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(["recruiter", "admin"]))
):
    query = select(Candidate)
    if job_id:
        query = query.where(Candidate.job_id == job_id)
    if stage:
        query = query.where(Candidate.stage == stage)
    if skills:
        for skill in [s.strip() for s in skills.split(",")]:
            query = query.where(Candidate.skills.contains(skill))
    return db.exec(query).all()

@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def candidate_detail(candidate_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    job = db.get(Job, candidate.job_id)
    if job and (job.recruiter_id != user.id and user.role.lower() != "admin"):
        raise HTTPException(status_code=403, detail="Access forbidden")
    return candidate

# --- Pipeline Endpoint ---
@router.get("/pipeline/{job_id}")
def pipeline_view(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    job = db.get(Job, job_id)
    if not job or (job.recruiter_id != user.id and user.role.lower() != "admin"):
        raise HTTPException(status_code=404, detail="Job not found or unauthorized")
    stages = db.exec(
        select(Candidate.stage, func.count(Candidate.id))
        .where(Candidate.job_id == job_id)
        .group_by(Candidate.stage)
    ).all()
    return {stage[0]: stage[1] for stage in stages}

# --- Analytics Endpoint ---
@router.get("/analytics/applications-over-time")
def applications_over_time(days: int = 30, db: Session = Depends(get_db), user: User = Depends(require_roles(["recruiter", "admin"]))):
    start_date = datetime.utcnow() - timedelta(days=days)
    job_ids = [j.id for j in db.exec(select(Job.id).where(Job.recruiter_id == user.id)).all()]
    query = select(func.date(Candidate.created_at), func.count(Candidate.id)).where(
        Candidate.job_id.in_(job_ids),
        Candidate.created_at >= start_date
    ).group_by(func.date(Candidate.created_at)).order_by(func.date(Candidate.created_at))
    return [{"date": d[0], "count": d[1]} for d in db.exec(query).all()]

# --- Settings Endpoint ---
@router.get("/settings")
def recruiter_settings(user: User = Depends(require_roles(["recruiter", "admin"]))):
    return {"user_id": user.id, "email": user.email, "role": user.role}
