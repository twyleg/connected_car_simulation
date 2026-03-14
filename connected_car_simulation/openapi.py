def create_openapi_spec(server_url: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Connected Car Simulation API",
            "version": "1.0.0",
            "description": (
                "HTTP API for controlling and inspecting the connected car simulation. "
                "The simulator UI uses these endpoints to drive the vehicle model and "
                "to retrieve route and traffic-light data."
            ),
        },
        "servers": [
            {
                "url": server_url,
                "description": "Current simulator instance",
            }
        ],
        "paths": {
            "/api/set_vehicle_output": {
                "get": {
                    "summary": "Set target vehicle output",
                    "description": "Updates the vehicle acceleration limit and target velocity.",
                    "parameters": [
                        {
                            "name": "acceleration",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "number", "format": "float"},
                            "description": "Requested acceleration in m/s².",
                        },
                        {
                            "name": "target_velocity",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "number", "format": "float"},
                            "description": "Requested target velocity in km/h.",
                        },
                    ],
                    "responses": {
                        "200": {"description": "Vehicle output accepted."}
                    },
                }
            },
            "/api/set_vehicle_position": {
                "get": {
                    "summary": "Set vehicle route position",
                    "description": "Moves the vehicle to a specific position along the route.",
                    "parameters": [
                        {
                            "name": "position",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "number", "format": "float"},
                            "description": "Route position in meters.",
                        }
                    ],
                    "responses": {
                        "200": {"description": "Vehicle position updated."}
                    },
                }
            },
            "/api/get_simulation_state": {
                "get": {
                    "summary": "Get full simulation state",
                    "responses": {
                        "200": {
                            "description": "Current simulation state.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SimulationState"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/get_route_information": {
                "get": {
                    "summary": "Get route metadata",
                    "responses": {
                        "200": {
                            "description": "Current route information.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/RouteInformation"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/get_vehicle_input_adhoc": {
                "get": {
                    "summary": "Get infrastructure data within radio range",
                    "responses": {
                        "200": {
                            "description": "Vehicle input limited to traffic lights within radio range.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/VehicleInput"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/get_vehicle_input_infrastructure": {
                "get": {
                    "summary": "Get full infrastructure input",
                    "responses": {
                        "200": {
                            "description": "Vehicle input with all traffic lights from the scenario.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/VehicleInput"}
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "Coordinates": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "format": "double"},
                        "lon": {"type": "number", "format": "double"},
                    },
                    "required": ["lat", "lon"],
                },
                "SimulationVehicleState": {
                    "type": "object",
                    "properties": {
                        "max_acceleration": {"type": "number", "format": "float"},
                        "target_velocity": {"type": "number", "format": "float", "description": "m/s"},
                        "current_velocity": {"type": "number", "format": "float", "description": "m/s"},
                        "position_coordinates": {"$ref": "#/components/schemas/Coordinates"},
                        "position_on_route": {"type": "number", "format": "float"},
                    },
                    "required": [
                        "max_acceleration",
                        "target_velocity",
                        "current_velocity",
                        "position_coordinates",
                        "position_on_route",
                    ],
                },
                "VehicleInputState": {
                    "type": "object",
                    "properties": {
                        "current_velocity": {"type": "number", "format": "float", "description": "km/h"},
                        "max_acceleration": {"type": "number", "format": "float"},
                        "position_on_route": {"type": "number", "format": "float"},
                    },
                    "required": ["current_velocity", "max_acceleration", "position_on_route"],
                },
                "TrafficLightState": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "position_on_track": {"type": "number", "format": "float"},
                        "lon": {"type": "number", "format": "double"},
                        "lat": {"type": "number", "format": "double"},
                        "period": {"type": "number", "format": "float"},
                        "ratio": {"type": "number", "format": "float"},
                        "state": {"type": "string", "enum": ["red", "yellow", "green"]},
                        "offset": {"type": "integer"},
                        "t": {"type": "number", "format": "float"},
                    },
                    "required": ["id", "position_on_track", "lon", "lat", "period", "ratio", "state", "offset", "t"],
                },
                "TrafficLightOutput": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "position_on_route": {"type": "number", "format": "float"},
                        "state": {"type": "string", "enum": ["red", "yellow", "green"]},
                        "period": {"type": "number", "format": "float"},
                        "ratio": {"type": "number", "format": "float"},
                        "t": {"type": "number", "format": "float"},
                    },
                    "required": ["id", "position_on_route", "state", "period", "ratio", "t"],
                },
                "SimulationState": {
                    "type": "object",
                    "properties": {
                        "vehicle_state": {"$ref": "#/components/schemas/SimulationVehicleState"},
                        "traffic_lights_state": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/TrafficLightState"},
                        },
                    },
                    "required": ["vehicle_state", "traffic_lights_state"],
                },
                "RouteInformation": {
                    "type": "object",
                    "properties": {
                        "length": {"type": "integer"},
                        "start": {"$ref": "#/components/schemas/Coordinates"},
                        "end": {"$ref": "#/components/schemas/Coordinates"},
                    },
                    "required": ["length", "start", "end"],
                },
                "MapData": {
                    "type": "object",
                    "properties": {
                        "speed_limit": {"type": "integer"},
                    },
                    "required": ["speed_limit"],
                },
                "VehicleInput": {
                    "type": "object",
                    "properties": {
                        "vehicle_state": {"$ref": "#/components/schemas/VehicleInputState"},
                        "map": {"$ref": "#/components/schemas/MapData"},
                        "traffic_lights": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/TrafficLightOutput"},
                        },
                    },
                    "required": ["vehicle_state", "map", "traffic_lights"],
                },
            }
        },
    }
