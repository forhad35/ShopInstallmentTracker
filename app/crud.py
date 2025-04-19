# crud.py
from sqlalchemy.orm import Session
from app import models,schemas
from app.models  import Purchase,Payment


# ইউজার খুঁজে বের করো ইমেইল দিয়ে
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# নতুন ইউজার তৈরি করো
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
# Create a new purchase
def create_purchase(db: Session, user_id: int, product_name: str, product_price: float):
    db_purchase = Purchase(user_id=user_id, product_name=product_name, product_price=product_price, due_amount=product_price)
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

# Add a payment
def add_payment(db: Session, purchase_id: int, paid_amount: float):
    db_payment = Payment(purchase_id=purchase_id, paid_amount=paid_amount)
    db.add(db_payment)
    db.commit()

    # Update the total paid and due amount for the purchase
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    purchase.total_paid += paid_amount
    purchase.due_amount = purchase.product_price - purchase.total_paid

    db.commit()
    return purchase  # Return updated purchase info with the total paid and due amount


# def get_installments_by_user(db: Session, user_id: int):
#     installments = db.query(Installment).filter(Installment.user_id == user_id).all()
#     for installment in installments:
#         print(installment.user.name)
#     return db.query(models.Installment).filter(models.Installment.user_id == user_id).all()