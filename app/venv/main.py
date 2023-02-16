from datetime import timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from model import airportData, userModel, showUserModel, login, showAirportData
import redis
import redisConfig
import redisCache
import airport
import database
from auth import Hash, Token, oauth2

r = redisConfig.redisConnect()


app = FastAPI(title="AirportInfo",)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post('/api/v1/user/create-user', response_model=showUserModel, tags=['User'])
async def createUser(model: userModel):
    hashedPassword = Hash.getHashedPassword(model.password)
    newUser = userModel(username=model.username, email=model.email, password=hashedPassword)
    result = await database.createUser(newUser)
    if not result: raise HTTPException(400)
    return result


@app.get('/api/v1/user/get-user/{username}', tags=['User'])
async def getUser(username: str):
    result = await database.getUser(username)
    if not result: raise HTTPException(400)
    return result


@app.post('/api/v1/user/login', tags=['User'])
async def login(request: OAuth2PasswordRequestForm = Depends()):
    user = await database.getUser(request.username)
    if not user: raise HTTPException(status_code=404, detail=f"Invalid Credentials")
    if not Hash.verifyPassword(user['password'], request.password): raise HTTPException(status_code=404, 
    detail=f"Invalid Username or Password")

    accessTokenExpires = timedelta(minutes=Token.ACCESS_TOKEN_EXPIRE_MINUTES)
    accessToken = Token.createAccessToken(
        data={"sub": user['email']}, expiresDelta=accessTokenExpires
    )
    return {"access_token": accessToken, "token_type": "bearer"}




@app.put('/api/v1/user/change-password', response_model=showUserModel, tags=['User'])
async def changePassword(username: str, password: str, newPassword: str, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    currentUser = await database.getUser(username)
    if not currentUser: raise HTTPException(status_code=404, detail=f"Invalid User")

    if not Hash.verifyPassword(currentUser['password'], password):
        raise HTTPException(status_code=404, detail=f"Invalid Password")

    hashedPassword = Hash.getHashedPassword(newPassword)
    result = await database.updateUser(currentUser['username'], updatedPassword=hashedPassword)
    if not result: raise HTTPException(400)


    currentUser = await database.getUser(username)
    return currentUser



@app.delete('/api/v1/user/delete-user', tags=['User'])
async def deleteUser(username: str, password: str, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    currentUser = await database.getUser(username)
    if not currentUser: raise HTTPException(status_code=404, detail=f"Invalid User")

    if not Hash.verifyPassword(currentUser['password'], password):
        raise HTTPException(status_code=404, detail=f"Invalid Password")

    hashedPassword = Hash.getHashedPassword(password)
    result = await database.deleteUser(username)
    if not result: raise HTTPException(400)
    
    return True






@app.get('/')
async def Home():
    return r.ping()


@app.get('/api/v1/data/get-info/{icao}', response_model=showAirportData, tags=['Airport Data'])
async def getAirportInfo(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    cache = redisCache.getData(icao)

    if cache is None:
        data = airport.getAirportInfo(icao)
        redisCache.setData(icao, json.dumps(data))
        print("Data received from API")
        return data
    
    print("Data received from cache")
    return json.loads(cache)
    

@app.post('/api/v1/data/add-to-favorites', tags=['Airport Data'])
async def addToFavorites(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    cache = redisCache.getData(username+icao)

    if cache is None:
        data = airport.getAirportInfo(icao)
        redisCache.setData(username+icao, json.dumps(data))
        print("Data received from API")

    else:
        print("Data received from cache")
        data = json.loads(cache)

    data['user'] = username
    result = await database.addToFavorites(data)
    if not result: raise HTTPException(400)
    return result


@app.get('/api/v1/data/find-in-favorites/{icao}', tags=['Airport Data'])
async def findInFavorites(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    cache = redisCache.getData(username+icao)
    if cache is None:
        data = await database.findInFavorites(username, icao)

    else:
        data = json.loads(cache)
    
    if not data: raise HTTPException(404)
    return data


@app.get('/api/v1/data/get-all-data', tags=['Airport Data'])
async def getAllData(getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    data = await database.getAllData(username)
    if not data: raise HTTPException(404)
    return data


@app.delete('/api/v1/data/remove-from-favorites/{icao}', tags=['Airport Data'])
async def removeFromFavorites(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    data = await database.removeFromFavorites(username, icao)
    if not data: raise HTTPException(404)
    return data