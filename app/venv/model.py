
from pydantic import BaseModel
from typing import Union


class airportData(BaseModel):
    user: Union[str, None] = None
    icao: str
    iata: str
    name: str
    type: str
    country: str
    continent: str
    wikipedia: str
    website: str

class showAirportData(BaseModel):
    icao: str
    iata: str
    name: str
    type: str
    country: str
    continent: str
    wikipedia: str
    website: str
    
class userModel(BaseModel):
    username: str
    email: str
    password: str

class showUserModel(BaseModel):
    username: str
    email: str

class changePasswordModel(BaseModel):
    username: str
    password: str
    newPassword: str
    
class login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None

