from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
jinja = Jinja2Templates(directory="templates")
names = {"小菠萝", "小猫咪", "小狗狗", "小鱼儿", "小兔子"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket: str] = dict()

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[websocket] = client_id

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket)

    async def broadcast(self, message: str, client_id: str):
        for connection, id in self.active_connections.items():
            if len(message) == 0:
                data = f"{client_id} 离开了聊天室"
            elif id == client_id:
                data = "我说的是: " + message
            else:
                data = f"{id} 说: {message}"
            await connection.send_text(data)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return jinja.TemplateResponse("chat.html", {"request": request, "client_id": names.pop()})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, client_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("", client_id)
        names.add(client_id)
