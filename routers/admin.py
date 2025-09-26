# backend/routers/admin.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from database import get_db
from models import User
from routers.auth import require_roles

router = APIRouter(prefix="/superadmin", tags=["Admin"])  # <--- Rename here

@router.get("/summary")
def admin_summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(["superadmin"])),
):
    total_users = db.exec(select(func.count(User.id))).one()
    users = db.exec(select(User)).all()

    return {
        "total_users": total_users,
        "users": users
    }
