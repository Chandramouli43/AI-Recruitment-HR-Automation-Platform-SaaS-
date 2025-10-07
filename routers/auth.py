from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.concurrency import run_in_threadpool
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
import os
from database import get_db
from models import User
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- JWT settings ---
SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_MINUTES = 15

# --- OAuth2 scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- FastAPI-Mail Config ---
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASS"),
    MAIL_FROM=os.getenv("EMAIL_USER"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# --- Email Helper ---
async def send_email(to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    username: Optional[str] = None
    email: EmailStr
    password: str
    role: Literal["recruiter", "company", "superadmin"]
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- JWT Helpers ---
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": data["sub"], "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_reset_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "reset"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# --- Signup ---
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, session: Session = Depends(get_db)):
    if payload.role == "recruiter" and not payload.company_name:
        raise HTTPException(status_code=400, detail="company_name required")

    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = get_password_hash(payload.password)
    user = User(
        name=payload.name,
        username=payload.username,
        email=str(payload.email),
        hashed_password=hashed,
        role=payload.role,
        company_name=payload.company_name,
        company_website=payload.company_website,
        company_id=payload.company_id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "company_name": user.company_name,
        "company_website": user.company_website,
        "company_id": user.company_id,
        "message": f"{user.role.capitalize()} created successfully"
    }

# --- Login with JSON payload (React frontend) ---
@router.post("/login-json")
def login_json(payload: LoginRequest, session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email
    }


# --- Login with OAuth2 form (Swagger / OAuth2 clients) ---
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        {"sub": str(user.id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer","role": user.role }

# --- Forgot Password ---
@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, session: Session = Depends(get_db)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user.id)
    reset_link = f"http://localhost:3000/ResetPassword?token={reset_token}"

    await send_email(
        to=payload.email,
        subject="Password Reset Request",
        body=f"Click the link to reset your password: {reset_link}"
    )

    return {"msg": "Reset link sent to your email"}

# --- Reset Password ---
@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, session: Session = Depends(get_db)):
    user_id = verify_reset_token(payload.token)

    def update_password():
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = get_password_hash(payload.new_password)
        session.add(user)
        session.commit()
        return user

    user = await run_in_threadpool(update_password)

    await send_email(
        to=user.email,
        subject="Password Reset Successful",
        body="Your password has been successfully reset. If you did not request this change, please contact support immediately."
    )

    return {"msg": "Password reset successful. A confirmation email has been sent."}

# --- Get current user ---
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Protected route example ---
@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "company_name": current_user.company_name,
        "company_website": current_user.company_website,
        "company_id": current_user.company_id
    }

def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker
