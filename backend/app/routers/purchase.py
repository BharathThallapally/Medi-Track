from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.security import get_current_user
from app.database.connection import get_db

from app.models.user import User
from app.models.patient import Patient
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.medicine_batch import MedicineBatch
from app.models.purchase import Purchase
from app.models.purchase_medicine import PurchaseMedicine
from app.models.prescription_medicine import PrescriptionMedicine
from app.models.notification_preferences import NotificationPreference
from app.models.consent import Consent

from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse
)

from app.schemas.purchase_medicine import (
    PurchaseMedicineCreate,
    PurchaseMedicineResponse
)

from app.services.email_service import (
    send_purchase_medicine_sheet_email
)


router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"]
)


# ============================================================
# PHARMACY ROLE CHECK
# ============================================================

def check_pharmacy_role(current_user: User):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can manage purchases"
        )


# ============================================================
# CREATE PURCHASE
# ============================================================

@router.post(
    "",
    response_model=PurchaseResponse
)
def create_purchase(
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    # --------------------------------------------------------
    # Check patient
    # --------------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == purchase_data.patient_id
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # --------------------------------------------------------
    # Get patient User account
    # --------------------------------------------------------

    patient_user = (
        db.query(User)
        .filter(
            User.id == patient.user_id
        )
        .first()
    )

    if not patient_user:
        raise HTTPException(
            status_code=404,
            detail="Patient user account not found"
        )

    # --------------------------------------------------------
    # Get pharmacy
    # --------------------------------------------------------

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
    # CHECK EMAIL BEFORE UPDATING
    # ========================================================

    if purchase_data.email is not None:

        email_value = str(purchase_data.email)

        existing_email_user = (
            db.query(User)
            .filter(
                User.email == email_value,
                User.id != patient_user.id
            )
            .first()
        )

        if existing_email_user:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This email address is already registered "
                    "to another user."
                )
            )

    # ========================================================
    # CHECK PHONE BEFORE UPDATING
    # ========================================================

    if purchase_data.phone is not None:

        existing_phone_user = (
            db.query(User)
            .filter(
                User.phone == purchase_data.phone,
                User.id != patient_user.id
            )
            .first()
        )

        if existing_phone_user:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This phone number is already registered "
                    "to another user."
                )
            )

    # ========================================================
    # UPDATE PATIENT CONTACT DETAILS
    # ========================================================

    if purchase_data.email is not None:
        patient_user.email = str(purchase_data.email)

    if purchase_data.phone is not None:
        patient_user.phone = purchase_data.phone

    # ========================================================
    # CREATE / UPDATE NOTIFICATION PREFERENCES
    # ========================================================

    preferences = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.patient_id == patient.id
        )
        .first()
    )

    if not preferences:

        preferences = NotificationPreference(
            patient_id=patient.id,
            email_enabled=purchase_data.email_enabled,
            whatsapp_enabled=purchase_data.whatsapp_enabled,
            sms_enabled=purchase_data.sms_enabled
        )

        db.add(preferences)

    else:

        preferences.email_enabled = (
            purchase_data.email_enabled
        )

        preferences.whatsapp_enabled = (
            purchase_data.whatsapp_enabled
        )

        preferences.sms_enabled = (
            purchase_data.sms_enabled
        )

    # ========================================================
    # NOTIFICATION CONSENT
    # ========================================================

    any_channel_enabled = (
        purchase_data.email_enabled
        or purchase_data.whatsapp_enabled
        or purchase_data.sms_enabled
    )

    if any_channel_enabled:

        consent = (
            db.query(Consent)
            .filter(
                Consent.patient_id == patient.id,
                Consent.consent_type == "EXPIRY_NOTIFICATION"
            )
            .order_by(Consent.id.desc())
            .first()
        )

        if not consent:

            consent = Consent(
                patient_id=patient.id,
                consent_type="EXPIRY_NOTIFICATION",
                status="GRANTED",
                given_at=datetime.now(timezone.utc)
            )

            db.add(consent)

        else:

            consent.status = "GRANTED"
            consent.given_at = datetime.now(timezone.utc)
            consent.revoked_at = None

    # --------------------------------------------------------
    # Create purchase
    # --------------------------------------------------------

    purchase = Purchase(
        patient_id=purchase_data.patient_id,
        pharmacy_id=pharmacy.id,
        prescription_id=purchase_data.prescription_id,
        total_amount=purchase_data.total_amount
    )

    db.add(purchase)

    db.commit()
    db.refresh(purchase)

    return purchase


# ============================================================
# GET ALL PURCHASES
# ============================================================

@router.get(
    "",
    response_model=list[PurchaseResponse]
)
def get_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

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

    purchases = (
        db.query(Purchase)
        .filter(
            Purchase.pharmacy_id == pharmacy.id
        )
        .order_by(Purchase.id)
        .all()
    )

    return purchases


# ============================================================
# GET SINGLE PURCHASE
# ============================================================

