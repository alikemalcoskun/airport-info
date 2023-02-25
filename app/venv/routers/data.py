from fastapi import APIRouter, Depends, HTTPException
import json
from model import userModel, showAirportData
import redisCache
import airport
import database
from auth import Hash, Token, oauth2






router = APIRouter(
    prefix="/data",
    tags=["Data"],
    responses={404: {"description": "Not found"}},
)



@router.get('/get-info/{icao}', response_model=showAirportData)
async def getAirportInfo(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    cache = redisCache.getData(username+icao)

    if cache is None:
        data = airport.getAirportInfo(icao, username)
        redisCache.setData(username+icao, data.json())
        print("Data received from API")
        data = json.loads(data.json())
    else:
        print("Data received from cache")
        data = json.loads(cache)

    return data
    

@router.post('/add-to-favorites')
async def addToFavorites(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    cache = redisCache.getData(username+icao)

    if cache is None:
        data = airport.getAirportInfo(icao, username)
        redisCache.setData(username+icao, data.json())
        data = json.loads(data.json())
        print("Data received from API.")

    else:
        print("Data received from cache.")
        data = json.loads(cache)

    result = await database.addToFavorites(data)
    if not result: raise HTTPException(400)
    return result


@router.get('/find-in-favorites/{icao}')
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


@router.get('/get-all-data')
async def getAllData(getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    data = await database.getAllData(username)
    if not data: raise HTTPException(404)
    return data


@router.delete('/remove-from-favorites/{icao}')
async def removeFromFavorites(icao, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    data = await database.removeFromFavorites(username, icao)
    if not data: raise HTTPException(404)
    return data


@router.delete('/remove-all-data')
async def removeFromFavorites(getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    user = await getCurrentUser
    username = user['username']
    data = await database.deleteAllData(username)
    if not data: raise HTTPException(404)
    return True