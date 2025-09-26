from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Role(str, Enum):
    recruiter = "recruiter"
    company = "company"
    admin = "admin"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    username: Optional[str] = None
    email: str
    hashed_password: str
    role: str
    company_name: Optional[str]
    company_website: Optional[str]
    company_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    department: str
    employment_type: str
    location: Optional[str]
    is_remote: bool = False
    description: str
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "USD"
    benefits: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    expiry_date: Optional[date] = None
    reference_id: Optional[str] = None
    jd_file: Optional[str] = None
    status: str = "Draft"

    # ✅ timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # ✅ recruiter relationship
    recruiter_id: Optional[int] = Field(foreign_key="user.id", nullable=False)
    recruiter: Optional["User"] = Relationship()

    applications: List["Application"] = Relationship(back_populates="job")



class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    role: str
    skills: Optional[str]  # comma-separated tags
    stage: str = "Applied"
    resume_url: Optional[str]
    notes: Optional[str]
    recruiter_comments: Optional[str]

    # ✅ Link to applications
    applications: List["Application"] = Relationship(back_populates="candidate")


class ApplicationStatus(str, Enum):
    applied = "applied"
    pipeline = "pipeline"
    rejected = "rejected"
    hired = "hired"


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    candidate_id: int = Field(foreign_key="candidate.id")
    candidate_name: str
    candidate_email: str
    status: ApplicationStatus = ApplicationStatus.applied
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # ✅ Back-populates
    job: Job = Relationship(back_populates="applications")
    candidate: Candidate = Relationship(back_populates="applications")

# --- Additional Models for Candidates Dashboard ---

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    profile_image_url = Column(String)

class JobSearch(Base):
    __tablename__ = "job_search"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)

class SavedJobs(Base):
    __tablename__ = "saved_jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)

class RecentApplications(Base):
    __tablename__ = "recent_applications"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    company = Column(String)
    status = Column(String)
    applied_days_ago = Column(Integer)

class RecommendedJobSections(Base):
    __tablename__ = "recommended_jobsections"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)

class Applications(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    company = Column(String)
    status = Column(String)
    applied_days_ago = Column(Integer)

class Notifications(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read