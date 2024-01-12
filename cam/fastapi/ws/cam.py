import websockets
import asyncio
import numpy as np
import multiprocessing as mp
import time
import cv2

frame = None


def websocket_process(img_dict):
    async def main_logic(websocket):
        await recv_msg(websocket, img_dict)

    async def main():
        async with websockets.serve(main_logic, "localhost", 5678):
            await asyncio.Future()

    asyncio.run(main())


async def recv_msg(websocket, img_dict):
    recv_text = await websocket.recv()
    if recv_text == 'begin':
        while True:
            frame = img_dict['img']
            if isinstance(frame, np.ndarray):
                enconde_data = cv2.imencode('.png', frame)[1]
                enconde_str = enconde_data.tostring()
                try:
                    await websocket.send(enconde_str)
                    time.sleep(0.07)
                except Exception as e:
                    print(e)
                    return True


def image_put(q, id):
    cap = cv2.VideoCapture(id)
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, None, fx=0.7, fy=0.7)
            q.put(frame)
            q.get() if q.full() else ...


def image_get(q, img_dict):
    while True:
        frame = q.get()
        if isinstance(frame, np.ndarray):
            img_dict['img'] = frame


def run_single_camera(id):
    mp.set_start_method(method='spawn')
    queue = mp.Queue(maxsize=3)
    m = mp.Manager()
    img_dict = m.dict()
    Processes = [mp.Process(target=image_put, args=(queue, id)),
                 mp.Process(target=image_get, args=(queue, img_dict)),
                 mp.Process(target=websocket_process, args=(img_dict,))]

    [process.start() for process in Processes]
    [process.join() for process in Processes]


def run():
    run_single_camera(0)


if __name__ == '__main__':
    run()
