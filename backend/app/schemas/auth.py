from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str