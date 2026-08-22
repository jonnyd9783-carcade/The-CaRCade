import pygame
import sys
from render.view import View
from vehicle.state import VehicleState
from input.controller import Controller

pygame.init()
pygame.display.set_mode((800, 600))

view = View()
vehicle = VehicleState()
controller = Controller()
controller.calibrate()

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    raw = controller.read_raw()
    steering = raw["axis_0"]
    throttle = raw["axis_1"]

    vehicle.apply_input(steering, throttle)

    view.draw(vehicle)

    clock.tick(60)  # cap and stabilize the loop at 60 frames per second

pygame.quit()
sys.exit()