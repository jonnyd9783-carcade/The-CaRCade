"""
steering_whatif.py

One-off diagnostic (not part of the sim). Replays a recording headless up
to a chosen frame, freezes the vehicle and the brake_and_steer strategy at
that moment, then continues the maneuver three ways and reports the first
real wall impact in each:

  A  as-is        the strategy continues unchanged (must reproduce the
                  impact recorded by strategy_replay.py: this is the check
                  that the snapshot is right)
  B  flipped      same state, steering direction reversed
  C  no safety    the player's raw input only, no intervention

Only brake_and_steer is supported: its steering direction is chosen once at
trigger time, so it can be flipped. head_on_only recomputes it every frame.

Usage:
    python3 steering_whatif.py telemetry_runs/run_2026-10-05_201803.csv 1020
    python3 steering_whatif.py <csv> <frame> [--steer-deadzone x] [--throttle-deadzone y]

"frame" is the 1-based frame number shown by strategy_replay.py and in the
telemetry rows. The snapshot is the state after that frame is processed.
Speeds are px/frame. Angles use this codebase's convention: 0 = glancing,
90 = head-on, measured from the wall surface.
"""

import copy
import csv
import math
import sys
from dataclasses import dataclass
from vehicle.state import VehicleState
from safety.collision_check import compute_incidence_degrees
from safety.intervention import SafetyIntervention

MAX_FRAMES_AFTER = 150
MIN_IMPACT_NORMAL_SPEED = 0.1  # below this a contact is the car resting on the wall

WALL_NORMALS = {
    "left": (-1, 0),
    "right": (1, 0),
    "top": (0, -1),
    "bottom": (0, 1),
}


@dataclass
class Cmd:
    steering: float = 0.0
    throttle: float = 0.0


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
    return {
        "frame": frame,
        "wall": wall,
        "total": math.hypot(vx, vy),
        "normal": normal_speed(vx, vy, wall),
        "vel_angle": compute_incidence_degrees(vx, vy, wall),
        "nose_angle": compute_incidence_degrees(nose_x, nose_y, wall),
        "part": "nose" if (nose_x * nx + nose_y * ny) > 0 else "rear",
    }


def step(vehicle, safety, row, steer_fallback, throttle_fallback):
    cmd = Cmd(float(row["steering_input_raw"]), float(row["throttle_input_raw"]))
    steer_dz = row_deadzone(row, "steering_deadzone", steer_fallback)
    throttle_dz = row_deadzone(row, "throttle_deadzone", throttle_fallback)
    if safety is not None:
        final, _ = safety.update(vehicle, cmd)
    else:
        final = cmd
    vehicle.apply_input(
        final.steering, final.throttle,
        steering_deadzone=steer_dz, throttle_deadzone=throttle_dz,
    )


def run_variant(vehicle0, safety0, rows, start_index, flip, steer_fb, throttle_fb):
    vehicle = copy.deepcopy(vehicle0)
    safety = copy.deepcopy(safety0) if safety0 is not None else None
    if flip and safety is not None:
        safety.steer_sign = -safety.steer_sign
    end_index = min(len(rows), start_index + MAX_FRAMES_AFTER)
    for k in range(start_index, end_index):
        step(vehicle, safety, rows[k], steer_fb, throttle_fb)
        impact = getattr(vehicle, "impact", None)
        if impact:
            found = describe_impact(k + 1, set(impact["walls"]), impact)
            if found["normal"] >= MIN_IMPACT_NORMAL_SPEED:
                return found, vehicle
    return None, vehicle


csv_path = None
snapshot_frame = None
steer_fallback = 0.12
throttle_fallback = 0.12
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--steer-deadzone" and i + 1 < len(args):
        steer_fallback = float(args[i + 1])
        i += 2
    elif args[i] == "--throttle-deadzone" and i + 1 < len(args):
        throttle_fallback = float(args[i + 1])
        i += 2
    elif csv_path is None:
        csv_path = args[i]
        i += 1
    else:
        snapshot_frame = int(args[i])
        i += 1

if csv_path is None or snapshot_frame is None:
    print("Usage: python3 steering_whatif.py <csv> <frame> [--steer-deadzone x] [--throttle-deadzone y]")
    sys.exit(1)

with open(csv_path, newline="") as f:
    rows = list(csv.DictReader(f))

if not rows or "steering_input_raw" not in rows[0]:
    print("Needs a recording with raw-input columns.")
    sys.exit(1)

if snapshot_frame < 1 or snapshot_frame >= len(rows):
    print(f"Frame must be between 1 and {len(rows) - 1}.")
    sys.exit(1)

vehicle = VehicleState()
safety = SafetyIntervention()
for k in range(snapshot_frame):
    step(vehicle, safety, rows[k], steer_fallback, throttle_fallback)

print(f"Snapshot after frame {snapshot_frame}: x={vehicle.x:.0f}, y={vehicle.y:.0f}, "
      f"speed={vehicle.speed:.2f}, heading={vehicle.heading:.1f}")
print(f"Strategy phase: {safety.phase}, steer_sign: {safety.steer_sign:+d}")
if safety.phase == "idle":
    print("WARNING: the strategy is idle at this frame, so flipping the steering direction changes nothing.")

variants = [
    ("A as-is", False, True),
    ("B flipped steering", True, True),
    ("C no safety", False, False),
]

print()
print(f"{'variant':<20} {'frame':>6} {'wall':<7} {'total':>6} {'normal':>7} {'vel_ang':>8} {'nose_ang':>9}  part")
for label, flip, use_safety in variants:
    result, end_vehicle = run_variant(
        vehicle, safety if use_safety else None, rows, snapshot_frame,
        flip, steer_fallback, throttle_fallback,
    )
    if result is None:
        print(f"{label:<20} no impact within {MAX_FRAMES_AFTER} frames "
              f"(ended at x={end_vehicle.x:.0f}, y={end_vehicle.y:.0f}, speed={end_vehicle.speed:.2f})")
    else:
        print(f"{label:<20} {result['frame']:>6} {result['wall']:<7} {result['total']:>6.2f} "
              f"{result['normal']:>7.2f} {result['vel_angle']:>8.1f} {result['nose_angle']:>9.1f}  {result['part']}")

print()
print("Check: variant A must match the impact strategy_replay.py recorded for this run.")
sys.exit()
