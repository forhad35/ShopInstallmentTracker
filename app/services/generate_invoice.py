from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
import os
import pdfkit
from datetime import datetime, timedelta
from app import models
from app.core.database import get_db

router = APIRouter()

#get users payment invoice
@router.get("/invoice/{user_id}/{purchase_id}", response_class=FileResponse)
def generate_invoice(user_id: int, purchase_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    purchase = db.query(models.Purchase).filter(
        models.Purchase.user_id == user_id,
        models.Purchase.id == purchase_id
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found for this user")

    last_payment = db.query(models.Payment).filter(
        models.Payment.purchase_id == purchase.id
    ).order_by(models.Payment.paid_date.desc()).first()

    paid = last_payment.paid_amount if last_payment else 0

    # Template location
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    # Jinja2 environment setup
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("invoice.html")
    html_content = template.render(
        name=user.name,
        email=user.email,
        product_name=purchase.product_name,
        price=purchase.product_price,
        paid=paid,
        due=purchase.due_amount,
        date=purchase.created_at.strftime("%Y-%m-%d")
    )

    pdf_file = f"invoice_user_{user_id}_purchase_{purchase_id}.pdf"
    pdfkit.from_string(html_content, pdf_file)

    with open(pdf_file, "rb") as f:
        pdf_data = f.read()

    os.remove(pdf_file)

    return Response(content=pdf_data, media_type="application/pdf")
# admin get Weekly/monthly report (paid & due) for all users as pdf
@router.get("/admin/report/{timeframe}/{category}", response_class=FileResponse)
def download_report(timeframe: str, category: str, db: Session = Depends(get_db)):
    # Validate timeframe and category
    if timeframe not in ["weekly", "monthly"] or category not in ["paid", "due"]:
        raise HTTPException(status_code=400, detail="Invalid parameters")

    # Logic based on timeframe
    today = datetime.utcnow()
    days = 7 if timeframe == "weekly" else 30
    date_from = today - timedelta(days=days)

    users = db.query(models.User).all()
    report_data = []

    for user in users:
        purchases = db.query(models.Purchase).filter(
            models.Purchase.user_id == user.id,
            models.Purchase.created_at >= date_from
        ).all()

        for purchase in purchases:
            if category == "due":
                if purchase.due_amount > 0:
                    report_data.append({
                        "name": user.name,
                        "email": user.email,
                        "product": purchase.product_name,
                        "price": purchase.product_price,
                        "paid": purchase.total_paid,
                        "due": purchase.due_amount,
                        "date": purchase.created_at.strftime("%Y-%m-%d")
                    })
            elif category =="paid":
                if purchase.due_amount <= 0:
                    report_data.append({
                        "name": user.name,
                        "email": user.email,
                        "product": purchase.product_name,
                        "price": purchase.product_price,
                        "paid": purchase.total_paid,
                        "due": purchase.due_amount,
                        "date": purchase.created_at.strftime("%Y-%m-%d")
                    })

    # HTML Render
        # Template location
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        # Jinja2 environment setup
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report.html")
    html_content = template.render(
        data=report_data,
        month=" - " +today.strftime("%B %Y") if timeframe =="monthly" else "",
        report_type=timeframe.capitalize(),
        category = category.capitalize()
    )

    pdf_file = f"../../monthly_due_report.pdf"
    pdfkit.from_string(html_content, pdf_file)
    # background_tasks.add_task(os.remove, pdf_file)


    return FileResponse(path=pdf_file, media_type='application/pdf', filename=pdf_file)