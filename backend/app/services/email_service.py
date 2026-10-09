

import logging

from datetime import datetime, timezone


from zoneinfo import ZoneInfo




from sqlalchemy.orm import Session






from app.models.notification import Notification

from app.models.patient import Patient

from app.models.user import User

from app.models.medicine import Medicine

from app.models.medicine_batch import MedicineBatch

from app.models.purchase import Purchase

from app.models.purchase_medicine import PurchaseMedicine

from app.models.prescription import Prescription

from app.models.prescription_medicine import PrescriptionMedicine





logger = logging.getLogger(__name__)





# =========================================================

# RESEND EMAIL SENDER

# =========================================================



async def send_smtp_email(
    recipient_email: str,
    subject: str,
    content: str,
) -> None:
    """Send email using the Resend HTTPS API.

    The function name is retained so existing notification and digital
    medicine-sheet functions do not need to change.
    """
    import os
    import resend

    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("RESEND_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not configured")

    if not sender_email:
        raise RuntimeError("RESEND_FROM_EMAIL is not configured")

    resend.api_key = api_key

    try:
        result = await resend.Emails.send_async(
            {
                "from": sender_email,
                "to": [recipient_email],
                "subject": subject,
                "text": content,
            }
        )

        if isinstance(result, dict):
            message_id = result.get("id")
        else:
            message_id = getattr(result, "id", None)

        logger.info(
            "Resend accepted email request. Message ID: %s",
            message_id or "not returned",
        )
    except Exception:
        logger.exception("Resend email API request failed")
        raise


# =========================================================
# EXPIRY NOTIFICATION EMAIL
# =========================================================




# =========================================================



