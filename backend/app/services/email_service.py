from datetime import datetime, timezone
from email.message import EmailMessage

from aiosmtplib import SMTP
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.notification import Notification
from app.models.patient import Patient
from app.models.user import User
from app.models.medicine import Medicine
from app.models.medicine_batch import MedicineBatch

from app.models.purchase import Purchase
from app.models.purchase_medicine import PurchaseMedicine
from app.models.prescription import Prescription
from app.models.prescription_medicine import PrescriptionMedicine


# =========================================================
# SMTP EMAIL SENDER
# =========================================================

async def send_smtp_email(
    recipient_email: str,
    subject: str,
    content: str
):
    """
    Send an email through the configured Gmail SMTP account.
    """

    message = EmailMessage()

    message["From"] = settings.SMTP_FROM
    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(content)

    smtp = SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        timeout=30
    )

    try:

        await smtp.connect()

        await smtp.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD
        )

        await smtp.send_message(message)

    finally:

        if smtp.is_connected:
            await smtp.quit()


# =========================================================
# EXPIRY NOTIFICATION EMAIL
# =========================================================

async def send_email_notification(
    db: Session,
    notification: Notification
):
    """
    Send an expiry-related email notification.
    """

    # -----------------------------------------------------
    # Get patient
    # -----------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == notification.patient_id
        )
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    # -----------------------------------------------------
    # Get patient user account
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == patient.user_id
        )
        .first()
    )

    if not user:
        raise ValueError(
            "Patient user account not found"
        )

    if not user.email:
        raise ValueError(
            "Patient email address not found"
        )

    # -----------------------------------------------------
    # Get medicine
    # -----------------------------------------------------

    medicine = None

    if notification.medicine_id:

        medicine = (
            db.query(Medicine)
            .filter(
                Medicine.id == notification.medicine_id
            )
            .first()
        )

    # -----------------------------------------------------
    # Get medicine batch
    # -----------------------------------------------------

    batch = None

    if notification.batch_id:

        batch = (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.id == notification.batch_id
            )
            .first()
        )

    medicine_name = (
        medicine.medicine_name
        if medicine
        else "Your medicine"
    )

    expiry_date = (
        batch.expiry_date.strftime("%d-%m-%Y")
        if batch and batch.expiry_date
        else "Not available"
    )

    # -----------------------------------------------------
    # Determine expiry message
    # -----------------------------------------------------

    notification_type = notification.notification_type

    if notification_type == "EXPIRED_TODAY":

        subject = (
            "MediTrack - Medicine Expiry Alert"
        )

        expiry_message = (
            f'Your medicine "{medicine_name}" has '
            f'reached its recorded expiry date today '
            f'({expiry_date}).'
        )

    elif notification_type == "EXPIRY_URGENT_1_DAY":

        subject = (
            "MediTrack - Medicine Expires Tomorrow"
        )

        expiry_message = (
            f'Your medicine "{medicine_name}" is '
            f'scheduled to expire tomorrow '
            f'({expiry_date}).'
        )

    elif notification_type == "EXPIRY_URGENT_2_DAYS":

        subject = (
            "MediTrack - Medicine Expiry Alert"
        )

        expiry_message = (
            f'Your medicine "{medicine_name}" is '
            f'scheduled to expire in 2 days '
            f'({expiry_date}).'
        )

    elif notification_type.startswith(
        "EXPIRY_WARNING_"
    ):

        subject = (
            "MediTrack - Medicine Expiry Reminder"
        )

        expiry_message = (
            f'Your medicine "{medicine_name}" is '
            f'approaching its recorded expiry date '
            f'({expiry_date}).'
        )

    elif notification_type.startswith(
        "EXPIRED_"
    ):

        subject = (
            "MediTrack - Expired Medicine Alert"
        )

        expiry_message = (
            f'Your medicine "{medicine_name}" has '
            f'passed its recorded expiry date '
            f'({expiry_date}).'
        )

    else:

        subject = (
            "MediTrack - Medicine Expiry Reminder"
        )

        expiry_message = (
            f'Please check the recorded expiry '
            f'information for your medicine '
            f'"{medicine_name}".'
        )

    # -----------------------------------------------------
    # Email content
    # -----------------------------------------------------

    content = f"""Hello {user.name},

This is a notification from MediTrack.

{expiry_message}

Expiry Date: {expiry_date}

Please check the medicine package and consult your pharmacist or doctor for appropriate action.

This notification is generated from the medicine and expiry information recorded in MediTrack.

Regards,
MediTrack
Digital Medicine Management & Reminder System
"""

    # -----------------------------------------------------
    # Send email
    # -----------------------------------------------------

    await send_smtp_email(
        recipient_email=user.email,
        subject=subject,
        content=content
    )

    # -----------------------------------------------------
    # Mark notification as SENT
    # -----------------------------------------------------

    notification.status = "SENT"

    notification.sent_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(notification)

    return notification


# =========================================================
# PURCHASE DIGITAL MEDICINE SHEET
# =========================================================

