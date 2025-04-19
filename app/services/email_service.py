import os
from email.message import EmailMessage
from random import randint

from aiosmtplib import send
from fastapi import HTTPException, Depends, APIRouter
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
router = APIRouter()
# Temporary in-memory OTP storage
otp_storage = {}

# Pydantic models
class EmailRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

# Function to generate random 6-digit OTP
def generate_otp():
    return str(randint(100000, 999999))

# Function to send OTP to Gmail
async def send_email_otp(email: str, otp: str):
    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_USERNAME")
    message["To"] = email
    message["Subject"] = "Your OTP Code"
    message.set_content(f"Your OTP is: {otp}")

    await send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
    )
@router.post("/send-otp/")
async def send_otp(data: EmailRequest):
    otp = generate_otp()
    otp_storage[data.email] = otp
    await send_email_otp(data.email, otp)
    return {"message": f"OTP sent to {data.email}"}

@router.post("/verify-otp/")
async def verify_otp(data: OTPVerifyRequest, db: Session = Depends(get_db)):
    saved_otp = otp_storage.get(data.email)
    if saved_otp and saved_otp == data.otp:
        del otp_storage[data.email]

        # Check if user exists
        user = crud.get_user_by_email(db, data.email)
        if user:
            return {"message": "OTP verified", "user": user}
        else:
            raise HTTPException(status_code=404, detail="User not registered")

    raise HTTPException(status_code=400, detail="Invalid OTP")