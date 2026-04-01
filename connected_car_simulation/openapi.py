from typing import Any, Dict

from connected_car_simulation.resource_loader import load_json_resource


def create_openapi_spec(server_url: str) -> Dict[str, Any]:
    openapi_spec = load_json_resource("openapi.json")
    openapi_spec["servers"] = [
        {
            "url": server_url,
            "description": "Current simulator instance",
        }
    ]
    return openapi_spec
