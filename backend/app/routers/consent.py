from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db

from app.models.user import User
from app.models.patient import Patient
from app.models.consent import Consent

from app.schemas.consent import (
    ConsentCreate,
    ConsentResponse
)


router = APIRouter(
    prefix="/consents",
    tags=["Consents"]
)


def check_patient_role(current_user: User):
    if current_user.role != "PATIENT":
        raise HTTPException(
            status_code=403,
            detail="Only patient users can manage consents"
        )


@router.post(
    "",
    response_model=ConsentResponse
)
def create_consent(
    consent_data: ConsentCreate,
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
        db.query(Consent)
        .filter(
            Consent.patient_id == patient.id,
            Consent.consent_type == consent_data.consent_type
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Consent already exists for this type"
        )

    now = datetime.now(timezone.utc)

    consent = Consent(
        patient_id=patient.id,
        consent_type=consent_data.consent_type,
        status=consent_data.status,
        given_at=now if consent_data.status == "GRANTED" else None,
        revoked_at=None
    )

    db.add(consent)
    db.commit()
    db.refresh(consent)

    return consent


@router.get(
    "/me",
    response_model=list[ConsentResponse]
)
def get_my_consents(
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

    return (
        db.query(Consent)
        .filter(Consent.patient_id == patient.id)
        .order_by(Consent.id)
        .all()
    )