async def send_purchase_medicine_sheet_email(
    db: Session,
    purchase_id: int
):
    """
    Send the patient a digital medicine sheet after
    completing a medicine purchase.

    The information comes from the recorded purchase,
    prescription, medicine and batch records.

    This function does NOT create or modify medical advice.
    """

    # -----------------------------------------------------
    # Get purchase
    # -----------------------------------------------------

    purchase = (
        db.query(Purchase)
        .filter(
            Purchase.id == purchase_id
        )
        .first()
    )

    if not purchase:
        raise ValueError(
            "Purchase not found"
        )

    # -----------------------------------------------------
    # Get patient
    # -----------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == purchase.patient_id
        )
        .first()
    )

    if not patient:
        raise ValueError(
            "Patient not found"
        )

    # -----------------------------------------------------
    # Get patient user account
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == patient.user_id
        )
        .first()
    )

    if not user:
        raise ValueError(
            "Patient user account not found"
        )

    if not user.email:
        raise ValueError(
            "Patient email address not found"
        )

    # -----------------------------------------------------
    # Get purchase medicines
    # -----------------------------------------------------

    purchase_items = (
        db.query(PurchaseMedicine)
        .filter(
            PurchaseMedicine.purchase_id == purchase_id
        )
        .all()
    )

    if not purchase_items:
        raise ValueError(
            "No medicines found for this purchase"
        )

    # -----------------------------------------------------
    # Get prescription
    # -----------------------------------------------------

    prescription = None

    if purchase.prescription_id:

        prescription = (
            db.query(Prescription)
            .filter(
                Prescription.id
                == purchase.prescription_id
            )
            .first()
        )

    # -----------------------------------------------------
    # Build medicine sheet
    # -----------------------------------------------------

    medicine_lines = []

    for index, item in enumerate(
        purchase_items,
        start=1
    ):

        medicine = (
            db.query(Medicine)
            .filter(
                Medicine.id == item.medicine_id
            )
            .first()
        )

        batch = (
            db.query(MedicineBatch)
            .filter(
                MedicineBatch.id == item.batch_id
            )
            .first()
        )

        if not medicine:
            continue

        medicine_name = (
            medicine.medicine_name
        )

        batch_number = (
            getattr(
                batch,
                "batch_number",
                None
            )
            if batch
            else None
        )

        expiry_date = (
            batch.expiry_date.strftime(
                "%d-%m-%Y"
            )
            if batch and batch.expiry_date
            else "Not available"
        )

        # -------------------------------------------------
        # Get prescription instructions for this medicine
        # -------------------------------------------------

        prescription_medicine = None

        if prescription:

            prescription_medicine = (
                db.query(
                    PrescriptionMedicine
                )
                .filter(
                    PrescriptionMedicine.prescription_id
                    == prescription.id,
                    PrescriptionMedicine.medicine_id
                    == item.medicine_id
                )
                .first()
            )

        dosage = (
            prescription_medicine.dosage
            if prescription_medicine
            else "Not recorded"
        )

        frequency = (
            prescription_medicine.frequency
            if prescription_medicine
            else "Not recorded"
        )

        timing = (
            prescription_medicine.timing
            if prescription_medicine
            and prescription_medicine.timing
            else "Not recorded"
        )

        food_instruction = (
            prescription_medicine.food_instruction
            if prescription_medicine
            and prescription_medicine.food_instruction
            else "Not recorded"
        )

        duration_days = (
            prescription_medicine.duration_days
            if prescription_medicine
            else "Not recorded"
        )

        quantity = item.quantity

        medicine_lines.append(
            f"""
Medicine {index}
------------------------------

Medicine Name : {medicine_name}
Batch Number  : {batch_number or "Not available"}
Expiry Date   : {expiry_date}

Dosage        : {dosage}
Frequency     : {frequency}
Timing        : {timing}
Food          : {food_instruction}
Duration      : {duration_days} days
Quantity      : {quantity}
"""
        )

    if not medicine_lines:
        raise ValueError(
            "No valid medicine details found"
        )

    # -----------------------------------------------------
    # Prescription information
    # -----------------------------------------------------

    if prescription:

        prescription_date = (
            prescription.prescription_date.strftime(
                "%d-%m-%Y"
            )
            if prescription.prescription_date
            else "Not available"
        )

        prescription_section = f"""
PRESCRIPTION DETAILS
====================

Prescription ID : {prescription.id}
Prescription Date : {prescription_date}
"""

    else:

        prescription_section = """
PRESCRIPTION DETAILS
====================

No prescription was linked to this purchase.
"""

    # -----------------------------------------------------
    # Purchase information
    # -----------------------------------------------------

    purchase_date = (
        purchase.purchase_date.strftime(
            "%d-%m-%Y %I:%M %p"
        )
        if purchase.purchase_date
        else "Not available"
    )

    total_amount = (
        f"₹{purchase.total_amount:.2f}"
        if purchase.total_amount is not None
        else "Not available"
    )

    # -----------------------------------------------------
    # Email subject
    # -----------------------------------------------------

    subject = (
        "MediTrack - Your Digital Medicine Sheet"
    )

    # -----------------------------------------------------
    # Email body
    # -----------------------------------------------------

    content = f"""Hello {user.name},

Thank you for your purchase.

MediTrack has created your digital medicine sheet based on the medicine, batch and prescription information recorded by the pharmacy.

PURCHASE DETAILS
================

Purchase ID  : {purchase.id}
Purchase Date: {purchase_date}
Total Amount : {total_amount}

{prescription_section}

MEDICINE DETAILS
================
{"".join(medicine_lines)}

IMPORTANT
=========

This digital medicine sheet contains the medicine and prescription information recorded in MediTrack.

MediTrack does not independently change, increase, decrease, stop or recommend any medication.

Please follow the instructions recorded by your prescribing doctor/pharmacy. If you have questions about your medication, consult your doctor or pharmacist.

Regards,
MediTrack
Digital Medicine Management & Reminder System
"""

    # -----------------------------------------------------
    # Send email
    # -----------------------------------------------------

    await send_smtp_email(
        recipient_email=user.email,
        subject=subject,
        content=content
    )

    return {
        "message": (
            "Digital medicine sheet sent successfully"
        ),
        "purchase_id": purchase.id,
        "patient_id": patient.id,
        "email": user.email
    }