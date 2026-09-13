"""
safety/collision_check.py

Milestone 7 (Safety Experiments) — Step A: detection/decision logic only.
Does NOT modify the player's command yet — just calculates whether the
system WOULD intervene, and logs it. Wiring in the actual brake+steer
intervention is a deliberate second step, once this detection logic has
been watched in real driving and confirmed to behave sensibly.

Core idea: compare raw time-to-collision (TTC) against how long the
vehicle would actually need to rotate away from the wall at max steering
lock, using the same bicycle-model math already built for wheelbase-aware
steering. A near-perpendicular approach needs more lead time (more
rotation required) than a glancing approach (less rotation required).

Known approximation, not exact: "required rotation" is estimated as the
angle between the current velocity vector and the wall, which assumes
velocity direction already matches heading. In reality MOMENTUM_LAG means
these can differ slightly during a sharp turn — good enough to test the
overall trigger logic, not treated as precise.

Arena is currently axis-aligned, so wall-relative geometry is simplified
to direct x/y component checks rather than general vector projection —
this simplification stops being valid the moment non-axis-aligned
obstacles or other vehicles are introduced (see project notes on
eventual shapely-based geometry for that future case).

Bug caught via live testing (not assumption): both raw_ttc and
time_to_rotate scale as 1/speed, so as the vehicle coasts and slows down,
BOTH numbers grow together and their ratio can stay past the trigger
threshold indefinitely — even when the vehicle is barely moving and
genuinely many seconds from the wall. MAX_RELEVANT_TTC_FRAMES is a hard
absolute ceiling on top of the relative comparison, fixing this.
"""

import math
from vehicle.state import (
    ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y,
    WHEELBASE_PIXELS, MAX_STEERING_ANGLE_DEGREES,
)

SAFETY_MARGIN = 1.3  # intervene when raw TTC < required-rotation-time * this margin
MAX_RELEVANT_TTC_FRAMES = 90  # never intervene beyond this, regardless of ratio (~1.5 sec at 60fps)


def max_angular_velocity_rad_per_frame(speed, wheelbase_pixels=WHEELBASE_PIXELS,
                                        max_steering_angle_degrees=MAX_STEERING_ANGLE_DEGREES):
    """How fast the vehicle CAN rotate at max steering lock, given current speed."""
    max_angle_rad = math.radians(max_steering_angle_degrees)
    return abs(speed) * math.tan(max_angle_rad) / wheelbase_pixels


def check_boundary_ttc(vehicle):
    """
    Checks all four arena walls. Returns a dict describing the single
    most urgent wall (if any wall is actually being approached), or None
    if no wall currently poses a concern.
    """
    vx = vehicle.velocity_x
    vy = vehicle.velocity_y

    candidates = []

    # Right wall: closing if vx > 0
    if vx > 0.01:
        distance = ARENA_MAX_X - vehicle.x
        candidates.append(("right", distance, vx))
    # Left wall: closing if vx < 0
    if vx < -0.01:
        distance = vehicle.x - ARENA_MIN_X
        candidates.append(("left", distance, -vx))
    # Bottom wall: closing if vy > 0
    if vy > 0.01:
        distance = ARENA_MAX_Y - vehicle.y
        candidates.append(("bottom", distance, vy))
    # Top wall: closing if vy < 0
    if vy < -0.01:
        distance = vehicle.y - ARENA_MIN_Y
        candidates.append(("top", distance, -vy))

    if not candidates:
        return None

    speed_total = math.hypot(vx, vy)
    if speed_total < 0.01:
        return None

    best = None
    for wall, distance, closing_speed in candidates:
        if closing_speed <= 0.01:
            continue
        raw_ttc = distance / closing_speed

        # Skip entirely if beyond the absolute relevance ceiling — no
        # point computing rotation time for a wall that's many seconds
        # away regardless of ratio.
        if raw_ttc > MAX_RELEVANT_TTC_FRAMES:
            continue

        # Approximate required rotation: angle between velocity vector
        # and the wall's surface. For a vertical wall (left/right), the
        # wall surface runs along y — incidence angle is the angle of
        # the velocity vector off the y-axis. For a horizontal wall
        # (top/bottom), the wall surface runs along x — incidence angle
        # is the angle of the velocity vector off the x-axis.
        if wall in ("left", "right"):
            incidence_rad = math.atan2(abs(vx), abs(vy)) if vy != 0 else math.pi / 2
        else:
            incidence_rad = math.atan2(abs(vy), abs(vx)) if vx != 0 else math.pi / 2

        max_ang_vel = max_angular_velocity_rad_per_frame(speed_total)
        if max_ang_vel < 1e-6:
            continue
        time_to_rotate_frames = incidence_rad / max_ang_vel

        result = {
            "wall": wall,
            "distance": distance,
            "raw_ttc_frames": raw_ttc,
            "incidence_degrees": math.degrees(incidence_rad),
            "time_to_rotate_frames": time_to_rotate_frames,
            "would_intervene": raw_ttc < time_to_rotate_frames * SAFETY_MARGIN,
        }

        if best is None or raw_ttc < best["raw_ttc_frames"]:
            best = result

    return best