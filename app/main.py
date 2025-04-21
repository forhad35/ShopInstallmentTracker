# main.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.services.notifications import notify_due_installments
from app.services.generate_invoice import router as invoice_router
from app.api.admin_panal import router as admin_router
from app.services.email_service import router as email_service
from app.api.user import router as user_router
from app.core.database import Base,engine
Base.metadata.create_all(bind=engine)
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("interval", days=1)
def run_daily_check():
    asyncio.run(notify_due_installments())

scheduler.start()

# Load environment variables
load_dotenv()

app = FastAPI()
app.include_router(user_router)
app.include_router(email_service)
app.include_router(admin_router)
app.include_router(invoice_router)
# Allow frontend access (CORS policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend এর URL চাইলে নির্দিষ্ট করতেও পারো
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running on Render!"}


