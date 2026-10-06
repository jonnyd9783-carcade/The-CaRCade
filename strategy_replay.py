"""
strategy_replay.py

Milestone 7: re-runs a recorded run's RAW player input through the live
physics and a selected safety strategy. Unlike replay_main.py, which only
redraws recorded positions and never simulates anything, this actually
re-simulates, so identical input can be tested under different strategies.

Usage:
    python3 strategy_replay.py telemetry_runs/<file>.csv
    python3 strategy_replay.py telemetry_runs/<file>.csv --strategy head_on_only
    python3 strategy_replay.py telemetry_runs/<old file>.csv --steer-deadzone 0.04 --throttle-deadzone 0.045

Writes its own telemetry file, named replay_<strategy>_<timestamp>.csv
(live runs are named run_<strategy>_<timestamp>.csv), so the result can
be watched later with replay_main.py.

Deadzones: the live run's deadzones are applied to the raw input, so replay
must use the same values or the paths diverge. Recordings made after the
deadzone columns were added carry them per frame, and replay uses those.
Older recordings don't, so replay falls back to --steer-deadzone and
--throttle-deadzone (default 0.12). Found via deadzone_sweep.py: the live
run's calibrated deadzones were about 0.04, and the old fixed 0.12 zeroed
inputs the live run applied.

Impact summary: vehicle/state.py records the velocity that carried the
vehicle into a wall (before the collision zeroes it). One impact is logged
the first frame each wall is hit (a vehicle pushed against a wall counts
once; pushing again after a gap counts again). Speeds are in px/frame.
Angles use this codebase's incidence convention: 0 = glancing, 90 =
head-on, measured from the wall surface. "vel_ang" is from the velocity
vector (what actually hit the wall); "nose_ang" is from the car's heading.
The ft/s figure assumes PIXELS_PER_FOOT and 60 fps, both placeholders, so
treat it as a readability aid; the strategy-to-strategy comparison is the
useful signal.

Known approximation:
- Simulated sensor noise is random, so the sensor/estimate columns won't
  match the original. The safety logic uses true vehicle state, so this
  doesn't affect the comparison.
"""

import csv
import math
import sys
import pygame
from dataclasses import dataclass
from render.view import View
from vehicle.state import (
    VehicleState, ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y,
    PIXELS_PER_FOOT,
)
from sensors.simulated_position import SimulatedPositionSensor
from estimation.position_estimator import PositionEstimator
from telemetry import Telemetry
from safety.collision_check import compute_incidence_degrees
from safety.intervention import SafetyIntervention
from safety.head_on_only import HeadOnOnlyIntervention

# NOTE: duplicated from main.py - keep the two in sync when adding a strategy.
STRATEGIES = {
    "brake_and_steer": SafetyIntervention,
    "head_on_only": HeadOnOnlyIntervention,
}

# Outward-pointing unit normal of each wall (screen coordinates, y grows down).
WALL_NORMALS = {
    "left": (-1, 0),
    "right": (1, 0),
    "top": (0, -1),
    "bottom": (0, 1),
}


@dataclass
class ReplayCommand:
    steering: float = 0.0
    throttle: float = 0.0


def touching_wall(vehicle):
    return (
        vehicle.x <= ARENA_MIN_X or vehicle.x >= ARENA_MAX_X
        or vehicle.y <= ARENA_MIN_Y or vehicle.y >= ARENA_MAX_Y
    )


def row_deadzone(row, column, fallback):
    value = row.get(column, "")
    if value is None or value == "":
        return fallback
    return float(value)


def normal_speed(vx, vy, wall):
    if wall in ("left", "right"):
        return abs(vx)
    return abs(vy)


def describe_impact(frame, walls, impact):
    vx = impact["velocity_x"]
    vy = impact["velocity_y"]
    heading_rad = math.radians(impact["heading"])
    nose_x = math.sin(heading_rad)
    nose_y = -math.cos(heading_rad)
    wall = max(walls, key=lambda w: normal_speed(vx, vy, w))
    nx, ny = WALL_NORMALS[wall]
    nose_dot = nose_x * nx + nose_y * ny
    return {
        "frame": frame,
        "wall": wall,
        "corner": len(walls) > 1,
        "total": math.hypot(vx, vy),
        "normal": normal_speed(vx, vy, wall),
        "vel_angle": compute_incidence_degrees(vx, vy, wall),
        "nose_angle": compute_incidence_degrees(nose_x, nose_y, wall),
        "part": "nose" if nose_dot > 0 else "rear",
    }


csv_path = None
strategy_name = "brake_and_steer"
fallback_steer_deadzone = 0.12
fallback_throttle_deadzone = 0.12
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--strategy" and i + 1 < len(args):
        strategy_name = args[i + 1]
        i += 2
    elif args[i] == "--steer-deadzone" and i + 1 < len(args):
        fallback_steer_deadzone = float(args[i + 1])
        i += 2
    elif args[i] == "--throttle-deadzone" and i + 1 < len(args):
        fallback_throttle_deadzone = float(args[i + 1])
        i += 2
    else:
        csv_path = args[i]
        i += 1

