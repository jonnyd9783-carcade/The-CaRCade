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
from safety.intervention import SafetyIntervention
from safety.head_on_only import HeadOnOnlyIntervention

STRATEGIES = {
    "brake_and_steer": SafetyIntervention,
    "head_on_only": HeadOnOnlyIntervention,
}

strategy_name = "brake_and_steer"
for i, arg in enumerate(sys.argv):
    if arg == "--strategy" and i + 1 < len(sys.argv):
        strategy_name = sys.argv[i + 1]

if strategy_name not in STRATEGIES:
    print(f"Unknown strategy '{strategy_name}', defaulting to brake_and_steer")
    strategy_name = "brake_and_steer"

pygame.init()
pygame.display.set_mode((800, 600))

view = View()
vehicle = VehicleState()
position_sensor = SimulatedPositionSensor(vehicle)
estimator = PositionEstimator(vehicle.x, vehicle.y)
safety_system = STRATEGIES[strategy_name]()
print(f"Using safety strategy: {strategy_name}")
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

    final_command, intervening = safety_system.update(vehicle, command)
    if intervening:
        print(f"[SAFETY] intervening: phase={getattr(safety_system, 'phase', 'active')}")

    vehicle.apply_input(final_command.steering, final_command.throttle, steering_deadzone=steering_deadzone, throttle_deadzone=throttle_deadzone)

    sensor_reading = position_sensor.read()
    estimated_state = estimator.update(vehicle.velocity_x, vehicle.velocity_y, sensor_reading.x, sensor_reading.y)

    if recording_started:
        telemetry.record(vehicle, final_command, sensor_reading, estimated_state)

    view.draw(vehicle, sensor_reading, estimated_state)

    clock.tick(60)

telemetry.close()
pygame.quit()
sys.exit()