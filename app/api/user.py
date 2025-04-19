
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.core.database import get_db
router = APIRouter()
# Email → OTP verify করার পর এখানে call করবা user register করতে
@router.post("/register/", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered.")
    return crud.create_user(db, user)

# Get all users (for admin)
@router.get("/users/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
# Create a new purchase
@router.post("/purchases/", response_model=schemas.PurchaseOut)
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    return crud.create_purchase(db, purchase.user_id, purchase.product_name, purchase.product_price)

# Add a payment for a purchase
@router.post("/payments/", response_model=schemas.PurchaseOut)
def add_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return crud.add_payment(db, payment.purchase_id, payment.paid_amount)

# Get all purchases for a user
@router.get("/users/{user_id}/purchases/", response_model=list[schemas.PurchaseOut])
def get_user_purchases(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Purchase).filter(models.Purchase.user_id == user_id).all()