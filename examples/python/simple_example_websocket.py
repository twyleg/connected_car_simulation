#!/usr/bin/env python
import asyncio
import json
from typing import Any, Dict

import websockets

from simple_example_common import calculate_vehicle_output


WEBSOCKET_URL = "ws://localhost:8081"
POLL_INTERVAL_SECONDS = 0.1


async def send_action(websocket: Any, action: str, **parameters: Any) -> Dict[str, Any]:
    request = {
        "action": action,
        **parameters,
    }
    await websocket.send(json.dumps(request))

    while True:
        message = await websocket.recv()
        payload = json.loads(message)
        if payload.get("type") == "event":
            continue
        return payload


async def main() -> None:
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        while True:
            vehicle_input_response = await send_action(websocket, "get_vehicle_input_adhoc")
            vehicle_input = vehicle_input_response["data"]
            vehicle_output = calculate_vehicle_output(vehicle_input)

            await send_action(
                websocket,
                "set_vehicle_output",
                target_velocity=vehicle_output["target_velocity"],
                acceleration=vehicle_output["acceleration"],
            )
            await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
