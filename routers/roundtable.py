
from fastapi import FastAPI,APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Cookie
from fastapi.responses import HTMLResponse

from typing import Union, List, Dict, Optional #, json	#, TypedDict
from pydantic import BaseModel, Field, validator
from datetime import datetime


from dependencies.security import get_current_user, get_websocket_user


router = APIRouter(
    prefix="/roundtable",
    tags=["Roundtable"]
    )

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        
        <ul id='messages'>
        </ul>
        
        <script>
            //alert("test1");
            try {
            var ws = new WebSocket("wss://ballcom.xyz/api/roundtable/ws");
            } catch (e) {alert(e)}
            //alert("working");
            ws.onmessage = function(event) {
                //alert("recived");
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };

            ws.onerror = function(event) {alert(error)}; 
           
            ws.onclose = function(event) {alert("Connection closed")};

            function sendMessage(event) {
                event.preventDefault();
                //alert(ws.readyState, ws.url);
                var input = document.getElementById("messageText");
                //alert("test3");
                try {
                    ws.send(input.value);
                } catch (error) {
                    alert(error)
                }
                //alert(`sent, message: ${input.value}`);
                input.value = ''
            }
            
        </script>
    </body>
</html>
"""

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

    async def terminateSocket(self):
        await Manager.broadcast(message=f"{self.username}: Terminating Connection", sender="SERVER")
        try:
            await self.websocket.close()
        except Exception as error:
            print(f"WEBSOCKET TERMINATE ERROR: {error}")
        Manager.connections.remove(self)
        print(ConnectionManager)       
        #del self

class ConnectionManager(Base):
    connections: List[Connection] = []


    #def connect(self, socket:WebSocket = Depends()):
    #    obj = Connection(websocket=socket)
    #    self.connections.append(obj)
    #    return obj
    @staticmethod
    async def terminate(sender: Connection):
        await sender.terminateSocket()
        #, connections: List[Connection]):
    
    async def broadcast(self, message:str, sender:str):
        #, connections: List[Connection]):
        for connection in self.connections:
            print(connection)
            await connection.sendMessage(message, sender)

Manager = ConnectionManager()

@router.get("/chat")
async def get():
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
    print("webtest2")
    sender = connection.username
    while True:
        try:
            data = await connection.websocket.receive_text()
        except WebSocketDisconnect:
            await Manager.terminate(sender=connection)
            break
        #print("websocket text recived")
        #await websocket.send_text(f"Message text was: {data}")
        await Manager.broadcast(data,sender)
