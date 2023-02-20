from fastapi import APIRouter
from fastapi import Depends, HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from model import userModel, showUserModel
from auth import Hash, Token, oauth2
import database



router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/user/login")

@router.post('/create-user', response_model=showUserModel)
async def createUser(model: userModel):
    hashedPassword = Hash.getHashedPassword(model.password)
    newUser = userModel(username=model.username, email=model.email, password=hashedPassword)
    result = await database.createUser(newUser)
    if not result: raise HTTPException(400)
    return result


@router.get('/get-user/{username}')
async def getUser(username: str):
    result = await database.getUser(username)
    if not result: raise HTTPException(400)
    return result


@router.post('/login')
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




@router.put('/change-password', response_model=showUserModel)
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



@router.delete('/delete-user')
async def deleteUser(username: str, password: str, getCurrentUser: userModel = Depends(oauth2.getCurrentUser)):
    currentUser = await database.getUser(username)
    if not currentUser: raise HTTPException(status_code=404, detail=f"Invalid User")

    if not Hash.verifyPassword(currentUser['password'], password):
        raise HTTPException(status_code=404, detail=f"Invalid Password")

    hashedPassword = Hash.getHashedPassword(password)
    result = await database.deleteUser(username)
    if not result: raise HTTPException(400)

    result = await database.deleteAllData(username)
    if not result: raise HTTPException(400)
    
    return True