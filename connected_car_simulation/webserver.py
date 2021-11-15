import asyncio
import pathlib
import os
import json
from simulation_environment import SimulationEnvironment
from aiohttp import web, web_response, web_request


ROOT_DIR = pathlib.Path(os.getcwd())


class WebServer:

    def __init__(self, simulation_environment: SimulationEnvironment, hostname: str, port: int) -> None:
        self.simulation_environment = simulation_environment
        self.app = web.Application()
        self.app.router.add_get('/api/set_vehicle_output', self.set_vehicle_output_handler)
        self.app.router.add_get('/api/set_vehicle_position', self.set_vehicle_position_handler)
        self.app.router.add_get('/api/get_simulation_state', self.get_simulation_state_handler)
        self.app.router.add_get('/api/get_route_information', self.get_route_information_handler)
        self.app.router.add_get('/api/get_vehicle_input_adhoc', self.get_vehicle_input_adhoc_handler)
        self.app.router.add_get('/api/get_vehicle_input_infrastructure', self.get_vehicle_input_infrastructure_handler)
        self.app.router.add_static('/static/',
                              path=ROOT_DIR / 'static',
                              name='static')

        runner = web.AppRunner(self.app)
        asyncio.get_event_loop().run_until_complete(runner.setup())
        site = web.TCPSite(runner, hostname, port)
        self.webserver_coroutine = site.start()

    def start(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.webserver_coroutine)

    async def set_vehicle_output_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        self.simulation_environment.vehicle.set_acceleration(float(request.query['acceleration']))
        self.simulation_environment.vehicle.set_target_velocity_in_kmh(float(request.query['target_velocity']))
        return web.Response(status=200)

    async def set_vehicle_position_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        self.simulation_environment.set_vehicle_position(float(request.query['position']))
        return web.Response(status=200)

    async def get_simulation_state_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        obj = self.simulation_environment.get_simulation_state()
        output = json.dumps(obj, indent=4)
        return web.json_response(status=200, body=output)

    async def get_route_information_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        obj = self.simulation_environment.get_route_information()
        output = json.dumps(obj, indent=4)
        return web.json_response(status=200, body=output)

    async def get_vehicle_input_adhoc_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        obj = self.simulation_environment.get_vehicle_input_adhoc()
        output = json.dumps(obj, indent=4)
        return web.json_response(status=200, body=output)

    async def get_vehicle_input_infrastructure_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        obj = self.simulation_environment.get_vehicle_input_infrastructure()
        output = json.dumps(obj, indent=4)
        return web.json_response(status=200, body=output)
