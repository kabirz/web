import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketState

from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Kabir聊天室</title>
    </head>
    <body>
        <h1>Kabir聊天室</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8080/ws");

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


# 返回一段 HTML 代码给前端
@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1、ws 连接
    await websocket.accept()
    while websocket.client_state == WebSocketState.CONNECTED:
        # 2、接收客户端发送的内容
        data = await websocket.receive_text()

        # 3、服务端发送内容
        await websocket.send_text(f"小菠萝收到的消息是: {data}")


if __name__ == '__main__':
    uvicorn.run(app, reload=True, host="127.0.0.1", port=8080)
