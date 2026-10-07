from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth import UserRegister


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# TEST AUTHENTICATION ROUTER
# --------------------------------------------------

@router.get("/test")
def auth_test():
    return {
        "message": "Authentication router is working"
    }


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

@router.post("/register")
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    if user_data.email:
        existing_email = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    # Check if phone already exists
    if user_data.phone:
        existing_phone = (
            db.query(User)
            .filter(User.phone == user_data.phone)
            .first()
        )

        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Phone number already registered"
            )

    # Hash password
    hashed_password = hash_password(
        user_data.password
    )

    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        role=user_data.role
    )

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone,
            "role": new_user.role,
            "is_active": new_user.is_active
        }
    }


# --------------------------------------------------
# USER LOGIN
# --------------------------------------------------

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Swagger sends the email through the "username" field
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # Create JWT access token
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# --------------------------------------------------
# GET CURRENT LOGGED-IN USER
# --------------------------------------------------

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Authenticated user",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "role": current_user.role,
            "is_active": current_user.is_active
        }
    }