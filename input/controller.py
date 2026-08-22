import pygame
import time

class Controller:
    def __init__(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected. Is the 8BitDo paired and turned on?")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.center_offset = {"axis_0": 0.0, "axis_1": 0.0}
        print(f"Connected controller: {self.joystick.get_name()}")

    def calibrate(self, samples=30, delay=0.01):
        totals = {"axis_0": 0.0, "axis_1": 0.0}
        for _ in range(samples):
            pygame.event.pump()
            totals["axis_0"] += self.joystick.get_axis(0)
            totals["axis_1"] += self.joystick.get_axis(1)
            time.sleep(delay)

        self.center_offset = {
            "axis_0": totals["axis_0"] / samples,
            "axis_1": totals["axis_1"] / samples,
        }
        print(f"Calibrated center offset: {self.center_offset}")

    def read_raw(self):
        pygame.event.pump()
        return {
            "axis_0": self.joystick.get_axis(0) - self.center_offset["axis_0"],
            "axis_1": self.joystick.get_axis(1) - self.center_offset["axis_1"],
        }