from jose import jwt,JWTError
from datetime import datetime,timedelta
from App import schemas
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from App import schemas
from App.config import setting
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY=setting.secret_key
ALGORITHM=setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=setting.access_token_expires_minutes


def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expiry_time":expire.isoformat()})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("user_id")
        if id is None:
            raise credentials_exception
        return user_id
    except JWTError:
       raise credentials_exception
   
def get_current_user(token:str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",
headers={"WWW-Authenticate":"Bearer"})
    return verify_access_token(token,credentials_exception)