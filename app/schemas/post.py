from pydantic import BaseModel
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str 
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True