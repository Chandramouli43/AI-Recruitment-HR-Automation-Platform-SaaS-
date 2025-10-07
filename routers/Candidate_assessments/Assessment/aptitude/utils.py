import random
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from database import SessionLocal
from models import LegacyQuestion
from .config import SENDER_EMAIL, SENDER_PASSWORD, OTP_EXPIRY, PASS_THRESHOLD

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

def generate_sets_db():
    db: Session = SessionLocal()
    all_questions = db.query(LegacyQuestion).all()
    if len(all_questions) < 250:
        raise Exception("Need at least 250 questions to create 10 sets of 25")
    random.shuffle(all_questions)
    for set_no in range(1, 11):
        start = (set_no - 1) * 25
        end = set_no * 25
        set_questions = all_questions[start:end]
        for q in set_questions:
            q.set_no = set_no
    db.commit()
    db.close()
    print("✅ 10 sets assigned successfully!")

def assign_questions(student_id: int):
    db: Session = SessionLocal()
    set_no = (student_id - 1) % 10 + 1
    questions = db.query(LegacyQuestion).filter(LegacyQuestion.set_no == set_no).all()
    db.close()
    return questions
