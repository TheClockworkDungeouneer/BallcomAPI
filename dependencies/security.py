from sqlmodel import Session
#from fastapi import Depends
from fastapi import Depends, FastAPI, Query, Path, Form, Request, File, UploadFile, Response, HTTPException, WebSocketException, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Union
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

import starlette.status as status
from starlette.status import HTTP_302_FOUND, HTTP_303_SEE_OTHER, HTTP_500_INTERNAL_SERVER_ERROR

#from ..main import engine

import datetime
import json
import os


## ---relative imports---
from dependencies.database import *
##


load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: Union[str, None] = None


def get_session() -> Session:
	with Session(engine) as session:
		yield session
		#return session
		

'''
def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )
'''

async def get_websocket_user(
    #token: Optional[str] = Depends(oauth2_scheme), 
    cookie_token: Optional[str] = Cookie(default=None),
    session: Session = Depends(get_session)
):
    print("testa")
    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason="Could not validate credentials",
        #headers={"WWW-Authenticate": "Bearer"}
	)
    if cookie_token:
        active_token = cookie_token
        print("COOKIE TOKEN: ", active_token)
    else:
        print("No Cookie")
        return f"Guest--{datetime.datetime.now()}"
        #return None 
        
        #raise credentials_exception

    try:
        payload = jwt.decode(
            cookie_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="No username",
                #headers={"WWW-Authenticate": "Bearer"}
                )
        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception
	#user = get_user(fake_users_db, username=token_data.username)
	#user = session.get(User, username=token_data.username)
    
    #print("testb")

    try:
		#session = get_session()
        user = session.exec(select(User).where(User.Username==username)).one()
    except MultipleResultsFound:
        raise WebSocketException(
			code=status.WS_1011_INTERNAL_ERROR,
			reason="Theres only supposed to be one of each username. Tell Max that the database is broken. Booooo I gotta fix it now."
			)
    if user is None:
        raise credentials_exception
    
    print(f"RETURING USER: {user.Username}")
    return user.Username
    


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    cookie_token: Optional[str] = Cookie(default=None),
    session: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
	)
    #print("cool stuff")
    if token:
        active_token = token
    elif cookie_token:
        active_token = cookie_token
        print("COOKIE TOKEN: ", active_token)
    else:
        raise credentials_exception

    try:
        		

        payload = jwt.decode(active_token, SECRET_KEY, algorithms=[ALGORITHM])
		##print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No username",
                headers={"WWW-Authenticate": "Bearer"}
                )
        token_data = TokenData(username=username)
    
    except JWTError:
        raise credentials_exception
	#user = get_user(fake_users_db, username=token_data.username)
	#user = session.get(User, username=token_data.username)
    try:
		#session = get_session()
        user = session.exec(select(User).where(User.Username==username)).one()
    except MultipleResultsFound:
        raise HTTPException(
			status_code=500,
			detail="Theres only supposed to be one of each username. Tell Max that the database is broken. Booooo I gotta fix it now."
			)
    if user is None:
        raise credentials_exception
    return user
    '''
	user = session.get(User, fake_decode_token(token))
	if not user.enabled:
		raise HTTPException(status_code=400, detail="Inactive user")
		return user
    '''

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

#def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends(), session:Session = Depends(get_session)):
	#print("test3")
	#user = session.get(User, username)
	#, session:Session = Depends(get_session)
	try:
		#session = get_session()
		user = session.exec(select(User).where(User.Username==form_data.username)).one()
	except MultipleResultsFound:
		raise HTTPException(
			status_code=500,
			detail="Theres only supposed to be one of each username. Tell Max that the database is broken. Booooo I gotta fix it now."
			)
	except NoResultFound:
		raise HTTPException(
			status_code=401,
			detail=f"Username \"{form_data.username}\" was not found."	
			)
	#print("test6", user)
	if not user:
		#print("test7")
		#return False
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	if not verify_password(form_data.password, user.Hashed_Password):
		##print("passwrong")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	#print("test5")
	return user

def create_access_token(data: dict, expires_delta: Union[datetime.timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=DEFAULT_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def site_dict(num_cards:int):
	try:
		with open(json_path("sites.json"), "r") as raw_file:
			#print(type(json.load(raw_file)))
			cooked_file = json.load(raw_file)
			#print(type(raw_file))
			#print(type(json.load(raw_file)))
			#cooked_file = Response(json.load(raw_file))
			return (cooked_file)
	except json.JSONDecodeError:
		raise HTTPException(status_code=404, detail="JSON file empty")

