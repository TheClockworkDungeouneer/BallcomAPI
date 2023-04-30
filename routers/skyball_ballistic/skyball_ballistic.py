
from fastapi import FastAPI,APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Cookie
from fastapi.responses import HTMLResponse

from typing import Union, List, Dict, Optional #, json	#, TypedDict
from pydantic import BaseModel, Field, validator
from datetime import datetime


from dependencies.security import get_current_user, get_websocket_user


router = APIRouter(
    prefix="/skyball",
    tags=["Ball Game"]
    )





class Base(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class Connection(Base):
    username: str = Field(default=(f"Guest-{datetime.now()}")) 
    websocket: WebSocket

    @validator("username", pre=True)
    def guest_default(cls, v):
        if v is None:
            return f"Guest--{datetime.now()}"
        return v

    def __init__(self, websocket: WebSocket,
            username:Optional[str]=Depends(get_websocket_user)):
        print(f"egg {username}")
        #print(f"BANG: {username}")
        super().__init__(username=username, websocket=websocket)
        #print(self.username) 
        Manager.connections.append(self)

    async def sendMessage(self, message, sender):
        try:
            await self.websocket.send_text(f"{sender}: {message}")
        except Exception as error:
            print(f"ERROR: Chat Broadcast Faliure. {error}")

    async def terminateSocket():
        Manager.broadcast(message=f"{self.username}: Terminating Connection")
        try:
            await websocket.close()
        except Exception as error:
            print(f"WEBSOCKET TERMINATE ERROR: {error}")
        ConnectionManager.connections.remove(self)
        print(ConnectionManager)       
        del self

class ConnectionManager(Base):
    connections: List[Connection] = []


    #def connect(self, socket:WebSocket = Depends()):
    #    obj = Connection(websocket=socket)
    #    self.connections.append(obj)
    #    return obj

    def terminate(self):
        pass
        #, connections: List[Connection]):
    
    async def broadcast(self, message:str, sender:str):
        #, connections: List[Connection]):
        for connection in self.connections:
            print(connection)
            await connection.sendMessage(message, sender)

Manager = ConnectionManager()

@router.get("/chat")
async def get():
    with open("routers/skyball_ballistic/skyball_ballistic.html", "r") as file:
        html = file.read()
    
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(
    *, 
    #cookie_token:Optional[str] = Cookie(default=None),
    #connection: Depends(lambda:Connection(username=username)) 
    connection: Connection = Depends()
):
    #print(username)
    #connection:Connection = Connection(username=username)
    print(f"username is: {connection.username}")
    await connection.websocket.accept()
    #Manager.connect(connection.websocket)
    sender = connection.username
    while True:
        try:
            data = await connection.websocket.receive_text()
        except WebSocketDisconnect:
             
            break
        #print("websocket text recived")
        #await websocket.send_text(f"Message text was: {data}")
        await Manager.broadcast(data,sender)
