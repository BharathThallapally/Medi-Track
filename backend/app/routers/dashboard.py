from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.purchase import Purchase
from app.models.medicine_batch import MedicineBatch


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================================
# PHARMACY DASHBOARD
# ============================================================

@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # CHECK PHARMACY ROLE
    # ========================================================

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can access the dashboard"
        )

    # ========================================================
    # FIND PHARMACY
    # ========================================================

    pharmacy = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.user_id == current_user.id
        )
        .first()
    )

    if not pharmacy:
        raise HTTPException(
            status_code=404,
            detail="Pharmacy profile not found"
        )

    # ========================================================
    # BASIC DASHBOARD COUNTS
    # ========================================================

    medicines_count = (
        db.query(Medicine)
        .count()
    )

    patients_count = (
        db.query(Patient)
        .count()
    )

    prescriptions_count = (
        db.query(Prescription)
        .filter(
            Prescription.pharmacy_id == pharmacy.id
        )
        .count()
    )

    purchases_count = (
        db.query(Purchase)
        .filter(
            Purchase.pharmacy_id == pharmacy.id
        )
        .count()
    )

    # ========================================================
    # DATE INFORMATION
    # ========================================================

    today = date.today()

    warning_date = today + timedelta(days=15)

    # ========================================================
    # EXPIRING SOON MEDICINES
    # ========================================================

    expiring_batches = (
        db.query(MedicineBatch)
        .filter(
            MedicineBatch.expiry_date >= today,
            MedicineBatch.expiry_date <= warning_date
        )
        .order_by(
            MedicineBatch.expiry_date.asc()
        )
        .all()
    )

    expiring_soon = []

    for batch in expiring_batches:

        medicine = (
            db.query(Medicine)
            .filter(
                Medicine.id == batch.medicine_id
            )
            .first()
        )

        days_remaining = (
            batch.expiry_date - today
        ).days

        expiring_soon.append(
            {
                "batch_id": batch.id,

                "medicine_id": batch.medicine_id,

                "medicine_name": (
                    medicine.medicine_name
                    if medicine
                    else "Unknown Medicine"
                ),

                "batch_number": batch.batch_number,

                "expiry_date": (
                    batch.expiry_date.isoformat()
                    if batch.expiry_date
                    else None
                ),

                "days_remaining": days_remaining
            }
        )

    # ========================================================
    # EXPIRED MEDICINES
    # ========================================================

    expired_batches = (
        db.query(MedicineBatch)
        .filter(
            MedicineBatch.expiry_date < today
        )
        .order_by(
            MedicineBatch.expiry_date.desc()
        )
        .all()
    )

    expired = []

    for batch in expired_batches:

        medicine = (
            db.query(Medicine)
            .filter(
                Medicine.id == batch.medicine_id
            )
            .first()
        )

        days_expired = (
            today - batch.expiry_date
        ).days

        expired.append(
            {
                "batch_id": batch.id,

                "medicine_id": batch.medicine_id,

                "medicine_name": (
                    medicine.medicine_name
                    if medicine
                    else "Unknown Medicine"
                ),

                "batch_number": batch.batch_number,

                "expiry_date": (
                    batch.expiry_date.isoformat()
                    if batch.expiry_date
                    else None
                ),

                "days_expired": days_expired
            }
        )

    # ========================================================
    # RECENT PURCHASES
    # ========================================================

    recent_purchase_records = (
        db.query(Purchase)
        .filter(
            Purchase.pharmacy_id == pharmacy.id
        )
        .order_by(
            Purchase.created_at.desc()
        )
        .limit(5)
        .all()
    )

    recent_purchases = []

    for purchase in recent_purchase_records:

        # ----------------------------------------------------
        # Find patient
        # ----------------------------------------------------

        patient = (
            db.query(Patient)
            .filter(
                Patient.id == purchase.patient_id
            )
            .first()
        )

        patient_name = "Unknown Patient"

        # ----------------------------------------------------
        # Patient contains user_id
        # ----------------------------------------------------

        if patient:

            patient_user = (
                db.query(User)
                .filter(
                    User.id == patient.user_id
                )
                .first()
            )

            if patient_user:
                patient_name = patient_user.name

        # ----------------------------------------------------
        # Add purchase
        # ----------------------------------------------------

        recent_purchases.append(
            {
                "id": purchase.id,

                "patient_id": purchase.patient_id,

                "patient_name": patient_name,

                "total_amount": (
                    float(purchase.total_amount)
                    if purchase.total_amount is not None
                    else 0
                ),

                "created_at": (
                    purchase.created_at.isoformat()
                    if purchase.created_at
                    else None
                )
            }
        )

    # ========================================================
    # FINAL DASHBOARD RESPONSE
    # ========================================================

    return {
        "medicines": medicines_count,

        "patients": patients_count,

        "prescriptions": prescriptions_count,

        "purchases": purchases_count,

        "expiring_soon": expiring_soon,

        "expired": expired,

        "recent_purchases": recent_purchases
    }