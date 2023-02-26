import motor.motor_asyncio
from model import airportData
from dotenv import load_dotenv
import os


load_dotenv()
MONGODB_CONNECTION_URI = os.getenv('MONGODB_CONNECTION_URI')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_URI) #MongoDB connection URI
database = client.redisfastapi
airportCollection = database.airport
usersCollection = database.users


async def findInFavorites(user, icao):
    data = await airportCollection.find_one({"user":user, "icao":icao},{"_id":0})
    return data

async def getAllData(user):
    data = []
    cursor = airportCollection.find({"user":user})

    async for doc in cursor:
        data.append(airportData(**doc))
    return data

async def deleteAllData(user):
    result = await airportCollection.delete_many({"user":user})
    return result

async def addToFavorites(airportData):
    await airportCollection.insert_one(airportData)
    data = await findInFavorites(airportData["user"], airportData["icao"])
    return data

async def removeFromFavorites(user, icao):
    await airportCollection.delete_one({"user":user, "icao":icao})
    return True



async def createUser(model):
    user = {"username":model.username, "email":model.email, "password":model.password}
    await usersCollection.insert_one(user)
    data = await getUser(user["username"])
    return data

async def getUser(username: str):
    user = await usersCollection.find_one({"username":username},{"_id":0})
    return user

async def getUserByEmail(email: str):
    user = await usersCollection.find_one({"email":email},{"_id":0})
    return user


async def updateUser(currentUsername, updatedUsername=None, updatedPassword=None, updatedEmail=None):
    user = await getUser(currentUsername)
    newUser = {}
    if updatedUsername:
        newUser['username'] = updatedUsername
    else:
        newUser['username'] = user['username']

    if updatedEmail:
        newUser['email'] = updatedEmail
    else:
        newUser['email'] = user['email']

    if updatedPassword:
        newUser['password'] = updatedPassword
    else:
        newUser['password'] = user['password']

    result = await usersCollection.replace_one({"username":currentUsername}, newUser)
    return result


async def deleteUser(username):
    result = await usersCollection.delete_one({"username":username})
    return result