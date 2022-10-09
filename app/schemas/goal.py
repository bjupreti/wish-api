from pydantic import BaseModel
from datetime import datetime

from .user import UserResponse

class GoalBase(BaseModel):
    name: str
    price: float
    total_amount: float

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    pass

class GoalResponse(GoalBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True
