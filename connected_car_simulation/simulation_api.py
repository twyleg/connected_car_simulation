from typing import Any, Callable, Dict

from connected_car_simulation.simulation_environment import SimulationEnvironment


class SimulationApiError(Exception):
    pass


class UnknownSimulationActionError(SimulationApiError):
    pass


class InvalidSimulationRequestError(SimulationApiError):
    pass


class SimulationApi:

    def __init__(self, simulation_environment: SimulationEnvironment) -> None:
        self.simulation_environment = simulation_environment
        self.action_handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "get_simulation_state": lambda _: self.get_simulation_state(),
            "get_route_information": lambda _: self.get_route_information(),
            "get_vehicle_input_adhoc": lambda _: self.get_vehicle_input_adhoc(),
            "get_vehicle_input_infrastructure": lambda _: self.get_vehicle_input_infrastructure(),
            "set_vehicle_output": self.handle_set_vehicle_output_action,
            "set_vehicle_position": self.handle_set_vehicle_position_action,
        }
        self.required_action_parameters: Dict[str, set[str]] = {
            "get_simulation_state": set(),
            "get_route_information": set(),
            "get_vehicle_input_adhoc": set(),
            "get_vehicle_input_infrastructure": set(),
            "set_vehicle_output": {"target_velocity", "acceleration"},
            "set_vehicle_position": {"position"},
        }

    def has_action(self, action: str) -> bool:
        return action in self.action_handlers

    def invoke_action(self, action: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.has_action(action):
            raise UnknownSimulationActionError(f"Unsupported action '{action}'.")

        missing_parameters = sorted(self.required_action_parameters[action] - set(request_data.keys()))
        if missing_parameters:
            missing_parameters_output = ", ".join(missing_parameters)
            raise InvalidSimulationRequestError(f"Missing required parameter(s): {missing_parameters_output}.")

        try:
            return self.action_handlers[action](request_data)
        except (TypeError, ValueError) as exc:
            raise InvalidSimulationRequestError(str(exc)) from exc

    def get_simulation_state(self) -> Dict[str, Any]:
        return self.simulation_environment.get_simulation_state()

    def get_route_information(self) -> Dict[str, Any]:
        return self.simulation_environment.get_route_information()

    def get_vehicle_input_adhoc(self) -> Dict[str, Any]:
        return self.simulation_environment.get_vehicle_input_adhoc()

    def get_vehicle_input_infrastructure(self) -> Dict[str, Any]:
        return self.simulation_environment.get_vehicle_input_infrastructure()

    def set_vehicle_output(self, target_velocity: float, acceleration: float) -> Dict[str, Any]:
        self.simulation_environment.vehicle.set_acceleration(acceleration)
        self.simulation_environment.vehicle.set_target_velocity_in_kmh(target_velocity)
        return {"status": "ok"}

    def set_vehicle_position(self, position: float) -> Dict[str, Any]:
        self.simulation_environment.set_vehicle_position(position)
        return {"status": "ok"}

    def handle_set_vehicle_output_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self.set_vehicle_output(
            target_velocity=float(request["target_velocity"]),
            acceleration=float(request["acceleration"]),
        )

    def handle_set_vehicle_position_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self.set_vehicle_position(float(request["position"]))
