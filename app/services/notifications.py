from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models import Purchase as Installment, User
from email.message import EmailMessage
from aiosmtplib import send
import os

# Load environment variables if needed
from dotenv import load_dotenv
load_dotenv()

# Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Main notification logic
async def notify_due_installments():
    db = next(get_db())
    today = datetime.utcnow()
    notify_before_days = 1
    target_date = today

    # Get all due installments whose due date is within the next n days
    due_installments = db.query(Installment).filter(
        Installment.due_amount > 0,
        Installment.create_at <= target_date
    ).all()

    for inst in due_installments:
        user = db.query(User).filter(User.id == inst.user_id).first()
        if user:
            await send_due_email(user.email, user.name, inst.due_amount, inst.create_date)

# Send email to user
async def send_due_email(to_email, name, due_amount, due_date):
    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_USERNAME")
    message["To"] = to_email
    message["Subject"] = "⏰ Upcoming Installment Due Reminder"

    message.set_content(
        f"""Hello {name},

This is a reminder that you have an upcoming due installment.

🔹 Due Amount: {due_amount}
📅 Due Date: {due_date.strftime('%Y-%m-%d')}

Please make the payment on or before the due date to avoid any issues.

Thank you!
"""
    )

    await send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
    )
