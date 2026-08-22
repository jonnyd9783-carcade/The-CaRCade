import pygame
import sys
from render.view import View
from vehicle.state import VehicleState
from input.controller import Controller
from input.mapping import map_controller_input

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
    command = map_controller_input(raw)

    vehicle.apply_input(command.steering, command.throttle)

    view.draw(vehicle)

    clock.tick(60)

pygame.quit()
sys.exit()