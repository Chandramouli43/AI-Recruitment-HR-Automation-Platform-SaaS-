from fastapi import FastAPI
from sqlmodel import SQLModel
from routers.AI_Interview_Bot.routes import interviews
from routers.Resume_parsing.routers import resume_router
from routers.HR_Automation.Task_Management.router import tasks_router
from routers.HR_Automation.Onboarding.routers import candidates, uploads
from routers.HR_Automation.digital_signature.routers import signatures, documents
from routers.HR_Automation.attendance.routers import attendance, leave
from routers.Basic_analytics.hiring_funnel.routers import hiring_funnel
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware



# -------------------------
# --- Routers -------------
# -------------------------
from routers.auth import router as auth_router
from routers.jobs import router as jobs_router
from routers.admin import router as admin_router
from routers.candidates import router as candidates_router
from routers.recruiter_dashboard import router as recruiter_dashboard_router
from routers.pipeline import router as pipeline_router
from routers.Analytics_Dashboard.analytics import router as analytics_router
from routers.HR_Automation.digital_signature.routers.documents import router as documents_router
from routers.HR_Automation.digital_signature.routers.signatures import router as signatures_router
from routers.Candidate_assessments.Assessment.Assessments.assessments_router import router as assessments_router
from routers.Candidate_assessments.Assessment.Assessments.assignments_router import router as assignments_router
from routers.Candidate_assessments.Assessment.Assessments.ai_interview_router import router as ai_interview_router
from routers.Candidate_assessments.Assessment.communication.comm_routes import router as comm_router
from routers.Candidate_assessments.Assessment.communication.comm_routes import router as codind_router
from routers.Candidate_assessments.Assessment.Assessments.Assessment_Result.candidates import router as candidates_router
from routers.Candidate_assessments.Assessment.aptitude.routers import exam,otp
from routers.Basic_analytics.hiring_funnel.routers import hiring_funnel
from routers.Basic_analytics.hiring_funnel.routers.hiring_funnel import router as time_hire
from routers.HR_Automation.Task_Management.router.tasks_router import router as tasks_router
from routers.Resume_parsing.routers.resume_router import router as resume_router




# -------------------------
# --- Initialize FastAPI ---
# -------------------------
app = FastAPI(title="AI Recruitment HR Platform")

# -------------------------
# --- Enable CORS ---------
# -------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",  # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# --- Startup Event -------
# -------------------------
@app.on_event("startup")
def on_startup():
    # Create SQLModel tables
    SQLModel.metadata.create_all(bind=engine)
    # Create Base (SQLAlchemy) tables
    Base.metadata.create_all(bind=engine)

    # Insert required documents if they don't exist

# -------------------------
# --- Include Routers -----
# -------------------------
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(candidates_router)
app.include_router(pipeline_router)
app.include_router(recruiter_dashboard_router, prefix="/api/recruiter_dashboard", tags=["Recruiter Dashboard"])
app.include_router(analytics_router)
app.include_router(assessments_router)
app.include_router(assignments_router)
app.include_router(candidates_router, prefix="/api/assessment_results", tags=["Assessment Results"])
app.include_router(ai_interview_router)
app.include_router(comm_router, prefix="/comm", tags=["Communication Exam"])
app.include_router(codind_router, prefix="/coding", tags=["Coding Exam"])
app.include_router(exam.router, prefix="/api/assessment/aptitude", tags=["Aptitude Exam"])
app.include_router(hiring_funnel.router, prefix="/api/hiring_funnel", tags=["Hiring Funnel"])
app.include_router(time_hire, prefix="/api/time_to_hire", tags=["Time to Hire"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(leave.router, prefix="/api/leave", tags=["Leave"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(signatures_router, prefix="/api/signatures", tags=["Signatures"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(documents.router, prefix="/api/document", tags=["Document"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(resume_router, prefix="/api/resume", tags=["Resume AI"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Interview Candidates"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])

# -------------------------
# --- Test Endpoint -------
# -------------------------
@app.get("/api/test")
def test_api():
    return {"message": "Backend is working and CORS is enabled!"}


