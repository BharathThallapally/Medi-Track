from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.expiry_service import get_expiry_status

from app.schemas.expiry import (
    ExpiryResponse,
    ExpiryListResponse
)

from app.core.security import get_current_user
from app.database.connection import get_db

from app.models.user import User
from app.models.medicine import Medicine
from app.models.medicine_batch import MedicineBatch

from app.schemas.medicine_batch import (
    MedicineBatchCreate,
    MedicineBatchUpdate,
    MedicineBatchResponse
)


router = APIRouter(
    prefix="/medicine-batches",
    tags=["Medicine Batches"]
)


def check_pharmacy_role(current_user: User):
    if current_user.role != "PHARMACY":
        raise HTTPException(
            status_code=403,
            detail="Only pharmacy users can manage medicine batches"
        )


# ============================================================
# CREATE MEDICINE BATCH
# ============================================================

@router.post(
    "",
    response_model=MedicineBatchResponse
)
def create_medicine_batch(
    batch_data: MedicineBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    # Check whether medicine exists
    medicine = db.query(Medicine).filter(
        Medicine.id == batch_data.medicine_id
    ).first()

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    # Validate manufacturing and expiry dates
    if (
        batch_data.manufacturing_date is not None
        and batch_data.expiry_date <= batch_data.manufacturing_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Expiry date must be after manufacturing date"
        )

    # Check duplicate batch number
    existing_batch = db.query(MedicineBatch).filter(
        MedicineBatch.medicine_id == batch_data.medicine_id,
        MedicineBatch.batch_number == batch_data.batch_number
    ).first()

    if existing_batch:
        raise HTTPException(
            status_code=400,
            detail="Batch number already exists for this medicine"
        )

    # Create batch
    new_batch = MedicineBatch(
        medicine_id=batch_data.medicine_id,
        batch_number=batch_data.batch_number,
        manufacturing_date=batch_data.manufacturing_date,
        expiry_date=batch_data.expiry_date
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return new_batch


# ============================================================
# GET ALL MEDICINE BATCHES
# ============================================================

@router.get(
    "",
    response_model=list[MedicineBatchResponse]
)
def get_medicine_batches(
    medicine_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    query = db.query(MedicineBatch)

    # Optional medicine filter
    if medicine_id is not None:
        query = query.filter(
            MedicineBatch.medicine_id == medicine_id
        )

    batches = query.order_by(
        MedicineBatch.id
    ).all()

    return batches


# ============================================================
# GET EXPIRY LIST
# IMPORTANT: This route comes BEFORE /{batch_id}
# ============================================================

@router.get(
    "/expiry-list",
    response_model=list[ExpiryListResponse]
)
def get_expiry_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    # Join medicine_batches with medicines
    batches = (
        db.query(
            MedicineBatch,
            Medicine.medicine_name
        )
        .join(
            Medicine,
            Medicine.id == MedicineBatch.medicine_id
        )
        .order_by(
            MedicineBatch.expiry_date
        )
        .all()
    )

    expiry_list = []

    for batch, medicine_name in batches:

        expiry_info = get_expiry_status(
            batch.expiry_date
        )

        expiry_list.append({
            "medicine_id": batch.medicine_id,
            "medicine_name": medicine_name,
            "batch_id": batch.id,
            "batch_number": batch.batch_number,
            "expiry_date": batch.expiry_date,
            "days_remaining": expiry_info["days_remaining"],
            "status": expiry_info["status"]
        })

    return expiry_list


# ============================================================
# GET SINGLE MEDICINE BATCH
# ============================================================

@router.get(
    "/{batch_id}",
    response_model=MedicineBatchResponse
)
def get_medicine_batch(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    batch = db.query(MedicineBatch).filter(
        MedicineBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Medicine batch not found"
        )

    return batch


# ============================================================
# GET SINGLE BATCH EXPIRY STATUS
# ============================================================

@router.get(
    "/{batch_id}/expiry",
    response_model=ExpiryResponse
)
def get_batch_expiry_status(
    batch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    batch = db.query(MedicineBatch).filter(
        MedicineBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Medicine batch not found"
        )

    # Calculate expiry information
    expiry_info = get_expiry_status(
        batch.expiry_date
    )

    return {
        "medicine_id": batch.medicine_id,
        "batch_id": batch.id,
        "batch_number": batch.batch_number,
        "expiry_date": batch.expiry_date,
        "days_remaining": expiry_info["days_remaining"],
        "status": expiry_info["status"]
    }


# ============================================================
# UPDATE MEDICINE BATCH
# ============================================================

@router.put(
    "/{batch_id}",
    response_model=MedicineBatchResponse
)
def update_medicine_batch(
    batch_id: int,
    batch_data: MedicineBatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_pharmacy_role(current_user)

    batch = db.query(MedicineBatch).filter(
        MedicineBatch.id == batch_id
    ).first()

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Medicine batch not found"
        )

    # Validate dates
    if (
        batch_data.manufacturing_date is not None
        and batch_data.expiry_date <= batch_data.manufacturing_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Expiry date must be after manufacturing date"
        )

    # Check duplicate batch number
    existing_batch = db.query(MedicineBatch).filter(
        MedicineBatch.medicine_id == batch.medicine_id,
        MedicineBatch.batch_number == batch_data.batch_number,
        MedicineBatch.id != batch_id
    ).first()

    if existing_batch:
        raise HTTPException(
            status_code=400,
            detail="Batch number already exists for this medicine"
        )

    # Update batch
    batch.batch_number = batch_data.batch_number
    batch.manufacturing_date = batch_data.manufacturing_date
    batch.expiry_date = batch_data.expiry_date

    db.commit()
    db.refresh(batch)

    return batch