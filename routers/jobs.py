# from fastapi import APIRouter, Depends, HTTPException
# from sqlmodel import Session, select
# from datetime import datetime
# from typing import Optional, List
# from models import Job, User
# from database import get_db
# from routers.auth import get_current_user  # Your current_user function

# router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# # --- Role checker dependency ---
# def require_roles(allowed_roles: List[str]):
#     def role_checker(current_user: User = Depends(get_current_user)):
#         if current_user.role.lower() not in [r.lower() for r in allowed_roles]:
#             raise HTTPException(status_code=403, detail="Operation not permitted")
#         return current_user
#     return role_checker

# # --- Create Job ---
# @router.post("/create", response_model=Job)
# def create_job(
#     title: str,
#     description: str,
#     location: Optional[str] = None,
#     salary: Optional[str] = None,
#     employment_type: Optional[str] = None,
#     status: Optional[str] = "Open",
#     skills: Optional[List[str]] = None,
#     created_at: Optional[datetime] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(require_roles(["company", "recruiter"]))
# ):
#     now = datetime.utcnow()
#     job = Job(
#         title=title,
#         description=description,
#         location=location,
#         salary=salary,
#         employment_type=employment_type,
#         status=status or "Draft",
#         skills=skills or [],
#         created_at=created_at or now,
#         updated_at=created_at or now,
#         recruiter_id=user.id
#     )
#     db.add(job)
#     db.commit()
#     db.refresh(job)
#     return job

# # --- Update Job ---
# @router.put("/update/{job_id}", response_model=Job)
# def update_job(
#     job_id: int,
#     title: Optional[str] = None,
#     description: Optional[str] = None,
#     location: Optional[str] = None,
#     salary: Optional[str] = None,
#     employment_type: Optional[str] = None,
#     status: Optional[str] = None,
#     skills: Optional[List[str]] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(require_roles(["company", "recruiter"]))
# ):
#     job = db.exec(select(Job).where(Job.id == job_id, Job.recruiter_id == user.id)).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found or unauthorized")

#     if title is not None:
#         job.title = title
#     if description is not None:
#         job.description = description
#     if location is not None:
#         job.location = location
#     if salary is not None:
#         job.salary = salary
#     if employment_type is not None:
#         job.employment_type = employment_type
#     if status is not None:
#         job.status = status
#     if skills is not None:
#         job.skills = skills

#     job.updated_at = datetime.utcnow()
#     db.add(job)
#     db.commit()
#     db.refresh(job)
#     return job

# # --- Delete Job ---
# @router.delete("/delete/{job_id}")
# def delete_job(
#     job_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(require_roles(["company", "recruiter"]))
# ):
#     job = db.exec(select(Job).where(Job.id == job_id, Job.recruiter_id == user.id)).first()
#     if not job:
#         raise HTTPException(status_code=404, detail="Job not found or unauthorized")

#     db.delete(job)
#     db.commit()
#     return {"detail": "Job deleted"}

# # --- Search Jobs ---
# @router.get("/search", response_model=List[Job])
# def search_jobs(
#     title: Optional[str] = None,
#     status: Optional[str] = None,
#     location: Optional[str] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(require_roles(["company", "recruiter"]))
# ):
#     statement = select(Job).where(Job.recruiter_id == user.id)
#     jobs = db.exec(statement).all()

#     filtered_jobs = []
#     for job in jobs:
#         if title and title.lower() not in job.title.lower():
#             continue
#         if status and status.lower() != job.status.lower():
#             continue
#         if location and location.lower() not in (job.location or "").lower():
#             continue
#         if start_date and job.created_at < start_date:
#             continue
#         if end_date and job.created_at > end_date:
#             continue
#         filtered_jobs.append(job)

#     return filtered_jobs

# # --- List All Jobs for current recruiter/company ---
# @router.get("/list", response_model=List[Job])
# def list_jobs(
#     db: Session = Depends(get_db),
#     user: User = Depends(require_roles(["company", "recruiter"]))
# ):
#     statement = select(Job).where(Job.recruiter_id == user.id)
#     jobs = db.exec(statement).all()
#     return jobs
