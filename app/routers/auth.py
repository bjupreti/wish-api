from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from ..models.user import User as UserModel 
from ..database import get_db
from .. import utils, oauth2

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(UserModel).filter_by(email=user_credentials.username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    # create a token
    access_token = oauth2.create_access_token(data={"id": user.id, "email": user.email})
    # return token
    return {"access_token": access_token, "token_type": "bearer"}