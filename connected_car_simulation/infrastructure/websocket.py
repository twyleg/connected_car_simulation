import json
import logging
from typing import Any, Dict, Optional

import websockets

from connected_car_simulation.simulation.simulation_api import (
    InvalidSimulationRequestError,
    SimulationApi,
    UnknownSimulationActionError,
)
from connected_car_simulation.simulation.simulation_environment import SimulationEnvironment


logger = logging.getLogger(__name__)


class Websocket:

    def __init__(self, simulation_environment: SimulationEnvironment, hostname: str, port: int):
        self.simulation_environment = simulation_environment
        self.api = SimulationApi(simulation_environment)
        self.hostname = hostname
        self.port = port
        self.server = None
        self.websocket: Optional[Any] = None

    async def start(self) -> None:
        self.server = await websockets.serve(self.websocket_handler, self.hostname, self.port)
        logger.info("WebSocket server listening on ws://%s:%s", self.hostname, self.port)

    async def stop(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        logger.info("WebSocket server stopped")

    async def websocket_handler(self, websocket: Any) -> None:
        logger.info("WebSocket client connected")
        self.websocket = websocket
        async for message in websocket:
            logger.debug("Received WebSocket message: %s", message)
            await websocket.send(self.handle_message(message))
        logger.info("WebSocket client disconnected")
        self.websocket = None

    def handle_message(self, message: str) -> str:
        try:
            request = json.loads(message)
        except json.JSONDecodeError:
            return self.create_error_response("Messages must contain valid JSON.")

        action = request.get("action")
        if not action:
            return self.create_error_response("Missing required field 'action'.")

        try:
            response_data = self.api.invoke_action(action, request)
        except (UnknownSimulationActionError, InvalidSimulationRequestError) as exc:
            return self.create_error_response(str(exc), action=action)

        response = {
            "type": "response",
            "action": action,
            "data": response_data,
        }
        return json.dumps(response)

    def create_error_response(self, error_message: str, action: Optional[str] = None) -> str:
        response = {
            "type": "error",
            "error": error_message,
        }
        if action is not None:
            response["action"] = action
        return json.dumps(response)

    async def publish_simulation_state(self, simulation_state: Dict) -> None:
        if self.websocket is not None:
            obj = {
                "type": "event",
                "event": "simulation_state",
                "simulation_state": simulation_state
            }
            json_dump = json.dumps(obj)
            await self.websocket.send(json_dump)
