from dataclasses import dataclass

@dataclass
class VehicleState:
    x: float = 400.0
    y: float = 300.0
    heading: float = 0.0
    current_steering: float = 0.0
    current_throttle: float = 0.0

    def apply_input(self, steering: float, throttle: float, speed: float = 2.5, deadzone: float = 0.08, ramp_rate: float = 0.15):
        if abs(steering) < deadzone:
            steering = 0.0
        if abs(throttle) < deadzone:
            throttle = 0.0

        self.current_steering += (steering - self.current_steering) * ramp_rate
        self.current_throttle += (throttle - self.current_throttle) * ramp_rate

        s = self.current_steering
        t = self.current_throttle
        s = (s ** 2) * (1 if s >= 0 else -1)
        t = (t ** 2) * (1 if t >= 0 else -1)

        self.x += s * speed
        self.y += t * speed