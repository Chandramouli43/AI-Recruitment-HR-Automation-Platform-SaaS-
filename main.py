from fastapi import FastAPI
from sqlmodel import SQLModel
from database import engine
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.auth import router as auth_router
from routers.jobs import router as jobs_router
from routers.admin import router as admin_router
from routers.candidates import router as candidates_router
from routers.recruiter_dashboard import router as recruiter_dashboard_router


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
    # Create all tables in DB
    SQLModel.metadata.create_all(engine)

# -------------------------
# --- Include Routers -----
# -------------------------
# Authentication
app.include_router(auth_router)  # ✅ no extra prefix needed

# Jobs CRUD
app.include_router(jobs_router)


# Admin routes
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(candidates_router)   

# Recruiter Dashboard
app.include_router(
    recruiter_dashboard_router,
    prefix="/api/recruiter_dashboard",
    tags=["Recruiter Dashboard"]
)

# -------------------------
# --- Test Endpoint -------
# -------------------------
@app.get("/api/test")
def test_api():
    return {"message": "Backend is working and CORS is enabled!"}
