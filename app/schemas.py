from pydantic import BaseModel, EmailStr
from datetime import datetime, date


class UserCreate(BaseModel):
    email: EmailStr
    name:str

class UserOut(BaseModel):
    id: int
    name:str
    email: EmailStr

    class Config:
        orm_mode = True

# Schema for creating a purchase
class PurchaseCreate(BaseModel):
    user_id: int
    product_name: str
    product_price: float

# Schema for a payment
class PaymentCreate(BaseModel):
    purchase_id: int
    paid_amount: float

# Response schema for purchase info
class PurchaseOut(BaseModel):
    id: int
    user_id: int
    product_name: str
    product_price: float
    total_paid: float
    due_amount: float
    created_at: datetime

    class Config:
        orm_mode = True