"""
sensors/simulated_position.py

Simulates a noisy position sensor by reading ground truth from a
VehicleState reference and adding Gaussian noise.

Milestone 5 (Sensor Simulation). Built with an eye toward eventual
replacement: a future UWBPositionSensor would implement the exact same
read() -> SensorReading interface, just pulling from real hardware
instead of corrupting a ground-truth reference. Nothing downstream
(main.py, rendering) should ever need to know or care which one it's
holding.
"""

import random
from dataclasses import dataclass

# Standard deviation of simulated position noise, in the same pixel units
# as VehicleState.x/y. Arbitrary starting guess, not yet tuned — adjust
# and re-run to feel out how much jitter looks/feels right.
POSITION_NOISE_STDDEV = 3.0


@dataclass
class SensorReading:
    x: float = 0.0
    y: float = 0.0


class SimulatedPositionSensor:
    def __init__(self, vehicle_state, noise_stddev=POSITION_NOISE_STDDEV):
        # Holds a reference to ground truth, not a copy — reads the
        # vehicle's current x/y fresh every time .read() is called.
        self.vehicle_state = vehicle_state
        self.noise_stddev = noise_stddev

    def read(self):
        noisy_x = self.vehicle_state.x + random.gauss(0, self.noise_stddev)
        noisy_y = self.vehicle_state.y + random.gauss(0, self.noise_stddev)
        return SensorReading(x=noisy_x, y=noisy_y)