
from fastapi import FastAPI,APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Cookie
from fastapi.responses import HTMLResponse

from typing import Union, List, Dict, Optional #, json	#, TypedDict
from pydantic import BaseModel, Field, validator
from datetime import datetime

import json

from dependencies.security import get_current_user, get_websocket_user


router = APIRouter(
    prefix="/skyball",
    tags=["Ball Game"]
    )





class Base(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class Connection(Base):
    #username: str = Field(default=(f"Guest-{str(datetime.now()).replace(' ','_')}")) 
    username: str = Field(default=(f"Guest-{datetime.now()}")) ## - Can't get rid of the space for some reason 
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

    async def sendJSON(self, data: str, sender: "Connection"):
        #print(data, type(data))
        JSON_packet = json.loads(data)
        JSON_packet["sender"] = sender.username
        #JSON_packet = {
        #        "data": data,
        #        "sender":sender.username
        #        }
        try:
            await self.websocket.send_json(JSON_packet)
        except Exception as error:
            print(f"ERROR: Chat Broadcast Faliure. {error}")

    async def terminateSocket(self):
        Manager.connections.remove(self)
        await Manager.broadcast(message=f"{self.username}: Terminating Connection", sender="SERVER")
        #try:
        #    await self.websocket.close()
        #except Exception as error:
        #    print(f"WEBSOCKET TERMINATE ERROR: {error}")
        #Manager.connections.remove(self)
        print(ConnectionManager)       
        #del self


debug_mode:bool = False
print_messages:bool = True

class ConnectionManager(Base):
    connections: List[Connection] = []

    #def connect(self, socket:WebSocket = Depends()):
    #    obj = Connection(websocket=socket)
    #    self.connections.append(obj)
    #    return obj

    @staticmethod
    async def terminate(sender: Connection):
        await sender.terminateSocket()
    
    async def broadcast(self, message:str, sender:str):
        #, connections: List[Connection]):
        if print_messages:
            print(f"MESSAGE: {message}", f"SENDER: {sender}")
        for connection in self.connections:
            if (debug_mode or (connection is not sender)):
                await connection.sendJSON(message, sender)


rooms_list: List["Room"] = []

## - UNIMPLEMENTED
valid_socket_requests = {
##  HEADER : FUNCTION
    "init":None,
    "update":None,
    "error":None
}



class Room(Base):
    connections: List[Connection] = []
    roomID: int
    host: Optional[Connection] = None

    def join(self, connection:Connection):      #roomID = rooms_list[-1]):
        if len(self.connections) >= 2:
            raise Exception("Max 2 players per room, attepted to exceed maximum.")
        
        self.connections.append(connection)
            #rooms_list.append(self)
        

    async def broadcastJSON(self, JSON, sender: Connection):
        for connection in self.connections:
            if print_messages:
                print(connection, sender)
            if (debug_mode or (connection is not sender)):
                await connection.sendJSON(JSON, sender)




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

    print(f"username is: {connection.username}")
    await connection.websocket.accept()
    #Manager.connect(connection.websocket)
    #sender = connection.username
    sender: Connection = connection
    while True:
        try:
            data = await connection.websocket.receive_text()
            await Manager.broadcast(data,sender)
        except WebSocketDisconnect:
            #await Manager.terminate(sender=connection)
            await connection.terminateSocket()
            break
        #print("websocket text recived")
        #await websocket.send_text(f"Message text was: {data}")
