from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..models.user import User as UserModel
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..database import get_db
from ..oauth2 import get_current_user
from .. import utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check if user already exists
    db_user = db.query(UserModel).filter_by(email=user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{db_user.email} already exist.")

    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = UserModel(**user.dict())
    db.add(new_user)
    db.commit()
    return new_user


@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, updated_user: UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_query = db.query(UserModel).filter_by(id=str(current_user.id))
    user = user_query.first()
    updated_user = updated_user.dict(exclude_unset=True)

    if "old_password" in updated_user and not utils.verify(updated_user["old_password"], user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Incorrect Old Password")
    
    if "old_password" in updated_user:
        updated_user.pop("old_password")
        # TODO: validate new_password
        # if not valid raise HTTPException
        updated_user["password"] = utils.hash(updated_user["new_password"])

        updated_user.pop("new_password")

    for key, value in updated_user.items():
        setattr(user, key, value)

    db.commit()

    return user_query.first()
    



@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(id=str(id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} doesn't exist.")
    return user