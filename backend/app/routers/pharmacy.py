from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.schemas.pharmacy import (
    PharmacyCreate,
    PharmacyResponse
)


router = APIRouter(
    prefix="/pharmacies",
    tags=["Pharmacy"]
)


# --------------------------------------------------
# ROLE CHECK
# --------------------------------------------------

def check_pharmacy_role(current_user: User):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can access this resource"
        )


# --------------------------------------------------
# CREATE PHARMACY PROFILE
# --------------------------------------------------

@router.post(
    "",
    response_model=PharmacyResponse
)
def create_pharmacy(
    pharmacy_data: PharmacyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check user role
    check_pharmacy_role(current_user)

    # Check whether this user already has a pharmacy
    existing_pharmacy = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.user_id == current_user.id
        )
        .first()
    )

    if existing_pharmacy:
        raise HTTPException(
            status_code=400,
            detail="Pharmacy profile already exists"
        )

    # Check license number
    existing_license = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.license_number
            == pharmacy_data.license_number
        )
        .first()
    )

    if existing_license:
        raise HTTPException(
            status_code=400,
            detail="License number already registered"
        )

    # Create pharmacy
    pharmacy = Pharmacy(
        user_id=current_user.id,
        pharmacy_name=pharmacy_data.pharmacy_name,
        license_number=pharmacy_data.license_number,
        address=pharmacy_data.address,
        city=pharmacy_data.city,
        state=pharmacy_data.state,
        pincode=pharmacy_data.pincode
    )

    db.add(pharmacy)
    db.commit()
    db.refresh(pharmacy)

    return pharmacy


# --------------------------------------------------
# GET MY PHARMACY PROFILE
# --------------------------------------------------

@router.get(
    "/me",
    response_model=PharmacyResponse
)
def get_my_pharmacy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check user role
    check_pharmacy_role(current_user)

    # Find pharmacy
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

    return pharmacy


# --------------------------------------------------
# UPDATE MY PHARMACY PROFILE
# --------------------------------------------------

@router.put(
    "/me",
    response_model=PharmacyResponse
)
def update_my_pharmacy(
    pharmacy_data: PharmacyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check user role
    check_pharmacy_role(current_user)

    # Find pharmacy
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

    # Check license number belongs to another pharmacy
    existing_license = (
        db.query(Pharmacy)
        .filter(
            Pharmacy.license_number
            == pharmacy_data.license_number,
            Pharmacy.id != pharmacy.id
        )
        .first()
    )

    if existing_license:
        raise HTTPException(
            status_code=400,
            detail="License number already registered"
        )

    # Update pharmacy
    pharmacy.pharmacy_name = pharmacy_data.pharmacy_name
    pharmacy.license_number = pharmacy_data.license_number
    pharmacy.address = pharmacy_data.address
    pharmacy.city = pharmacy_data.city
    pharmacy.state = pharmacy_data.state
    pharmacy.pincode = pharmacy_data.pincode

    db.commit()
    db.refresh(pharmacy)

    return pharmacy