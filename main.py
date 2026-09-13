import pygame
import sys
import time
from render.view import View
from vehicle.state import VehicleState
from input.controller import Controller
from input.keyboard_controller import KeyboardController
from input.mapping import map_controller_input
from input.mapping import map_keyboard_input
from telemetry import Telemetry
from sensors.simulated_position import SimulatedPositionSensor
from estimation.position_estimator import PositionEstimator
from safety.collision_check import check_boundary_ttc

pygame.init()
pygame.display.set_mode((800, 600))

view = View()
vehicle = VehicleState()
position_sensor = SimulatedPositionSensor(vehicle)
estimator = PositionEstimator(vehicle.x, vehicle.y)
telemetry = Telemetry()
recording_started = False

input_source = None
map_input = None
steering_deadzone = 0.12
throttle_deadzone = 0.12

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
        steering_deadzone = input_source.deadzone["axis_2"]
        throttle_deadzone = input_source.deadzone["axis_1"]
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
            steering_deadzone = input_source.deadzone["axis_2"]
            throttle_deadzone = input_source.deadzone["axis_1"]

    raw = input_source.read_raw()
    command = map_input(raw)

    if not recording_started:
        if abs(command.steering) > steering_deadzone or abs(command.throttle) > throttle_deadzone:
            recording_started = True
            print("First input detected, telemetry recording started.")

    vehicle.apply_input(command.steering, command.throttle, steering_deadzone=steering_deadzone, throttle_deadzone=throttle_deadzone)

    # --- Milestone 7, Step A: detection only, does not modify command yet ---
    safety_check = check_boundary_ttc(vehicle)
    if safety_check and safety_check["would_intervene"]:
        print(f"[SAFETY] would intervene: {safety_check['wall']} wall, "
              f"incidence={safety_check['incidence_degrees']:.1f}°, "
              f"raw_ttc={safety_check['raw_ttc_frames']:.1f}f, "
              f"rotate_time={safety_check['time_to_rotate_frames']:.1f}f")

    sensor_reading = position_sensor.read()
    estimated_state = estimator.update(vehicle.velocity_x, vehicle.velocity_y, sensor_reading.x, sensor_reading.y)

    if recording_started:
        telemetry.record(vehicle, command, sensor_reading, estimated_state)

    view.draw(vehicle, sensor_reading, estimated_state)

    clock.tick(60)

telemetry.close()
pygame.quit()
sys.exit()