import pygame
import sys
import os
from render.view import View
from vehicle.state import VehicleState
from replay import Replay
from sensors.simulated_position import SensorReading
from estimation.position_estimator import EstimatedState

filepath = sys.argv[1] if len(sys.argv) > 1 else None

if filepath is None:
    print("Usage: python3 replay_main.py path/to/telemetry_runs/run_....csv")
    sys.exit()

if not os.path.exists(filepath):
    print("File not found: " + filepath)
    print("Check the path and try again.")
    sys.exit()

pygame.init()
pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sim Lab - Replay")

view = View()
vehicle = VehicleState()
replay = Replay(filepath)

clock = pygame.time.Clock()

running = True
while running and replay.has_next():
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    row = replay.next_frame()
    vehicle.x = float(row["x"])
    vehicle.y = float(row["y"])
    vehicle.heading = float(row["heading"])

    # Older recordings (before this column existed) won't have this key —
    # fall back to matching heading, so the yellow line at least doesn't
    # freeze at 0 for old runs.
    if row.get("direction_of_travel") not in (None, ""):
        vehicle.direction_of_travel = float(row["direction_of_travel"])
    else:
        vehicle.direction_of_travel = vehicle.heading

    sensor_reading = None
    if row.get("sensor_x") not in (None, ""):
        sensor_reading = SensorReading(x=float(row["sensor_x"]), y=float(row["sensor_y"]))

    estimated_state = None
    if row.get("estimated_x") not in (None, ""):
        estimated_state = EstimatedState(x=float(row["estimated_x"]), y=float(row["estimated_y"]))

    view.draw(vehicle, sensor_reading, estimated_state)

    clock.tick(60)

pygame.quit()
sys.exit()