if csv_path is None:
    print("Usage: python3 strategy_replay.py <telemetry csv> [--strategy name] [--steer-deadzone x] [--throttle-deadzone y]")
    sys.exit(1)

if strategy_name not in STRATEGIES:
    print(f"Unknown strategy '{strategy_name}'. Options: {', '.join(STRATEGIES)}")
    sys.exit(1)

try:
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
except FileNotFoundError:
    print(f"File not found: {csv_path}")
    sys.exit(1)

if not rows or "steering_input_raw" not in rows[0]:
    print("This recording has no raw-input columns (recorded before the telemetry change).")
    print("Record a new run with main.py and use that file.")
    sys.exit(1)

if "steering_deadzone" in rows[0]:
    print("Using per-frame deadzones recorded in the file.")
else:
    print(f"No deadzone columns in this recording. Using steering {fallback_steer_deadzone}, "
          f"throttle {fallback_throttle_deadzone}.")

pygame.init()
pygame.display.set_mode((800, 600))

view = View()
vehicle = VehicleState()
position_sensor = SimulatedPositionSensor(vehicle)
estimator = PositionEstimator(vehicle.x, vehicle.y)
safety_system = STRATEGIES[strategy_name]()
telemetry = Telemetry(prefix=f"replay_{strategy_name}")
clock = pygame.time.Clock()

print(f"Replaying {csv_path} ({len(rows)} frames) with strategy: {strategy_name}")

frames = 0
intervention_frames = 0
wall_contacts = 0
was_touching = False
impacts = []
previous_hit_walls = set()

for row in rows:
    quit_requested = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_requested = True
    if quit_requested:
        break

    raw_command = ReplayCommand(
        steering=float(row["steering_input_raw"]),
        throttle=float(row["throttle_input_raw"]),
    )
    steer_dz = row_deadzone(row, "steering_deadzone", fallback_steer_deadzone)
    throttle_dz = row_deadzone(row, "throttle_deadzone", fallback_throttle_deadzone)

    final_command, intervening = safety_system.update(vehicle, raw_command)

    vehicle.apply_input(
        final_command.steering, final_command.throttle,
        steering_deadzone=steer_dz, throttle_deadzone=throttle_dz,
    )

    impact = getattr(vehicle, "impact", None)
    hit_walls_now = set(impact["walls"]) if impact else set()
    new_walls = hit_walls_now - previous_hit_walls
    if new_walls:
        impacts.append(describe_impact(frames + 1, new_walls, impact))
    previous_hit_walls = hit_walls_now

    sensor_reading = position_sensor.read()
    estimated_state = estimator.update(
        vehicle.velocity_x, vehicle.velocity_y, sensor_reading.x, sensor_reading.y
    )

    telemetry.record(
        vehicle, raw_command, final_command, intervening, safety_system.status,
        sensor_reading, estimated_state, steer_dz, throttle_dz,
    )

    view.draw(vehicle, sensor_reading, estimated_state)

    frames += 1
    if intervening:
        intervention_frames += 1
    touching = touching_wall(vehicle)
    if touching and not was_touching:
        wall_contacts += 1
    was_touching = touching

    clock.tick(60)

telemetry.close()
pygame.quit()

print("--- Summary ---")
print(f"Strategy: {strategy_name}")
print(f"Frames replayed: {frames}")
print(f"Frames with intervention: {intervention_frames}")
print(f"Wall contacts: {wall_contacts}")
print(f"Recorded run ended at ({float(rows[-1]['x']):.0f}, {float(rows[-1]['y']):.0f}); "
      f"this replay ended at ({vehicle.x:.0f}, {vehicle.y:.0f})")

print("--- Impacts (speeds in px/frame; angles in degrees, 0 = glancing, 90 = head-on) ---")
if not impacts:
    print("No wall impacts.")
else:
    print(f"{'#':>3} {'frame':>6} {'wall':<8} {'total':>6} {'normal':>7} {'vel_ang':>8} {'nose_ang':>9}  part")
    for n, e in enumerate(impacts, 1):
        wall_label = e["wall"] + ("*" if e["corner"] else "")
        print(f"{n:>3} {e['frame']:>6} {wall_label:<8} {e['total']:>6.2f} {e['normal']:>7.2f} "
              f"{e['vel_angle']:>8.1f} {e['nose_angle']:>9.1f}  {e['part']}")
    hardest = max(impacts, key=lambda e: e["normal"])
    mean_normal = sum(e["normal"] for e in impacts) / len(impacts)
    ftps = 60.0 / PIXELS_PER_FOOT
    print(f"Impact events: {len(impacts)}")
    print(f"Hardest: normal {hardest['normal']:.2f} px/frame (~{hardest['normal'] * ftps:.1f} ft/s) at frame {hardest['frame']}")
    print(f"Mean normal speed: {mean_normal:.2f} px/frame")
    print("* = corner hit (two walls in one frame); the wall with the larger normal speed is shown")
sys.exit()