from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db

from app.models.user import User
from app.models.patient import Patient
from app.models.notification_preferences import NotificationPreference

from app.schemas.notification_preferences import (
    NotificationPreferenceCreate,
    NotificationPreferenceResponse
)


router = APIRouter(
    prefix="/notification-preferences",
    tags=["Notification Preferences"]
)


def check_patient_role(current_user: User):
    if current_user.role != "PATIENT":
        raise HTTPException(
            status_code=403,
            detail="Only patient users can manage notification preferences"
        )


@router.post(
    "",
    response_model=NotificationPreferenceResponse
)
def create_notification_preferences(
    preference_data: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_patient_role(current_user)

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    existing = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.patient_id == patient.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Notification preferences already exist"
        )

    preferences = NotificationPreference(
        patient_id=patient.id,
        whatsapp_enabled=preference_data.whatsapp_enabled,
        sms_enabled=preference_data.sms_enabled,
        email_enabled=preference_data.email_enabled
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


@router.get(
    "/me",
    response_model=NotificationPreferenceResponse
)
def get_my_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_patient_role(current_user)

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    preferences = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.patient_id == patient.id
        )
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="Notification preferences not found"
        )

    return preferences


@router.put(
    "/me",
    response_model=NotificationPreferenceResponse
)
def update_my_notification_preferences(
    preference_data: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_patient_role(current_user)

    patient = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    preferences = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.patient_id == patient.id
        )
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="Notification preferences not found"
        )

    preferences.whatsapp_enabled = preference_data.whatsapp_enabled
    preferences.sms_enabled = preference_data.sms_enabled
    preferences.email_enabled = preference_data.email_enabled

    db.commit()
    db.refresh(preferences)

    return preferences