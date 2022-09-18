from jose import JWTError, jwt
from datetime import datetime, timedelta

#SECRET_KEY
#Algorithm
#expiration_time (default forever)

SECRET_KEY = "b95745a244dcb59609e4006ce1d6e45b2934f13539ae4dc49913ea34187e531a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": str(expire)})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    