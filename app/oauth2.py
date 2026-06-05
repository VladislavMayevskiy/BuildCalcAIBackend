from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from . import database
from app.models.users import Users
from app.schemas.token import TokenData
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_acces_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_acces_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise credential_exception

        token_data = TokenData(id=user_id)
        return token_data

    except JWTError:
        raise credential_exception
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not valid credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_acces_token(token, credential_exception)
    user = db.query(Users).filter(Users.id == token.id).first()
    return user