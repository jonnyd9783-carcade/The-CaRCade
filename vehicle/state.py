from dataclasses import dataclass

@dataclass
class VehicleState:
    x: float = 400.0       # starting position, center-ish of the arena
    y: float = 300.0
    heading: float = 0.0    # facing direction, in degrees