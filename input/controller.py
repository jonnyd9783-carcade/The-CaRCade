# Reads the physical 8BitDo controller via pygame's joystick module
# and produces raw axis/button values. This is the only file that
# should know pygame's joystick API exists.

import pygame

class Controller:
    def __init__(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected. Is the 8BitDo paired and turned on?")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"Connected controller: {self.joystick.get_name()}")

    def read_raw(self):
        """Returns raw axis values as a dict. We'll figure out exact
        axis numbers for the 8BitDo in the next step."""
        pygame.event.pump()  # required to refresh controller state
        return {
            "axis_0": self.joystick.get_axis(0),
            "axis_1": self.joystick.get_axis(1),
        }