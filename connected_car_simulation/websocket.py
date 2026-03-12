import json
import websockets
from typing import Any, Dict, Optional


class Websocket:

    def __init__(self, hostname: str, port: int):
        self.hostname = hostname
        self.port = port
        self.server = None
        self.websocket: Optional[Any] = None

    async def start(self) -> None:
        self.server = await websockets.serve(self.websocket_handler, self.hostname, self.port)

    async def stop(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    async def websocket_handler(self, websocket: Any) -> None:
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
