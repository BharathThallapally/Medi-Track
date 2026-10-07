from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.medicine_batch import MedicineBatch
from app.models.purchase_medicine import PurchaseMedicine
from app.models.purchase import Purchase
from app.models.notification_preferences import NotificationPreference
from app.models.consent import Consent
from app.models.notification import Notification


def get_expiry_stage(days_remaining: int):
    """
    Determine which expiry notification stage applies.

    Positive number  = days before expiry
    Zero              = expiry day
    Negative number   = days after expiry
    """

    # ---------------------------------------------------------
    # 15 to 10 DAYS BEFORE EXPIRY
    # ---------------------------------------------------------

    if 10 <= days_remaining <= 15:
        return f"EXPIRY_WARNING_{days_remaining}_DAYS"

    # ---------------------------------------------------------
    # 2 DAYS BEFORE EXPIRY
    # ---------------------------------------------------------

    if days_remaining == 2:
        return "EXPIRY_URGENT_2_DAYS"

    # ---------------------------------------------------------
    # 1 DAY BEFORE EXPIRY
    # ---------------------------------------------------------

    if days_remaining == 1:
        return "EXPIRY_URGENT_1_DAY"

    # ---------------------------------------------------------
    # EXPIRY DAY
    # ---------------------------------------------------------

    if days_remaining == 0:
        return "EXPIRED_TODAY"

    # ---------------------------------------------------------
    # 1 TO 7 DAYS AFTER EXPIRY
    # ---------------------------------------------------------

    if -7 <= days_remaining <= -1:
        days_expired = abs(days_remaining)

        return f"EXPIRED_{days_expired}_DAYS"

    # ---------------------------------------------------------
    # Outside notification period
    # ---------------------------------------------------------

    return None


def generate_expiry_notifications(db: Session):
    """
    Automatically create expiry notifications for eligible
    patients based on the medicine batch expiry date.

    Notification schedule:

    15 days before
    14 days before
    13 days before
    12 days before
    11 days before
    10 days before

    2 days before
    1 day before

    Expiry day

    1 day after
    2 days after
    3 days after
    4 days after
    5 days after
    6 days after
    7 days after

    Duplicate notifications are prevented for each
    patient + batch + notification stage + channel.
    """

    created_notifications = []

    # Current date in UTC.
    # Medicine expiry dates are date-based, so only the date
    # portion is used.
    today = datetime.now(
    ZoneInfo("Asia/Kolkata")
).date()

    # ---------------------------------------------------------
    # GET ALL MEDICINE BATCHES
    # ---------------------------------------------------------

    batches = db.query(MedicineBatch).all()

    for batch in batches:

        if not batch.expiry_date:
            continue

        # -----------------------------------------------------
        # CALCULATE DAYS REMAINING
        # -----------------------------------------------------

        days_remaining = (
            batch.expiry_date - today
        ).days

        # -----------------------------------------------------
        # DETERMINE NOTIFICATION STAGE
        # -----------------------------------------------------

        notification_stage = get_expiry_stage(
            days_remaining
        )

        # No notification required for this date.
        if not notification_stage:
            continue

        # -----------------------------------------------------
        # FIND PATIENTS WHO PURCHASED THIS BATCH
        # -----------------------------------------------------

        purchase_medicines = (
            db.query(PurchaseMedicine)
            .filter(
                PurchaseMedicine.batch_id == batch.id
            )
            .all()
        )

        for purchase_medicine in purchase_medicines:

            purchase = (
                db.query(Purchase)
                .filter(
                    Purchase.id
                    == purchase_medicine.purchase_id
                )
                .first()
            )

            if not purchase:
                continue

            patient_id = purchase.patient_id

            # -------------------------------------------------
            # NOTIFICATION PREFERENCES
            # -------------------------------------------------

            preferences = (
                db.query(NotificationPreference)
                .filter(
                    NotificationPreference.patient_id
                    == patient_id
                )
                .first()
            )

            if not preferences:
                continue

            # -------------------------------------------------
            # EXPLICIT CONSENT
            # -------------------------------------------------

            consent = (
                db.query(Consent)
                .filter(
                    Consent.patient_id == patient_id,
                    Consent.consent_type
                    == "EXPIRY_NOTIFICATION",
                    Consent.status == "GRANTED"
                )
                .first()
            )

            if not consent:
                continue

            now = datetime.now(timezone.utc)

            # =================================================
            # EMAIL
            # =================================================

            if preferences.email_enabled:

                existing_email = (
                    db.query(Notification)
                    .filter(
                        Notification.patient_id
                        == patient_id,

                        Notification.batch_id
                        == batch.id,

                        Notification.notification_type
                        == notification_stage,

                        Notification.channel
                        == "EMAIL"
                    )
                    .first()
                )

                if not existing_email:

                    notification = Notification(
                        patient_id=patient_id,
                        medicine_id=batch.medicine_id,
                        batch_id=batch.id,

                        notification_type=
                        notification_stage,

                        channel="EMAIL",

                        scheduled_at=now,

                        status="PENDING"
                    )

                    db.add(notification)
                    db.flush()

                    created_notifications.append(
                        notification
                    )

            # =================================================
            # SMS
            # =================================================

            if preferences.sms_enabled:

                existing_sms = (
                    db.query(Notification)
                    .filter(
                        Notification.patient_id
                        == patient_id,

                        Notification.batch_id
                        == batch.id,

                        Notification.notification_type
                        == notification_stage,

                        Notification.channel
                        == "SMS"
                    )
                    .first()
                )

                if not existing_sms:

                    notification = Notification(
                        patient_id=patient_id,
                        medicine_id=batch.medicine_id,
                        batch_id=batch.id,

                        notification_type=
                        notification_stage,

                        channel="SMS",

                        scheduled_at=now,

                        status="PENDING"
                    )

                    db.add(notification)
                    db.flush()

                    created_notifications.append(
                        notification
                    )

            # =================================================
            # WHATSAPP
            # =================================================

            if preferences.whatsapp_enabled:

                existing_whatsapp = (
                    db.query(Notification)
                    .filter(
                        Notification.patient_id
                        == patient_id,

                        Notification.batch_id
                        == batch.id,

                        Notification.notification_type
                        == notification_stage,

                        Notification.channel
                        == "WHATSAPP"
                    )
                    .first()
                )

                if not existing_whatsapp:

                    notification = Notification(
                        patient_id=patient_id,
                        medicine_id=batch.medicine_id,
                        batch_id=batch.id,

                        notification_type=
                        notification_stage,

                        channel="WHATSAPP",

                        scheduled_at=now,

                        status="PENDING"
                    )

                    db.add(notification)
                    db.flush()

                    created_notifications.append(
                        notification
                    )

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    db.commit()

    return created_notifications