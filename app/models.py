
from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy import ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    purchases = relationship("Purchase", back_populates="user")
class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_name = Column(String)
    product_price = Column(Float)
    total_paid = Column(Float, default=0)  # Total paid for this purchase
    due_amount = Column(Float, default=0)  # Remaining due for this purchase
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="purchases")
    payments = relationship("Payment", back_populates="purchase")
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    paid_amount = Column(Float)
    paid_date = Column(DateTime, default=datetime.utcnow)
    purchase = relationship("Purchase", back_populates="payments")
