# Connected Car Simulation

Connected Car Simulation is a Python-based simulator for experimenting with vehicle movement, route-following, and traffic-light interaction. It ships with:

- a live OpenLayers web UI
- a WebSocket stream for realtime simulation updates
- an HTTP API for controlling the simulation and reading state
- Swagger-based API documentation

![Traffic light states](doc/images/web_application_screenshot.png)

## Features

- Realtime vehicle simulation on a GPX-based route
- Configurable traffic-light timings and vehicle parameters
- Browser UI for map visualization and simulation control
- HTTP endpoints for control and inspection
- OpenAPI/Swagger documentation at `/api/docs`
- PyInstaller build support

## Project Layout

```text
connected_car_simulation/
├── connected_car_simulation/
│   ├── main.py
│   ├── simulation_environment.py
│   ├── webserver.py
│   ├── websocket.py
│   └── resources/
│       ├── config.xml
│       └── ui/
├── resources/
│   └── images/
├── examples/
├── pyinstaller.spec
└── tox.ini
```

## Requirements

- Python 3.9+
- A virtual environment is recommended

## Development Setup

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Simulator

Start the application with:

```bash
python -m connected_car_simulation
```

Once started, open:

- UI: `http://localhost:8080/static/index.html`
- Swagger docs: `http://localhost:8080/api/docs`

The simulator also exposes a WebSocket endpoint on:

- `ws://localhost:8081`

## HTTP API

The simulator provides these main HTTP endpoints:

- `GET /api/set_vehicle_output`
- `GET /api/set_vehicle_position`
- `GET /api/get_simulation_state`
- `GET /api/get_route_information`
- `GET /api/get_vehicle_input_adhoc`
- `GET /api/get_vehicle_input_infrastructure`
- `GET /api/openapi.json`
- `GET /api/docs`

For parameter and schema details, use the Swagger UI.

## Configuration

The simulator reads its runtime configuration from:

- [`connected_car_simulation/resources/config.xml`](connected_car_simulation/resources/config.xml)

This file controls vehicle parameters, speed limits, and traffic-light definitions.

## Packaging with PyInstaller

Build the standalone executable with:

```bash
tox -e pyinstaller
```

The PyInstaller spec bundles:

- `connected_car_simulation/resources/config.xml`
- the web UI assets
- example files

## Notes

- In PyInstaller `--onefile` mode, bundled resources are extracted into a temporary `_MEI...` directory at startup.
- The project resolves bundled resource paths at runtime so the same code works in development and in the packaged executable.

## License

GPL 3.0
