# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlmodel import Session, select, func
# from typing import List, Optional
# from database import get_db
# from models import Job, Candidate, User
# from schemas import JobCreate, JobRead, CandidateRead
# from routers.auth import get_current_user
# from datetime import datetime, timedelta

# router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# # --- Role check dependency ---
# def recruiter_or_admin(user: User = Depends(get_current_user)):
#     if user.role.lower() not in ["recruiter", "admin"]:
#         raise HTTPException(status_code=403, detail="Access forbidden")
#     return user

# # --- Dashboard Widgets ---
# @router.get("/widgets")
# def dashboard_widgets(user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     # Count active jobs (status contains "Open" or "Published")
#     active_jobs = db.exec(
#         select(Job).where(Job.recruiter_id == user.id, Job.status.ilike("%Open%"))
#     ).all()

#     job_ids = [j.id for j in db.exec(select(Job.id).where(Job.recruiter_id == user.id)).all()]

#     # Count all applications for user's jobs
#     applications_received = db.exec(
#         select(Candidate).where(Candidate.job_id.in_(job_ids))
#     ).all()

#     # Count candidates in pipeline (stage not "Hired")
#     candidates_in_pipeline = db.exec(
#         select(Candidate).where(Candidate.job_id.in_(job_ids), Candidate.stage != "Hired")
#     ).all()

#     return {
#         "active_jobs": len(active_jobs),
#         "applications_received": len(applications_received),
#         "candidates_in_pipeline": len(candidates_in_pipeline)
#     }

# # --- Create Job ---
# @router.post("/jobs", response_model=JobRead)
# def create_job(payload: JobCreate, user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     job = Job(**payload.dict(), recruiter_id=user.id, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
#     db.add(job)
#     db.commit()
#     db.refresh(job)
#     return job

# # --- List Jobs with filters ---
# @router.get("/jobs", response_model=List[JobRead])
# def list_jobs(
#     status: Optional[str] = Query(None),
#     title: Optional[str] = Query(None),
#     location: Optional[str] = Query(None),
#     start_date: Optional[datetime] = Query(None),
#     end_date: Optional[datetime] = Query(None),
#     db: Session = Depends(get_db),
#     user: User = Depends(recruiter_or_admin)
# ):
#     query = select(Job).where(Job.recruiter_id == user.id)

#     if status:
#         query = query.where(Job.status.ilike(f"%{status.strip()}%"))
#     if title:
#         query = query.where(Job.title.ilike(f"%{title.strip()}%"))
#     if location:
#         query = query.where(Job.location.ilike(f"%{location.strip()}%"))
#     if start_date:
#         query = query.where(Job.created_at >= start_date)
#     if end_date:
#         query = query.where(Job.created_at <= end_date)

#     return db.exec(query).all()

# # --- Job Detail ---
# @router.get("/jobs/{job_id}", response_model=JobRead)
# def job_detail(job_id: int, user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     job = db.get(Job, job_id)
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found")
#     if job.recruiter_id != user.id and user.role.lower() != "admin":
#         raise HTTPException(status_code=403, detail="Access forbidden")
#     return job

# # --- Bulk Delete Jobs ---
# @router.delete("/jobs/bulk")
# def bulk_delete_jobs(job_ids: List[int], user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     for job_id in job_ids:
#         job = db.get(Job, job_id)
#         if job and (job.recruiter_id == user.id or user.role.lower() == "admin"):
#             db.delete(job)
#     db.commit()
#     return {"msg": "Jobs deleted successfully"}

# # --- Candidates Endpoints ---
# @router.get("/candidates", response_model=List[CandidateRead])
# def list_candidates(
#     skills: Optional[str] = Query(None),
#     job_id: Optional[int] = None,
#     stage: Optional[str] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(recruiter_or_admin)
# ):
#     query = select(Candidate)
#     if job_id:
#         query = query.where(Candidate.job_id == job_id)
#     if stage:
#         query = query.where(Candidate.stage == stage)
#     if skills:
#         skill_list = [s.strip() for s in skills.split(",")]
#         for skill in skill_list:
#             query = query.where(Candidate.skills.contains(skill))
#     return db.exec(query).all()

# @router.post("/candidates/bulk-assign")
# def bulk_assign_candidates(candidate_ids: List[int], job_id: int, user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     job = db.get(Job, job_id)
#     if not job or (job.recruiter_id != user.id and user.role.lower() != "admin"):
#         raise HTTPException(status_code=403, detail="Access forbidden")
#     for cid in candidate_ids:
#         candidate = db.get(Candidate, cid)
#         if candidate:
#             candidate.job_id = job_id
#             db.add(candidate)
#     db.commit()
#     return {"msg": "Candidates assigned to job"}

# @router.get("/candidates/{candidate_id}", response_model=CandidateRead)
# def candidate_detail(candidate_id: int, user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     candidate = db.get(Candidate, candidate_id)
#     if not candidate:
#         raise HTTPException(status_code=404, detail="Candidate not found")
#     job = db.get(Job, candidate.job_id)
#     if job and (job.recruiter_id != user.id and user.role.lower() != "admin"):
#         raise HTTPException(status_code=403, detail="Access forbidden")
#     return candidate

# # --- Analytics ---
# @router.get("/analytics/applications-over-time")
# def applications_over_time(days: int = 30, user: User = Depends(recruiter_or_admin), db: Session = Depends(get_db)):
#     start_date = datetime.utcnow() - timedelta(days=days)
#     job_ids = [j.id for j in db.exec(select(Job.id).where(Job.recruiter_id == user.id)).all()]

#     query = select(func.date(Candidate.created_at), func.count(Candidate.id)).where(
#         Candidate.job_id.in_(job_ids),
#         Candidate.created_at >= start_date
#     ).group_by(func.date(Candidate.created_at))

#     return [{"date": d[0], "count": d[1]} for d in db.exec(query).all()]
