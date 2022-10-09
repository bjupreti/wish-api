from pydantic import BaseModel
from datetime import datetime

from .user import UserResponse

class TransactionBase(BaseModel):
    title: str
    amount: float
    category: str
    # is_archived: bool
    is_income: bool
    is_recurring: bool

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    is_expense: bool
    created_at: datetime

    class Config:
        orm_mode = True
