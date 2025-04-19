from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from app.core.database import  get_db
from sqlalchemy.orm import Session
from app import models

router = APIRouter()
#weekly payment report chart
@router.get("/admin/weekly-report")
def weekly_report(db: Session = Depends(get_db)):
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    payments = db.query(
        func.to_char(models.Payment.paid_date, "%Y-%m-%d").label("date"),
        func.sum(models.Payment.paid_amount).label("total")
    ).filter(
        models.Payment.paid_date >= week_ago
    ).group_by("date").all()

    return [{"date": row.date, "total": row.total} for row in payments]
#monthly payment report chart
@router.get("/admin/monthly-report")
def monthly_report(db: Session = Depends(get_db)):
    today = datetime.utcnow()
    month_ago = today - timedelta(days=30)

    payments = db.query(
        func.to_char(models.Payment.paid_date, "%Y-%m-%d").label("date"),
        func.sum(models.Payment.paid_amount).label("total")
    ).filter(
        models.Payment.paid_date >= month_ago
    ).group_by("date").all()

    return [{"date": row.date, "total": row.total} for row in payments]

@router.get("/admin/users-with-payments")
def users_with_payments(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    data = []

    for user in users:
        purchases = db.query(models.Purchase).filter(models.Purchase.user_id == user.id).all()
        for purchase in purchases:
            data.append({
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "product_name": purchase.product_name,
                "price": purchase.product_price,
                "total_paid": purchase.total_paid,
                "due_amount": purchase.due_amount,
                "purchase_id":purchase.id,
                "purchase_date": purchase.created_at.strftime("%Y-%m-%d")
            })
    return data
