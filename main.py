import pygame
import sys
import time
from render.view import View
from vehicle.state import VehicleState
from input.controller import Controller
from input.keyboard_controller import KeyboardController
from input.mapping import map_controller_input
from input.mapping import map_keyboard_input

pygame.init()
pygame.display.set_mode((800, 600))

view = View()
vehicle = VehicleState()

input_source = None
map_input = None

start_time = time.time()
print("Waiting for controller...")

while time.time() - start_time < 10:
    pygame.event.pump()
    pygame.joystick.init()
    count = pygame.joystick.get_count()
    if count > 0:
        input_source = Controller()
        input_source.calibrate()
        map_input = map_controller_input
        break
    view.draw(vehicle)
    time.sleep(0.2)

if input_source is None:
    print("10 seconds elapsed, switching to keyboard.")
    input_source = KeyboardController()
    map_input = map_keyboard_input

clock = pygame.time.Clock()

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if hasattr(input_source, "calibrate") and hasattr(input_source, "joystick"):
        if input_source.joystick.get_button(8):
            input_source.calibrate()
            
    raw = input_source.read_raw()
    command = map_input(raw)

    vehicle.apply_input(command.steering, command.throttle)

    view.draw(vehicle)

    clock.tick(60)

pygame.quit()
sys.exit()