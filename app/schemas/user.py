from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: str | None
    old_password: str | None
    new_password: str | None
    currency: str | None
    language: str | None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    total_income: float
    total_expense: float
    currency: str
    language: str
    profile_pic_url: str


    class Config:
        orm_mode = True

class LoginToken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: str | None

class UploadPhotoResponse(BaseModel):
    detail: str