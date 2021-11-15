import json
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Optional, Dict


class Websocket:

    def __init__(self, hostname: str, port: int):
        self.websocket_coroutine = websockets.serve(self.websocket_handler, hostname, port)
        self.websocket: Optional[WebSocketServerProtocol] = None

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.websocket_coroutine)

    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        print('Websocket connected!')
        self.websocket = websocket
        async for message in websocket:
            print(f"Received message: {message}")
            reply = f"Echo: {message}!"
            await websocket.send(reply)
        print('Websocket disconnected!')
        self.websocket = None

    async def publish_simulation_state(self, simulation_state: Dict) -> None:
        if self.websocket is not None:
            obj = {
                "simulation_state": simulation_state
            }
            json_dump = json.dumps(obj)
            await self.websocket.send(json_dump)

