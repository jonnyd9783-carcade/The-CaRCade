from dataclasses import dataclass

@dataclass
class NormalizedCommand:
    steering: float = 0.0   # -1.0 (full left) to 1.0 (full right)
    throttle: float = 0.0   # -1.0 to 1.0
    brake: float = 0.0      # 0.0 to 1.0


def map_controller_input(raw: dict) -> NormalizedCommand:
    """Converts a Controller's raw axis dict into a NormalizedCommand.
    This is the only function that needs to know controller axis numbers."""
    return NormalizedCommand(
        steering=raw["axis_0"],
        throttle=raw["axis_1"],
    )