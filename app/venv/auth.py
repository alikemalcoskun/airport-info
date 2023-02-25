from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import database
from model import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")
class Hash:

    def getHashedPassword(password):
        return pwd_context.hash(password)

    def verifyPassword(hashedPassword, plainPassword):
        return pwd_context.verify(plainPassword, hashedPassword)


class Token:
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES):
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

    def createAccessToken(data: dict, expiresDelta: Union[timedelta, None] = None):
        toEncode = data.copy()
        if expiresDelta:
            expire = datetime.utcnow() + expiresDelta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        toEncode.update({"exp": expire})
        encodedJwt = jwt.encode(toEncode, Token.SECRET_KEY, algorithm=Token.ALGORITHM)
        return encodedJwt


    def verifyToken(token: str, credentialsException):
        try:
            payload = jwt.decode(token, Token.SECRET_KEY, algorithms=[Token.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentialsException
            tokenData = TokenData(email=email)
            return tokenData
        except JWTError:
            raise credentialsException





class oauth2:


    async def getUser(email: str):
        result = await database.getUserByEmail(email)
        if not result: return None
        return result


    async def getCurrentUser(token: str = Depends(oauth2Scheme)):
        credentialsException = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        tokenData = Token.verifyToken(token, credentialsException)
        user = await oauth2.getUser(email=tokenData.email)
        if user is None:
            raise credentialsException
        return user