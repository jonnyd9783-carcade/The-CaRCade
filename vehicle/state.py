from dataclasses import dataclass
import math

@dataclass
class VehicleState:
    x: float = 400.0
    y: float = 300.0
    heading: float = 0.0
    current_steering: float = 0.0
    current_throttle: float = 0.0

    def apply_input(self, steering, throttle, speed=2.5, steering_deadzone=0.12, throttle_deadzone=0.12, ramp_rate=0.15, turn_rate=3.0):
        if abs(steering) < steering_deadzone:
            steering = 0.0
        if abs(throttle) < throttle_deadzone:
            throttle = 0.0

        self.current_steering += (steering - self.current_steering) * ramp_rate
        self.current_throttle += (throttle - self.current_throttle) * ramp_rate

        s = self.current_steering
        t = self.current_throttle
        s = (s ** 2) * (1 if s >= 0 else -1)
        t = (t ** 2) * (1 if t >= 0 else -1)

        self.heading += s * turn_rate

        heading_rad = math.radians(self.heading)
        self.x -= math.sin(heading_rad) * t * speed
        self.y += math.cos(heading_rad) * t * speed