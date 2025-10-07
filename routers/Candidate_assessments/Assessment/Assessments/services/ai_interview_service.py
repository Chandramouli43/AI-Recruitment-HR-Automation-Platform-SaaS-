from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import AIInterviewTemplate  
from schema.ai_interview import AIInterviewTemplateCreate, AIInterviewTemplateUpdate
from schema.ai_interview import AIInterviewTemplateCreate, AIInterviewTemplateUpdate


def create_template(db: Session, data: AIInterviewTemplateCreate):
    template = AIInterviewTemplate(**data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

def get_template(db: Session, template_id: int):
    return db.query(AIInterviewTemplate).filter(AIInterviewTemplate.id == template_id).first()

def update_template(db: Session, template_id: int, data: AIInterviewTemplateUpdate):
    template = db.query(AIInterviewTemplate).filter(AIInterviewTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = data.dict(exclude_unset=True)  # ✅ only update provided fields
    for key, value in update_data.items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template

def delete_template(db: Session, template_id: int):
    template = db.query(AIInterviewTemplate).filter(AIInterviewTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}  # ✅ return JSON response
