import json
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from gpxpy.gpx import GPXTrackPoint
from typing import Optional


class Websocket:

    def __init__(self, hostname: str, port: int):
        self.websocket_coroutine = websockets.serve(self.websocket_handler, hostname, port)
        self.websocket: Optional[WebSocketServerProtocol] = None

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.websocket_coroutine)

    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        print('handler started')
        self.websocket = websocket
        async for message in websocket:
            print(f"Received message: {message}")
            reply = f"Echo: {message}!"
            await websocket.send(reply)
        print('handler stopped')
        self.websocket = None

    async def publish_position(self, position: GPXTrackPoint) -> None:
        if self.websocket is not None:
            pt = {
                "lon": position.longitude,
                "lat": position.latitude,
            }
            await self.websocket.send(json.dumps(pt))
