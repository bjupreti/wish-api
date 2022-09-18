from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..models.user import User as UserModel
from ..schemas.user import UserCreate, UserResponse
from ..database import get_db
from .. import utils

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = UserModel(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user


@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(id=str(id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} doesn't exist.")
    return user