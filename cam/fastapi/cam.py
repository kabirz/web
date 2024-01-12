import cv2
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse

app = FastAPI()

camera_count = 0
cam = None


@app.get('/video')
async def video_feed(request: Request):
    async def get_frame():
        global camera_count, cam
        if camera_count == 0 and cam is None:
            cam = cv2.VideoCapture(0)
        camera_count += 1

        while cam.isOpened():
            success, frame = cam.read()
            frame = cv2.flip(frame, 1)
            if not success:
                cam = None
                camera_count -= 1
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            if await request.is_disconnected():
                cam.release()
                cam = None
                camera_count -= 1
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return StreamingResponse(get_frame(), media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/', response_class=HTMLResponse)
async def index():
    return ''' <!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>摄像头</title>
</head>
<body>
    <h3>摄像头捕获</h3>
    <div>
        <img src=video width="50%" alt="">
    </div>
    <h3>摄像头捕获</h3>
</body>
</html>
    '''


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000)
