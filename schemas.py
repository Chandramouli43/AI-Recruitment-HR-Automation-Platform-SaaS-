from pydantic import BaseModel, EmailStr
from typing import Optional, List,Literal
from datetime import datetime


# --- Users ---
class UserCreate(BaseModel):
    name: str
    username: Optional[str] = None       # NEW
    email: EmailStr
    password: str
    role: Literal["recruiter", "company", "superadmin"]
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_id: Optional[str] = None


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str

# --- Jobs ---
class JobBase(BaseModel):
    title: str
    department: str
    employment_type: str
    location: Optional[str] = None
    is_remote: bool = False
    description: str
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    benefits: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    expiry_date: Optional[datetime] = None
    reference_id: Optional[str] = None
    jd_file: Optional[str] = None
    is_draft: bool = False

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: Optional[str] = None
    skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None
    reference_id: Optional[str] = None
    jd_file: Optional[str] = None
    is_draft: Optional[bool] = None

class JobRead(JobBase):
    id: int
    recruiter_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Candidates ---
class CandidateCreate(BaseModel):
    name: str
    role: str
    email: EmailStr
    skills: Optional[List[str]] = []
    stage: Optional[str] = "Applied"
    resume_url: Optional[str] = None
    notes: Optional[str] = None
    job_id: Optional[int] = None

class CandidateRead(CandidateCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True



from pydantic import BaseModel
from typing import Optional

class Profile(BaseModel):
    id: int
    name: str
    role: str
    profile_image_url: str

    class Config:
        from_attributes = True

class JobSearch(BaseModel):
    id: int
    title: str
    company: str
    location: str

    class Config:
        from_attributes = True

class JobSearchCreate(BaseModel):
    title: str
    company: str
    location: str

class SavedJobs(BaseModel):
    id: int
    title: str
    company: str
    location: str

    class Config:
        from_attributes = True

class SavedJobsCreate(BaseModel):
    title: str
    company: str
    location: str

class RecentApplications(BaseModel):
    id: int
    job_title: str
    company: str
    status: str
    applied_days_ago: int

    class Config:
        from_attributes = True

class RecentApplicationsCreate(BaseModel):
    job_title: str
    company: str
    status: str
    applied_days_ago: int

class RecommendedJobSections(BaseModel):
    id: int
    title: str
    company: str
    location: str

    class Config:
        from_attributes = True

class RecommendedJobSectionsCreate(BaseModel):
    title: str
    company: str
    location: str

class Applications(BaseModel):
    id: int
    job_title: str
    company: str
    status: str
    applied_days_ago: Optional[int] = None

    class Config:
        from_attributes = True

class ApplicationsCreate(BaseModel):
    job_title: str
    company: str
    status: str
    applied_days_ago: Optional[int]

class Notifications(BaseModel):
    id: int
    message: str
    is_read: int

    class Config:
        from_attributes = True

class NotificationsCreate(BaseModel):
    message: str
    is_read: Optional[int] = 0
