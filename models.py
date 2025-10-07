import os
import enum
from datetime import datetime, date
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, JSON as SA_JSON, Enum as SAEnum,Float, DateTime
from sqlalchemy.orm import relationship
from database import Base, engine

# ======================
# ENUMS
# ======================
class Role(str, enum.Enum):
    recruiter = "recruiter"
    company = "company"
    admin = "admin"

class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    pipeline = "pipeline"
    rejected = "rejected"
    hired = "hired"

class LeaveStatus(str, enum.Enum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class DocStatus(str, enum.Enum):
    pending = "Pending"
    uploaded = "Uploaded"

# ======================
# CORE MODELS (SQLModel)
# ======================
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
    benefits: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    skills: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    expiry_date: Optional[date] = None
    reference_id: Optional[str] = None
    jd_file: Optional[str] = None
    status: str = "Draft"
    role: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    recruiter_id: int = Field(foreign_key="user.id")
    recruiter: Optional["User"] = Relationship()
    applications: List["Application"] = Relationship(back_populates="job")

class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    role: str
    skills: Optional[str]
    stage: str = "Applied"
    resume_url: Optional[str]
    notes: Optional[str]
    recruiter_comments: Optional[str]
    applications: List["Application"] = Relationship(back_populates="candidate")

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    candidate_id: int = Field(foreign_key="candidate.id")
    candidate_name: str
    candidate_email: str
    status: ApplicationStatus = ApplicationStatus.applied
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    hired_at: Optional[datetime] = None
    job: Job = Relationship(back_populates="applications")
    candidate: Candidate = Relationship(back_populates="applications")

class AIInterviewTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    interview_type: str
    questions: List[str] = Field(default_factory=list, sa_column=Column(SA_JSON))
    time_limit: Optional[int] = None
    difficulty: Optional[str] = None
    created_by: Optional[int] = Field(foreign_key="user.id")

class Assessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    skill: Optional[str] = None
    difficulty: Optional[str] = None
    role: Optional[str] = None
    question_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="user.id")

class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidate.id")
    assessment_id: int = Field(foreign_key="assessment.id")
    due_date: Optional[date] = None
    status: str = "Assigned"

# ======================
# EXAM / LEGACY MODELS
# ======================
class LegacyQuestion(Base):
    __tablename__ = "legacy_questions"
    id = Column(Integer, primary_key=True, index=True)
    set_no = Column(Integer, nullable=True)
    question = Column(String, nullable=False)
    options = Column(SA_JSON, nullable=False)
    answer = Column(String, nullable=False)

class LegacyCandidate(Base):
    __tablename__ = "legacy_candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    verified = Column(Integer, default=0)
    score = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    answers = Column(SA_JSON, nullable=True)

# ======================
# ATTENDANCE & LEAVE
# ======================
class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    status = Column(String, default="Present")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    leave_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String)
    status = Column(SAEnum(LeaveStatus), default=LeaveStatus.pending)

# ======================
# ONBOARDING / DIGITAL SIGNATURE
# ======================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class OnboardingCandidate(Base):
    __tablename__ = "candidates_onboarding"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    documents = relationship("OnboardingDocument", back_populates="candidate", cascade="all, delete-orphan")

class OnboardingDocument(Base):
    __tablename__ = "documents_onboarding"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    status = Column(SAEnum(DocStatus, name="docstatus_enum"), default=DocStatus.pending)
    candidate_id = Column(Integer, ForeignKey("candidates_onboarding.id"))
    candidate = relationship("OnboardingCandidate", back_populates="documents")

class Signature(Base):
    __tablename__ = "signatures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

class CandidateRecord(Base):
    __tablename__ = "candidate_records"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(120), index=True)
    experience_level = Column(String(50), index=True)

    candidate_name = Column(String(200))
    candidate_email = Column(String(200), index=True)
    candidate_skills = Column(Text)
    candidate_experience_text = Column(Text)

    resume_text = Column(Text)
    jd_text = Column(Text)
    score = Column(Float)

    resume_filename = Column(String(300))
    email_sent = Column(String(20), default="no")
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)

class InterviewCandidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    otp = Column(String, nullable=True)
    otp_created_at = Column(DateTime, nullable=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="text")  # text or video

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(Text, nullable=True)
    video_path = Column(String, nullable=True)
    score = Column(Integer, nullable=True)

    candidate = relationship("Candidate")
    question = relationship("Question")


# ======================
# DATABASE INITIALIZATION
# ======================
def init_db():
    """
    Initialize all tables
    """
    SQLModel.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables initialized.")