@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse
)
def get_purchase(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

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

    purchase = (
        db.query(Purchase)
        .filter(
            Purchase.id == purchase_id,
            Purchase.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not purchase:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    return purchase


# ============================================================
# ADD MEDICINE TO PURCHASE
# ============================================================

@router.post(
    "/items",
    response_model=PurchaseMedicineResponse
)
def add_purchase_medicine(
    item_data: PurchaseMedicineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    # --------------------------------------------------------
    # Get pharmacy
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get purchase
    # --------------------------------------------------------

    purchase = (
        db.query(Purchase)
        .filter(
            Purchase.id == item_data.purchase_id,
            Purchase.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not purchase:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    # --------------------------------------------------------
    # Check prescription medicine
    # --------------------------------------------------------

    if purchase.prescription_id:

        prescribed_medicine = (
            db.query(PrescriptionMedicine)
            .filter(
                PrescriptionMedicine.prescription_id
                == purchase.prescription_id,

                PrescriptionMedicine.medicine_id
                == item_data.medicine_id
            )
            .first()
        )

        if not prescribed_medicine:

            raise HTTPException(
                status_code=400,
                detail=(
                    "This medicine is not part of "
                    "the selected prescription"
                )
            )

    # --------------------------------------------------------
    # Check medicine
    # --------------------------------------------------------

    medicine = (
        db.query(Medicine)
        .filter(
            Medicine.id == item_data.medicine_id
        )
        .first()
    )

    if not medicine:

        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    # --------------------------------------------------------
    # Check batch
    # --------------------------------------------------------

    batch = (
        db.query(MedicineBatch)
        .filter(
            MedicineBatch.id == item_data.batch_id,
            MedicineBatch.medicine_id
            == item_data.medicine_id
        )
        .first()
    )

    if not batch:

        raise HTTPException(
            status_code=404,
            detail=(
                "Medicine batch not found or "
                "does not belong to medicine"
            )
        )

    # --------------------------------------------------------
    # Validate quantity
    # --------------------------------------------------------

    if item_data.quantity <= 0:

        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    # --------------------------------------------------------
    # Validate price
    # --------------------------------------------------------

    if item_data.unit_price < 0:

        raise HTTPException(
            status_code=400,
            detail="Unit price cannot be negative"
        )

    # --------------------------------------------------------
    # Prevent duplicate medicine in same purchase
    # --------------------------------------------------------

    existing_item = (
        db.query(PurchaseMedicine)
        .filter(
            PurchaseMedicine.purchase_id
            == item_data.purchase_id,

            PurchaseMedicine.medicine_id
            == item_data.medicine_id,

            PurchaseMedicine.batch_id
            == item_data.batch_id
        )
        .first()
    )

    if existing_item:

        raise HTTPException(
            status_code=400,
            detail=(
                "This medicine batch is already "
                "added to this purchase"
            )
        )

    # --------------------------------------------------------
    # Create purchase item
    # --------------------------------------------------------

    purchase_medicine = PurchaseMedicine(
        purchase_id=item_data.purchase_id,
        medicine_id=item_data.medicine_id,
        batch_id=item_data.batch_id,
        quantity=item_data.quantity,
        unit_price=item_data.unit_price
    )

    db.add(purchase_medicine)

    db.commit()
    db.refresh(purchase_medicine)

    return purchase_medicine


# ============================================================
# COMPLETE PURCHASE + SEND DIGITAL MEDICINE SHEET
# ============================================================

@router.post(
    "/{purchase_id}/complete"
)
async def complete_purchase(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    # --------------------------------------------------------
    # Get pharmacy
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get purchase
    # --------------------------------------------------------

    purchase = (
        db.query(Purchase)
        .filter(
            Purchase.id == purchase_id,
            Purchase.pharmacy_id == pharmacy.id
        )
        .first()
    )

    if not purchase:

        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )

    # --------------------------------------------------------
    # Already sent
    # --------------------------------------------------------

    if purchase.medicine_sheet_sent_at:

        return {
            "message": (
                "Digital medicine sheet was "
                "already sent"
            ),
            "purchase_id": purchase.id,
            "completed": True,
            "already_sent": True
        }

    # --------------------------------------------------------
    # Get purchased medicines
    # --------------------------------------------------------

    purchase_items = (
        db.query(PurchaseMedicine)
        .filter(
            PurchaseMedicine.purchase_id
            == purchase.id
        )
        .all()
    )

    if not purchase_items:

        return {
            "message": (
                "Purchase has no medicines yet"
            ),
            "purchase_id": purchase.id,
            "completed": False,
            "already_sent": False
        }

    # ========================================================
    # IF PURCHASE HAS A PRESCRIPTION
    # ========================================================

    if purchase.prescription_id:

        prescribed_items = (
            db.query(PrescriptionMedicine)
            .filter(
                PrescriptionMedicine.prescription_id
                == purchase.prescription_id
            )
            .all()
        )

        prescribed_medicine_ids = {
            item.medicine_id
            for item in prescribed_items
        }

        purchased_medicine_ids = {
            item.medicine_id
            for item in purchase_items
        }

        missing_medicines = (
            prescribed_medicine_ids
            - purchased_medicine_ids
        )

        # ----------------------------------------------------
        # Purchase is not complete yet
        # ----------------------------------------------------

        if missing_medicines:

            return {
                "message": (
                    "Purchase is not complete. "
                    "Some prescribed medicines "
                    "have not been added yet."
                ),
                "purchase_id": purchase.id,
                "completed": False,
                "already_sent": False,
                "missing_medicine_ids": list(
                    missing_medicines
                )
            }

    # ========================================================
    # PURCHASE IS COMPLETE
    # ========================================================

    try:

        result = (
            await send_purchase_medicine_sheet_email(
                db,
                purchase.id
            )
        )

        # ----------------------------------------------------
        # Record successful delivery
        # ----------------------------------------------------

        purchase.medicine_sheet_sent_at = (
            datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(purchase)

        return {
            "message": (
                "Purchase completed and "
                "digital medicine sheet sent "
                "successfully"
            ),
            "purchase_id": purchase.id,
            "completed": True,
            "already_sent": False,
            "email": result.get("email")
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Purchase is complete, but the "
                f"digital medicine sheet could "
                f"not be sent: {error}"
            )
        )