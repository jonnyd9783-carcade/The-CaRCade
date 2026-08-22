import pygame
import time

pygame.init()
pygame.display.set_mode((100, 100))  # forces SDL to fully initialize on macOS
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller found. Is it paired and on?")
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Found: {joystick.get_name()}")
    print(f"Number of axes: {joystick.get_numaxes()}")
    print("Move the sticks around. Press Ctrl+C to stop.")

    while True:
        pygame.event.pump()
        axes = [round(joystick.get_axis(i), 2) for i in range(joystick.get_numaxes())]
        print(axes)
        time.sleep(0.2)