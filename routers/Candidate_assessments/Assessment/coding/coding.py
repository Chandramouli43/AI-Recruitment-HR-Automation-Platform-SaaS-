from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from utils import (
    generate_otp, send_email, ai_or_fallback_questions,
    save_submission, get_db_connection, run_code_detailed,
    generate_ai_email, generate_ai_manager_link
)
from datetime import datetime, timedelta
import json

router = APIRouter()

# ---------------- OTP store with expiration ----------------
# { email: {"otp": "123456", "expires": datetime } }
otp_store = {}
OTP_VALIDITY_MINUTES = 5

def store_otp(email, otp):
    otp_store[email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=OTP_VALIDITY_MINUTES)
    }

def verify_otp_func(email, otp):
    entry = otp_store.get(email)
    if not entry:
        return False
    if datetime.utcnow() > entry["expires"]:
        otp_store.pop(email, None)
        return False
    if entry["otp"] == otp:
        otp_store.pop(email, None)
        return True
    return False

# ---------------- Models ----------------
class OTPRequest(BaseModel):
    name: str
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class CodeSubmission(BaseModel):
    name: str
    email: str
    question_title: str
    language: str
    code: str

class FinalizeRequest(BaseModel):
    name: str
    email: str

# ---------------- OTP ----------------
@router.post("/send-otp")
def send_otp(data: OTPRequest):
    otp = generate_otp()
    store_otp(data.email, otp)  # store with expiration
    send_email(data.email, "Levitica OTP", f"Hello {data.name}, OTP: {otp}\nValid 5 minutes.")
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
def verify_otp_route(data: VerifyOTPRequest):
    verified = verify_otp_func(data.email, data.otp)
    return {"verified": verified}

# ---------------- Questions ----------------
@router.get("/questions")
def get_questions():
    questions = ai_or_fallback_questions()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                title TEXT,
                description TEXT,
                test_cases JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for q in questions:
            cur.execute(
                "INSERT INTO questions(title, description, test_cases) VALUES (%s,%s,%s)",
                (q["title"], q["description"], json.dumps(q["test_cases"]))
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Save questions error:", e)
    return {"questions": questions}

# ---------------- Run Code ----------------
@router.post("/run_code")
def run_code_endpoint(data: CodeSubmission):
    success, output = run_code_detailed(data.language, data.code)
    return {"success": success, "output": output or "No output"}

# ---------------- Submit Code ----------------
@router.post("/submit")
def submit_code(data: CodeSubmission):
    success, output = run_code_detailed(data.language, data.code)
    save_submission(
        data.name, data.email, data.question_title,
        data.language, data.code, output, success
    )
    return {
        "message": "Submission saved successfully.",
        "success": success,
        "output": output or ""
    }

# ---------------- Finalize Exam ----------------
@router.post("/finalize")
def finalize(data: FinalizeRequest, background_tasks: BackgroundTasks):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM submissions WHERE candidate_email=%s AND success=TRUE",
            (data.email,)
        )
        row = cur.fetchone()
        success_count = row[0] if row else 0
        cur.close()
        conn.close()

        if success_count >= 1:
            manager_link = generate_ai_manager_link(data.name, data.email)
            background_tasks.add_task(
                send_email,
                data.email,
                "Levitica Manager Round Scheduled",
                f"Hello {data.name},\n\nYou are eligible for the manager round.\nLink: {manager_link}"
            )
            return {"status": "manager_round", "link": manager_link}

        else:
            background_tasks.add_task(
                send_email,
                data.email,
                "Levitica Exam Result",
                generate_ai_email(data.name, "Regret")
            )
            return {"status": "regret"}

    except Exception as e:
        print("Finalize error:", e)
        return {"status": "error", "message": str(e)}