async def send_email_notification(

    db: Session,

    notification: Notification,

):

    """

    Send an expiry-related email and mark the notification

    as SENT only after successful email submission.

    """



    try:

        patient = (

            db.query(Patient)

            .filter(Patient.id == notification.patient_id)

            .first()

        )



        if not patient:

            raise ValueError("Patient not found")



        user = (

            db.query(User)

            .filter(User.id == patient.user_id)

            .first()

        )



        if not user or not user.email:

            raise ValueError("Patient email address not found")



        medicine = None



        if notification.medicine_id:

            medicine = (

                db.query(Medicine)

                .filter(Medicine.id == notification.medicine_id)

                .first()

            )



        batch = None



        if notification.batch_id:

            batch = (

                db.query(MedicineBatch)

                .filter(MedicineBatch.id == notification.batch_id)

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



        notification_type = notification.notification_type



        if notification_type == "EXPIRED_TODAY":

            subject = "MediTrack - Medicine Expiry Alert"

            expiry_message = (

                f'Your medicine "{medicine_name}" has reached '

                f'its recorded expiry date today ({expiry_date}).'

            )



        elif notification_type == "EXPIRY_URGENT_1_DAY":

            subject = "MediTrack - Medicine Expires Tomorrow"

            expiry_message = (

                f'Your medicine "{medicine_name}" is scheduled '

                f'to expire tomorrow ({expiry_date}).'

            )



        elif notification_type == "EXPIRY_URGENT_2_DAYS":

            subject = "MediTrack - Medicine Expiry Alert"

            expiry_message = (

                f'Your medicine "{medicine_name}" is scheduled '

                f'to expire in 2 days ({expiry_date}).'

            )



        elif notification_type.startswith("EXPIRY_WARNING_"):

            subject = "MediTrack - Medicine Expiry Reminder"

            expiry_message = (

                f'Your medicine "{medicine_name}" is approaching '

                f'its recorded expiry date ({expiry_date}).'

            )



        elif notification_type.startswith("EXPIRED_"):

            subject = "MediTrack - Expired Medicine Alert"

            expiry_message = (

                f'Your medicine "{medicine_name}" has passed '

                f'its recorded expiry date ({expiry_date}).'

            )



        else:

            subject = "MediTrack - Medicine Expiry Reminder"

            expiry_message = (

                f'Please check the recorded expiry information '

                f'for your medicine "{medicine_name}".'

            )



        content = f"""Hello {user.name},



This is a notification from MediTrack.



{expiry_message}



Expiry Date: {expiry_date}



Please check the medicine package and consult your pharmacist

or doctor for appropriate action.



This notification is generated from the medicine and expiry

information recorded in MediTrack.



Regards,

MediTrack

Digital Medicine Management & Reminder System

"""



        await send_smtp_email(

            recipient_email=user.email,

            subject=subject,

            content=content,

        )



        notification.status = "SENT"

        notification.sent_at = datetime.now(timezone.utc)



        db.commit()

        db.refresh(notification)



        return notification



    except Exception:

        db.rollback()



        logger.exception(

            "Could not send expiry notification ID %s",

            notification.id,

        )

        raise





# =========================================================

# PURCHASE DIGITAL MEDICINE SHEET

# =========================================================



async def send_purchase_medicine_sheet_email(

    db: Session,

    purchase_id: int,

):

    """

    Send the digital medicine sheet for a purchase.



    This function sends an email only. It does not create,

    complete, or modify a purchase.

    """



    purchase = (

        db.query(Purchase)

        .filter(Purchase.id == purchase_id)

        .first()

    )



    if not purchase:

        raise ValueError("Purchase not found")



    patient = (

        db.query(Patient)

        .filter(Patient.id == purchase.patient_id)

        .first()

    )



    if not patient:

        raise ValueError("Patient not found")



    user = (

        db.query(User)

        .filter(User.id == patient.user_id)

        .first()

    )



    if not user:

        raise ValueError("Patient user account not found")



    if not user.email:

        raise ValueError("Patient email address not found")



    purchase_items = (

        db.query(PurchaseMedicine)

        .filter(PurchaseMedicine.purchase_id == purchase_id)

        .all()

    )



    if not purchase_items:

        raise ValueError("No medicines found for this purchase")



    prescription = None



    if purchase.prescription_id:

        prescription = (

            db.query(Prescription)

            .filter(

                Prescription.id == purchase.prescription_id

            )

            .first()

        )



    medicine_lines = []



    for index, item in enumerate(purchase_items, start=1):

        medicine = (

            db.query(Medicine)

            .filter(Medicine.id == item.medicine_id)

            .first()

        )



        batch = (

            db.query(MedicineBatch)

            .filter(MedicineBatch.id == item.batch_id)

            .first()

        )



        if not medicine:

            continue



        batch_number = (

            getattr(batch, "batch_number", None)

            if batch

            else None

        )



        expiry_date = (

            batch.expiry_date.strftime("%d-%m-%Y")

            if batch and batch.expiry_date

            else "Not available"

        )



        prescription_medicine = None



        if prescription:

            prescription_medicine = (

                db.query(PrescriptionMedicine)

                .filter(

                    PrescriptionMedicine.prescription_id

                    == prescription.id,

                    PrescriptionMedicine.medicine_id

                    == item.medicine_id,

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



        medicine_lines.append(

            f"""

Medicine {index}

------------------------------



Medicine Name : {medicine.medicine_name}

Batch Number  : {batch_number or "Not available"}

Expiry Date   : {expiry_date}



Dosage        : {dosage}

Frequency     : {frequency}

Timing        : {timing}

Food          : {food_instruction}

Duration      : {duration_days} days

Quantity      : {item.quantity}

"""

        )



    if not medicine_lines:

        raise ValueError("No valid medicine details found")



    if prescription:

        prescription_date = (

            prescription.prescription_date.strftime("%d-%m-%Y")

            if prescription.prescription_date

            else "Not available"

        )



        prescription_section = f"""PRESCRIPTION DETAILS

====================



Prescription ID   : {prescription.id}

Prescription Date : {prescription_date}

"""

    else:

        prescription_section = """PRESCRIPTION DETAILS

====================



No prescription was linked to this purchase.

"""



    purchase_date = (

        purchase.purchase_date.strftime("%d-%m-%Y %I:%M %p")

        if purchase.purchase_date

        else "Not available"

    )



    total_amount = (

        f"₹{purchase.total_amount:.2f}"

        if purchase.total_amount is not None

        else "Not available"

    )



    subject = "MediTrack - Your Digital Medicine Sheet"



    content = f"""Hello {user.name},



Thank you for your purchase.



MediTrack has created your digital medicine sheet using the

medicine, batch and prescription information recorded by

the pharmacy.



PURCHASE DETAILS

================



Purchase ID   : {purchase.id}

Purchase Date : {purchase_date}

Total Amount  : {total_amount}



{prescription_section}



MEDICINE DETAILS

================

{"".join(medicine_lines)}



IMPORTANT

=========



This sheet contains the information recorded in MediTrack.

It does not independently change or recommend medication.



Follow the instructions recorded by your prescribing doctor

or pharmacy. Consult your doctor or pharmacist if you have

questions about your medication.



Regards,

MediTrack

Digital Medicine Management & Reminder System

"""



    await send_smtp_email(

        recipient_email=user.email,

        subject=subject,

        content=content,

    )



    logger.info(

        "Digital medicine sheet email submitted for purchase %s",

        purchase.id,

    )



    return {

        "message": "Digital medicine sheet sent successfully",

        "purchase_id": purchase.id,

        "patient_id": patient.id,

        "email": user.email,

    }





# =========================================================

# EXPIRY NOTIFICATION STAGE

# =========================================================



def get_expiry_stage(days_remaining: int):

    """Return the expiry notification stage for a given date."""



    if 10 <= days_remaining <= 15:

        return f"EXPIRY_WARNING_{days_remaining}_DAYS"



    if days_remaining == 2:

        return "EXPIRY_URGENT_2_DAYS"



    if days_remaining == 1:

        return "EXPIRY_URGENT_1_DAY"



    if days_remaining == 0:

        return "EXPIRED_TODAY"



    if -7 <= days_remaining <= -1:

        return f"EXPIRED_{abs(days_remaining)}_DAYS"



    return None





# =========================================================

# GENERATE EXPIRY NOTIFICATIONS

# =========================================================



def generate_expiry_notifications(db: Session):

    """

    Create pending expiry notifications for patients who have

    purchased the batch, enabled the channel and granted consent.



    SMS and WhatsApp records are queued only. This function

    does not send SMS or WhatsApp messages.

    """



    from app.models.notification_preferences import (

        NotificationPreference,

    )

    from app.models.consent import Consent



    created_notifications = []



    today = datetime.now(

        ZoneInfo("Asia/Kolkata")

    ).date()



    batches = db.query(MedicineBatch).all()



    for batch in batches:

        if not batch.expiry_date:

            continue



        days_remaining = (batch.expiry_date - today).days

        notification_stage = get_expiry_stage(days_remaining)



        if not notification_stage:

            continue



        purchase_medicines = (

            db.query(PurchaseMedicine)

            .filter(PurchaseMedicine.batch_id == batch.id)

            .all()

        )



        for purchase_medicine in purchase_medicines:

            purchase = (

                db.query(Purchase)

                .filter(

                    Purchase.id == purchase_medicine.purchase_id

                )

                .first()

            )



            if not purchase:

                continue



            patient_id = purchase.patient_id



            preferences = (

                db.query(NotificationPreference)

                .filter(

                    NotificationPreference.patient_id == patient_id

                )

                .first()

            )



            if not preferences:

                continue



            consent = (

                db.query(Consent)

                .filter(

                    Consent.patient_id == patient_id,

                    Consent.consent_type == "EXPIRY_NOTIFICATION",

                    Consent.status == "GRANTED",

                )

                .first()

            )



            if not consent:

                continue



            now = datetime.now(timezone.utc)



            channels = []



            if preferences.email_enabled:

                channels.append("EMAIL")



            if preferences.sms_enabled:

                channels.append("SMS")



            if preferences.whatsapp_enabled:

                channels.append("WHATSAPP")



            for channel in channels:

                existing = (

                    db.query(Notification)

                    .filter(

                        Notification.patient_id == patient_id,

                        Notification.batch_id == batch.id,

                        Notification.notification_type

                        == notification_stage,

                        Notification.channel == channel,

                    )

                    .first()

                )



                if existing:

                    continue



                notification = Notification(

                    patient_id=patient_id,

                    medicine_id=batch.medicine_id,

                    batch_id=batch.id,

                    notification_type=notification_stage,

                    channel=channel,

                    scheduled_at=now,

                    status="PENDING",

                )



                db.add(notification)

                db.flush()

                created_notifications.append(notification)



    db.commit()



    return created_notifications
