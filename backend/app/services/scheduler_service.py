from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.services.notification_service import (
    generate_expiry_notifications
)

from app.services.email_service import (
    send_email_notification
)

from app.models.notification import Notification


# =========================================================
# SCHEDULER
# =========================================================

scheduler = AsyncIOScheduler()


# =========================================================
# EXPIRY NOTIFICATION JOB
# =========================================================

async def run_expiry_notification_job():
    """
    Automatic daily MediTrack notification job.

    This job:

    1. Checks all medicine batches.
    2. Determines the expiry stage.
    3. Creates required expiry notifications.
    4. Finds pending EMAIL notifications.
    5. Sends the pending EMAIL notifications.
    6. Updates notification status through email_service.
    """

    db: Session = SessionLocal()

    try:

        print(
            "MediTrack: Running automatic "
            "expiry notification job..."
        )

        # =================================================
        # STEP 1
        # GENERATE EXPIRY NOTIFICATIONS
        # =================================================

        generated_notifications = (
            generate_expiry_notifications(db)
        )

        print(
            "MediTrack: Generated "
            f"{len(generated_notifications)} "
            "new notification(s)."
        )

        # =================================================
        # STEP 2
        # GET PENDING EMAIL NOTIFICATIONS
        # =================================================

        pending_notifications = (
            db.query(Notification)
            .filter(
                Notification.channel == "EMAIL",
                Notification.status == "PENDING"
            )
            .order_by(
                Notification.scheduled_at.asc()
            )
            .all()
        )

        print(
            "MediTrack: Found "
            f"{len(pending_notifications)} "
            "pending email notification(s)."
        )

        # =================================================
        # STEP 3
        # SEND EMAIL NOTIFICATIONS
        # =================================================

        for notification in pending_notifications:

            try:

                print(
                    "MediTrack: Sending email for "
                    f"notification ID "
                    f"{notification.id}..."
                )

                await send_email_notification(
                    db=db,
                    notification=notification
                )

                print(
                    "MediTrack: Email sent successfully "
                    f"for notification ID "
                    f"{notification.id}."
                )

            except Exception as error:

                # Roll back only the failed notification
                # transaction so other notifications can
                # continue processing.

                db.rollback()

                print(
                    "MediTrack: Failed to send email "
                    f"for notification ID "
                    f"{notification.id}: {error}"
                )

        # =================================================
        # JOB COMPLETED
        # =================================================

        print(
            "MediTrack: Automatic expiry notification "
            "job completed."
        )

    except Exception as error:

        db.rollback()

        print(
            "MediTrack: Notification job failed: "
            f"{error}"
        )

    finally:

        db.close()


# =========================================================
# START SCHEDULER
# =========================================================

def start_scheduler():
    """
    Start the MediTrack automatic scheduler.

    The expiry notification job runs every day at:

        12:00 AM

    Timezone:

        Asia/Kolkata

    The pharmacy does not need to manually generate
    expiry notifications.
    """

    # -----------------------------------------------------
    # PREVENT MULTIPLE SCHEDULER INSTANCES
    # -----------------------------------------------------

    if scheduler.running:
        print(
            "MediTrack: Scheduler is already running."
        )
        return

    # -----------------------------------------------------
    # ADD DAILY EXPIRY JOB
    # -----------------------------------------------------

    scheduler.add_job(

        run_expiry_notification_job,

        trigger=CronTrigger(
            hour=0,
            minute=0,
            second=0,
            timezone="Asia/Kolkata"
        ),

        id="daily_expiry_notification_job",

        replace_existing=True,

        max_instances=1,

        coalesce=True
    )

    # -----------------------------------------------------
    # START APSCHEDULER
    # -----------------------------------------------------

    scheduler.start()

    print(
        "MediTrack: Automatic notification scheduler "
        "started."
    )

    print(
        "MediTrack: Expiry notification job scheduled "
        "for every day at 12:00 AM IST."
    )


# =========================================================
# STOP SCHEDULER
# =========================================================

def stop_scheduler():
    """
    Stop the MediTrack scheduler safely.
    """

    if scheduler.running:

        scheduler.shutdown()

        print(
            "MediTrack: Notification scheduler stopped."
        )