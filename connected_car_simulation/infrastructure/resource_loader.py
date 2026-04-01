import json
from pathlib import Path
from typing import Any


FILE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = FILE_DIR.parent / "resources"


def get_resource_path(*path_parts: str) -> Path:
    return RESOURCES_DIR.joinpath(*path_parts)


def load_json_resource(*path_parts: str) -> Any:
    resource_path = get_resource_path(*path_parts)
    with resource_path.open(encoding="utf-8") as resource_file:
        return json.load(resource_file)


def load_text_resource(*path_parts: str) -> str:
    resource_path = get_resource_path(*path_parts)
    return resource_path.read_text(encoding="utf-8")
