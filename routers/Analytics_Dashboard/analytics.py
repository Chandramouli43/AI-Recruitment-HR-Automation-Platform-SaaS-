from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models
from database import get_db
from .utils import parse_date_str

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/kpis")
def get_kpis(
    role: str | None = Query(None),
    start_date: str | None = Query(None),
    expiryDate: str | None = Query(None),
    db: Session = Depends(get_db)
):
    # Parse dates
    start = parse_date_str(start_date)
    end = parse_date_str(expiryDate)

    # Prepare job query with filters
    job_query = db.query(models.Job).filter(models.Job.status.in_(["active", "Draft"]))

    if role:
        role_clean = role.strip().lower()
        job_query = job_query.filter(func.lower(func.trim(models.Job.role)) == role_clean)
    
    if end:
        job_query = job_query.filter(models.Job.expiry_date <= end)

    active_jobs = job_query.count()

    # Prepare application query with same job filters
    app_query = db.query(models.Application).join(models.Job)\
        .filter(models.Job.status.in_(["active", "Draft"]))

    if role:
        app_query = app_query.filter(func.lower(func.trim(models.Job.role)) == role_clean)
    if start:
        app_query = app_query.filter(models.Application.applied_at >= start)
    if end:
        app_query = app_query.filter(models.Application.applied_at <= end)

    total_applications = app_query.count()

    # Applications this week/month
    week_start = datetime.utcnow() - timedelta(days=7)
    month_start = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)

    applications_this_week = app_query.filter(models.Application.applied_at >= week_start).count()
    applications_this_month = app_query.filter(models.Application.applied_at >= month_start).count()

    # Average time to hire (in days)
    time_to_hire = db.query(
        func.avg(
            func.extract("epoch", models.Application.hired_at - models.Application.applied_at) / 86400.0
        )
    ).filter(models.Application.hired_at.isnot(None)).scalar()

    # Applications by status
    status_counts = db.query(models.Application.status, func.count(models.Application.id))\
        .group_by(models.Application.status).all()
    status_data = {s: c for s, c in status_counts}

    return {
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "applications_this_week": applications_this_week,
        "applications_this_month": applications_this_month,
        "avg_time_to_hire_days": round(time_to_hire, 2) if time_to_hire else None,
        "applications_by_status": status_data
    }
