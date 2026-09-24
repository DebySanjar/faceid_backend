from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from app.database import get_db
from app import models, schemas
from app.auth import get_current_admin

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=List[schemas.PaymentOut])
def list_payments(
    month: Optional[str] = None,       # "2026-09"
    student_id: Optional[int] = None,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    query = db.query(models.Payment).options(joinedload(models.Payment.student))
    if month:
        query = query.filter(models.Payment.month == month)
    if student_id:
        query = query.filter(models.Payment.student_id == student_id)
    if group_id:
        query = query.join(models.Student).filter(models.Student.group_id == group_id)
    return query.order_by(models.Payment.payment_date.desc()).all()


@router.post("/", response_model=schemas.PaymentOut)
def create_payment(data: schemas.PaymentCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    student = db.query(models.Student).filter(models.Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Talaba topilmadi")
    payment = models.Payment(**data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov topilmadi")
    db.delete(payment)
    db.commit()
    return {"message": "To'lov o'chirildi"}


@router.get("/summary/month")
def monthly_summary(
    month: str,   # "2026-09"
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Oylik to'lov hisoboti"""
    payments = db.query(models.Payment).filter(models.Payment.month == month).all()
    total = sum(p.amount for p in payments)
    paid_count = sum(1 for p in payments if p.status == models.PaymentStatus.paid)
    return {
        "month": month,
        "total_income": total,
        "payment_count": len(payments),
        "paid_count": paid_count,
    }
