from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db

from app.services.notification_service import generate_expiry_notifications
from app.services.email_service import send_email_notification

from app.models.user import User
from app.models.notification import Notification

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ---------------------------------------------------------
# Check Pharmacy Role
# ---------------------------------------------------------

def check_pharmacy_role(current_user: User):

    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can manage notifications"
        )


# ---------------------------------------------------------
# Create Notification
# ---------------------------------------------------------

@router.post(
    "",
    response_model=NotificationResponse
)
def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    notification = Notification(
        patient_id=notification_data.patient_id,
        medicine_id=notification_data.medicine_id,
        batch_id=notification_data.batch_id,
        notification_type=notification_data.notification_type,
        channel=notification_data.channel,
        scheduled_at=notification_data.scheduled_at,
        status=notification_data.status
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ---------------------------------------------------------
# Get All Notifications
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    notifications = (
        db.query(Notification)
        .order_by(Notification.id)
        .all()
    )

    return notifications


# ---------------------------------------------------------
# Generate Expiry Notifications
# ---------------------------------------------------------

@router.post("/generate-expiry")
def generate_expiry_notifications_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    notifications = generate_expiry_notifications(db)

    return {
        "message": "Expiry notifications generated successfully",
        "count": len(notifications),
        "notifications": [
            {
                "id": notification.id,
                "patient_id": notification.patient_id,
                "medicine_id": notification.medicine_id,
                "batch_id": notification.batch_id,
                "notification_type": notification.notification_type,
                "channel": notification.channel,
                "status": notification.status
            }
            for notification in notifications
        ]
    }


# ---------------------------------------------------------
# Send Email Notification
# ---------------------------------------------------------

@router.post("/{notification_id}/send-email")
async def send_email_notification_endpoint(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.channel != "EMAIL":
        raise HTTPException(
            status_code=400,
            detail="This notification is not configured for email"
        )

    if notification.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Notification has already been processed"
        )

    try:

        sent_notification = await send_email_notification(
            db,
            notification
        )

        return {
            "message": "Email sent successfully",
            "notification_id": sent_notification.id,
            "status": sent_notification.status
        }

    except Exception as error:

        db.rollback()

        print(
            f"MediTrack: Email delivery failed for notification "
            f"{notification_id}: {error}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Email delivery failed: {str(error)}"
        )


# ---------------------------------------------------------
# Get Notification By ID
# ---------------------------------------------------------

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    check_pharmacy_role(current_user)

    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return notification