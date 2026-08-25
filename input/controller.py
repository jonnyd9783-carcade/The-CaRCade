import pygame
import time

class Controller:
    def __init__(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected. Is the 8BitDo paired and turned on?")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.center_offset = {"axis_1": 0.0, "axis_2": 0.0}
        self.deadzone = {"axis_1": 0.1, "axis_2": 0.1}
        print(f"Connected controller: {self.joystick.get_name()}")

    def calibrate(self, samples=30, delay=0.01, margin=0.03):
        axis_1_samples = []
        axis_2_samples = []
        for i in range(samples):
            pygame.event.pump()
            axis_1_samples.append(self.joystick.get_axis(1))
            axis_2_samples.append(self.joystick.get_axis(2))
            time.sleep(delay)

        avg_1 = sum(axis_1_samples) / samples
        avg_2 = sum(axis_2_samples) / samples
        self.center_offset = {"axis_1": avg_1, "axis_2": avg_2}

        max_dev_1 = max(abs(v - avg_1) for v in axis_1_samples)
        max_dev_2 = max(abs(v - avg_2) for v in axis_2_samples)
        self.deadzone = {"axis_1": max_dev_1 + margin, "axis_2": max_dev_2 + margin}

        print(f"Calibrated center offset: {self.center_offset}")
        print(f"Calibrated deadzone: {self.deadzone}")

    def read_raw(self):
        pygame.event.pump()
        return {
            "axis_1": self.joystick.get_axis(1) - self.center_offset["axis_1"],
            "axis_2": self.joystick.get_axis(2) - self.center_offset["axis_2"],
        }