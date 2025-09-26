import json
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlmodel import Session
from models import Job, User
from .schemas import JobRead
from ..auth import require_roles, get_current_user
from database import get_db
import shutil, os
from datetime import datetime

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

UPLOAD_DIR = "uploads/jd_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/create")
async def create_job(
    title: str = Form(...),
    department: str = Form(...),
    employmentType: str = Form(...),
    location: str = Form(None),
    isRemote: bool = Form(False),
    description: str = Form(...),
    responsibilities: str = Form(None),
    requirements: str = Form(None),
    salaryMin: float = Form(None),
    salaryMax: float = Form(None),
    currency: str = Form("USD"),
    benefits: str = Form("[]"),
    skills: str = Form("[]"),
    expiryDate: str = Form(None),
    referenceId: str = Form(None),
    jdFile: UploadFile = None,
    status: str = Form("Draft"),
    session: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["recruiter"]))
):
    # Parse JSON safely
    try:
        benefits_list = json.loads(benefits)
    except:
        benefits_list = []
    try:
        skills_list = json.loads(skills)
    except:
        skills_list = []

    expiry_date_obj = None
    if expiryDate:
        try:
            expiry_date_obj = datetime.strptime(expiryDate, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiryDate format. Use YYYY-MM-DD.")

    jd_path = None
    if jdFile:
        jd_path = os.path.join(UPLOAD_DIR, jdFile.filename)
        with open(jd_path, "wb") as buffer:
            shutil.copyfileobj(jdFile.file, buffer)

    job = Job(
        title=title,
        department=department,
        employment_type=employmentType,
        location=location,
        is_remote=isRemote,
        description=description,
        responsibilities=responsibilities,
        requirements=requirements,
        salary_min=salaryMin,
        salary_max=salaryMax,
        currency=currency,
        benefits=benefits_list,
        skills=skills_list,
        expiry_date=expiry_date_obj,
        reference_id=referenceId,
        jd_file=jd_path,
        status=status,
        recruiter_id=current_user.id
    )

    session.add(job)
    session.commit()
    session.refresh(job)

    return {
    "message": "Job created successfully!",
    "job": {
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "employment_type": job.employment_type,
        "location": job.location,
        "is_remote": job.is_remote,
        "description": job.description,
        "responsibilities": job.responsibilities,
        "requirements": job.requirements,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.currency,
        "benefits": job.benefits,
        "skills": job.skills,
        "expiry_date": job.expiry_date,
        "reference_id": job.reference_id,
        "jd_file": job.jd_file,
        "status": job.status,
        "recruiter_id": job.recruiter_id,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }
}

