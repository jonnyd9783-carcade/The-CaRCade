from dataclasses import dataclass

@dataclass
class NormalizedCommand:
    steering: float = 0.0
    throttle: float = 0.0
    brake: float = 0.0


def map_controller_input(raw: dict) -> NormalizedCommand:
    result = NormalizedCommand(
        steering=raw["axis_2"],
        throttle=raw["axis_1"],
    )
    return result


def map_keyboard_input(raw: dict) -> NormalizedCommand:
    result = NormalizedCommand(
        steering=raw["steering"],
        throttle=raw["throttle"],
    )
    return result