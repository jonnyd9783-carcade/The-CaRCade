import pygame
import sys
import time
from render.view import View
from vehicle.state import VehicleState
from replay import Replay

filepath = sys.argv[1] if len(sys.argv) > 1 else None

if filepath is None:
    print("Usage: python3 replay_main.py path/to/telemetry_runs/run_....csv")
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

    view.draw(vehicle)

    clock.tick(60)

pygame.quit()
sys.exit()