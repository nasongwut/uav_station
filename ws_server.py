from typing import List
import json,base64,struct

# import  struct

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # print(message)
        for connection in self.active_connections:
            await connection.send_text(message)


station_manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await station_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            dictmsg = json.loads(data)
            payload = dictmsg['bin']
            packet = base64.b64decode(payload)
            unpack_st = struct.unpack('iiiiiiiiiii',packet)
            json_web = {"src":unpack_st[0],
                "dst":unpack_st[1],
                "seq":unpack_st[2],
                "cmd":unpack_st[3],
                "sta":unpack_st[4],
                "motor_x":unpack_st[5],
                "motor_y":unpack_st[6],
                "sta_volt":unpack_st[7],
                "sta_amp":unpack_st[8],
                "uav_volt":unpack_st[9],
                "uav_amp":unpack_st[10]}

            # print(json_web)

            await station_manager.broadcast(json.dumps(json_web))
    except WebSocketDisconnect:
        station_manager.disconnect(websocket)
        
        # await manager.broadcast(f"Client #{client_id} left the chat")