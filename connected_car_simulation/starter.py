import asyncio
import websockets
import os
import pathlib
from aiohttp import web

ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
gWebsocket = None
i = 0

async def websocket_handler(websocket, path):
    # print('handler started')
    # data = await websocket.recv()
    # reply = f"Data received as:  {data}!"
    # await websocket.send(reply)
    # print('handler finished')
    global gWebsocket
    print('handler started')
    gWebsocket = websocket
    async for message in websocket:
        print(f"Received message: {message}")
        reply = f"Echo: {message}!"
        await websocket.send(reply)
    print('handler stopped')
    gWebsocket = None


async def publisher():
    global i
    while True:
        if gWebsocket is not None:
            output = f"{i}"
            i = i + 1
            print(f"Send: {output}")
            await gWebsocket.send(output)

        print("loop")
        await asyncio.sleep(1)


async def status(request):
    return web.json_response('OK')

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    websocket_coroutine = websockets.serve(websocket_handler, "0.0.0.0", 8081)

    app = web.Application()
    app.router.add_get('/api/status', status)
    app.router.add_static('/static/',
                          path=ROOT_DIR / 'static',
                          name='static')

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    webserver_coroutine = site.start()

    loop.run_until_complete(webserver_coroutine)
    loop.run_until_complete(websocket_coroutine)
    loop.run_until_complete(publisher())
    loop.run_forever()
