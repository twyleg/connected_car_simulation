import asyncio
import signal
import xml.etree.ElementTree as ET
from contextlib import suppress

from simulation_environment import SimulationEnvironment
from websocket import Websocket
from webserver import WebServer
from typing import Dict


async def simulation_updater_and_publisher(simulation_environment: SimulationEnvironment, websocket: Websocket):
    while True:
        simulation_environment.update()
        simulation_state = simulation_environment.get_simulation_state()
        await websocket.publish_simulation_state(simulation_state)
        await asyncio.sleep(0.1)


def read_config(config_file_path: str) -> Dict:
    tree = ET.parse(config_file_path)
    return tree.getroot()


async def main() -> None:
    config = read_config('config.xml')

    simulation_environment = SimulationEnvironment(route_file_path='static/routes/ostfalia-wf-wob.gpx',
                                                   config=config)
    simulation_environment.vehicle.acceleration = 0.0
    simulation_environment.vehicle.set_target_velocity_in_kmh(0.0)

    websocket = Websocket('0.0.0.0', 8081)
    await websocket.start()

    webserver = WebServer(simulation_environment, '0.0.0.0', 8080)
    await webserver.start()

    print('Connected Car Simulation started!')
    print('Open http://localhost:8080/static/index.html in your browser.')

    updater_task = asyncio.create_task(
        simulation_updater_and_publisher(simulation_environment, websocket)
    )
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    try:
        await stop_event.wait()
    finally:
        updater_task.cancel()
        with suppress(asyncio.CancelledError):
            await updater_task
        await websocket.stop()
        await webserver.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
