from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.connection import engine


# =========================================================
# MODELS
# =========================================================

from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.patient import Patient
from app.models.medicine import Medicine
from app.models.medicine_batch import MedicineBatch
from app.models.notification import Notification
from app.models.purchase import Purchase
from app.models.purchase_medicine import PurchaseMedicine
from app.models.notification_preferences import NotificationPreference
from app.models.consent import Consent
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine


# =========================================================
# ROUTERS
# =========================================================

from app.routers.dashboard import router as dashboard_router
from app.routers.prescription import router as prescription_router
from app.routers.auth import router as auth_router
from app.routers.pharmacy import router as pharmacy_router
from app.routers.patient import router as patient_router
from app.routers.medicine import router as medicine_router
from app.routers.medicine_batch import router as medicine_batch_router
from app.routers.notification import router as notification_router
from app.routers.purchase import router as purchase_router
from app.routers.notification_preferences import (
    router as notification_preferences_router
)
from app.routers.consent import router as consent_router


# =========================================================
# SCHEDULER
# =========================================================

from app.services.scheduler_service import (
    start_scheduler,
    stop_scheduler
)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("MediTrack: Starting application...")

    # Start automatic notification scheduler
    start_scheduler()

    yield

    # Stop scheduler when application shuts down
    stop_scheduler()

    print("MediTrack: Application stopped.")


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="MediTrack API",
    description="Digital Medicine Management & Reminder System",
    version="1.0.0",
    lifespan=lifespan
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://medi-track-peach-rho.vercel.app"
],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)

app.include_router(pharmacy_router)

app.include_router(patient_router)

app.include_router(medicine_router)

app.include_router(medicine_batch_router)

app.include_router(notification_router)

app.include_router(purchase_router)

app.include_router(notification_preferences_router)

app.include_router(consent_router)

app.include_router(prescription_router)

app.include_router(dashboard_router)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Welcome to MediTrack API",
        "status": "running"
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/database-test")
def database_test():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

    return {
        "database": "connected",
        "result": result.scalar()
    }