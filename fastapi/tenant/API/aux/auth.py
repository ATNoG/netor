# @Author: Daniel Gomes
# @Date:   2022-08-23 14:37:01
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-08-26 09:57:17
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from aux import auth, constants
from datetime import datetime, timedelta
from typing import Optional
import aux.constants as Constants 
from exceptions.auth import CouldNotDecodeBearerToken

# constants
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    print(hashed_password, pwd_context.hash(plain_password))
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY,
                             algorithm=constants.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str):
    try:
        payload = jwt.decode(token, Constants.SECRET_KEY, 
                             algorithms=[Constants.ALGORITHM])
        username = payload.get("sub")
        return username
    except Exception:
        raise CouldNotDecodeBearerToken
