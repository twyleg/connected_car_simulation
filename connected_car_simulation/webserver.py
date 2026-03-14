import json
from pathlib import Path
from aiohttp import web, web_response, web_request

from connected_car_simulation.openapi import create_openapi_spec
from connected_car_simulation.simulation_environment import SimulationEnvironment
from connected_car_simulation.resource_path import get_resource_path


FILE_DIR = Path(__file__).parent


class WebServer:

    def __init__(self, simulation_environment: SimulationEnvironment, hostname: str, port: int) -> None:
        self.simulation_environment = simulation_environment
        self.hostname = hostname
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/api/set_vehicle_output', self.set_vehicle_output_handler)
        self.app.router.add_get('/api/set_vehicle_position', self.set_vehicle_position_handler)
        self.app.router.add_get('/api/get_simulation_state', self.get_simulation_state_handler)
        self.app.router.add_get('/api/get_route_information', self.get_route_information_handler)
        self.app.router.add_get('/api/get_vehicle_input_adhoc', self.get_vehicle_input_adhoc_handler)
        self.app.router.add_get('/api/get_vehicle_input_infrastructure', self.get_vehicle_input_infrastructure_handler)
        self.app.router.add_get('/api/openapi.json', self.openapi_handler)
        self.app.router.add_get('/api/docs', self.swagger_ui_handler)
        self.app.router.add_static('/static/',
                              path=FILE_DIR / 'resources/ui/',
                              name='static')
        self.runner = web.AppRunner(self.app)
        self.site = None

    async def start(self) -> None:
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.hostname, self.port)
        await self.site.start()

    async def stop(self) -> None:
        await self.runner.cleanup()
        self.site = None

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

    async def openapi_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        server_url = f"{request.scheme}://{request.host}"
        return web.json_response(create_openapi_spec(server_url))

    async def swagger_ui_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Connected Car Simulation API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>
    body { margin: 0; background: #08111f; }
    .topbar { display: none; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function() {
      window.ui = SwaggerUIBundle({
        url: '/api/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
      });
    };
  </script>
</body>
</html>
"""
        return web.Response(text=html, content_type='text/html')
