from dataclasses import dataclass

@dataclass
class VehicleState:
    x: float = 400.0
    y: float = 300.0
    heading: float = 0.0

    def apply_input(self, steering: float, throttle: float, speed: float = 2.5, deadzone: float = 0.08):
        if abs(steering) < deadzone:
            steering = 0.0
        if abs(throttle) < deadzone:
            throttle = 0.0

        # squares the input (preserving sign) so small stick pushes move
        # a little, and only a full push gives full speed - much smoother
        # than direct 1:1 response
        steering = (steering ** 2) * (1 if steering >= 0 else -1)
        throttle = (throttle ** 2) * (1 if throttle >= 0 else -1)

        self.x += steering * speed
        self.y += throttle * speed