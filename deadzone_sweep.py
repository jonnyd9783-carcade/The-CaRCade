"""
deadzone_sweep.py

One-off diagnostic (not part of the sim). Replays a live recording headless
(no window) through the same physics and brake_and_steer strategy, trying
many steering/throttle deadzone pairs, and reports which pairs reproduce the
recorded path exactly. The live run used the controller's calibrated
deadzones, which aren't saved in the CSV.

Usage:
    python3 deadzone_sweep.py telemetry_runs/run_2026-10-05_201803.csv
"""

import csv
import sys
from dataclasses import dataclass
from vehicle.state import VehicleState
from safety.intervention import SafetyIntervention

TOLERANCE = 1e-9  # recorded floats round-trip exactly, so a true match is ~0


@dataclass
class Cmd:
    steering: float = 0.0
    throttle: float = 0.0


def first_divergence(rows, steer_dz, throttle_dz):
    """Returns the first frame (1-based) where the replay's position differs
    from the recording, or len(rows) + 1 if it never does."""
    vehicle = VehicleState()
    safety = SafetyIntervention()
    for i, row in enumerate(rows):
        cmd = Cmd(float(row["steering_input_raw"]), float(row["throttle_input_raw"]))
        final, _ = safety.update(vehicle, cmd)
        vehicle.apply_input(
            final.steering, final.throttle,
            steering_deadzone=steer_dz, throttle_deadzone=throttle_dz,
        )
        err = abs(vehicle.x - float(row["x"])) + abs(vehicle.y - float(row["y"]))
        if err > TOLERANCE:
            return i + 1
    return len(rows) + 1


if len(sys.argv) < 2:
    print("Usage: python3 deadzone_sweep.py <live recording csv>")
    sys.exit(1)

with open(sys.argv[1], newline="") as f:
    rows = list(csv.DictReader(f))

if not rows or "steering_input_raw" not in rows[0]:
    print("Needs a recording with raw-input columns.")
    sys.exit(1)

perfect = len(rows) + 1

# Stage 1: coarse grid, 0.00 to 0.30 in steps of 0.01
coarse = [round(i * 0.01, 3) for i in range(31)]
results = []
for s in coarse:
    for t in coarse:
        results.append((first_divergence(rows, s, t), s, t))
results.sort(reverse=True)
print("Coarse sweep, best 5 (first divergent frame, steering dz, throttle dz):")
for r in results[:5]:
    print("  ", r)

best_frame, best_s, best_t = results[0]


# Stage 2: fine grid around the best coarse pair
def around(center):
    return [round(max(0.0, center - 0.01 + i * 0.001), 4) for i in range(21)]


matches = []
best_fine = 0
for s in around(best_s):
    for t in around(best_t):
        frame = first_divergence(rows, s, t)
        if frame > best_fine:
            best_fine = frame
            matches = []
        if frame == best_fine:
            matches.append((s, t))

print()
if best_fine == perfect:
    print("EXACT MATCH. All frames reproduced.")
else:
    print(f"No exact match. Best pair first diverges at frame {best_fine} of {len(rows)}.")
steer_vals = sorted(set(m[0] for m in matches))
throttle_vals = sorted(set(m[1] for m in matches))
print(f"Steering deadzone range that achieves this: {steer_vals[0]} to {steer_vals[-1]}")
print(f"Throttle deadzone range that achieves this: {throttle_vals[0]} to {throttle_vals[-1]}")
sys.exit()
