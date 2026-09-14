"""
safety/collision_check.py

Milestone 7 (Safety Experiments) — TTC-based boundary hazard detection.

Core idea: compare raw time-to-collision (TTC) against how long the
FULL response sequence actually takes — a fixed brake delay (during
which zero rotation happens) plus the real rotation time needed at
current speed and max steering lock. A near-perpendicular approach
needs more lead time (more rotation required) than a glancing approach.

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
threshold indefinitely. MAX_RELEVANT_TTC_FRAMES is a hard absolute
ceiling on top of the relative comparison, fixing this.

Second bug caught via live testing: with no minimum closing-speed floor,
a nearly-stationary vehicle in a tight corner could still register a
small raw_ttc and trigger intervention. MIN_CLOSING_SPEED_FOR_INTERVENTION
fixes this: below this speed, never intervene, regardless of distance.

Third bug caught via live testing: the intervention got stuck in an
endless brake->steer->brake->steer loop, never resolving. Root cause:
the steering phase's duration used to be pre-computed ONCE at trigger
time from the speed at that moment, but speed keeps dropping throughout
braking and steering (friction decay), so the real achievable rotation
rate during steering is lower than what was assumed when the duration
was calculated — the fixed frame count under-rotates relative to what's
actually needed, hands back control still unsafe, and immediately
re-triggers. Fix: compute_incidence_degrees() is now exposed here so
safety/intervention.py can check the LIVE, current incidence angle each
frame during steering, rather than trusting a stale precomputed
duration. Steering now continues until incidence is actually safe,
however long that genuinely takes.
"""

import math
from vehicle.state import (
    ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y,
    WHEELBASE_PIXELS, MAX_STEERING_ANGLE_DEGREES,
)

SAFETY_MARGIN = 1.10  # margin applied to the rotation-time portion only
MAX_RELEVANT_TTC_FRAMES = 90  # never intervene beyond this, regardless of ratio (~1.5 sec at 60fps)
MIN_CLOSING_SPEED_FOR_INTERVENTION = 1.0  # ~17% of TOP_SPEED=6.0 — below this, never intervene
BRAKE_DURATION_FRAMES = 10  # fixed brake-phase length in safety/intervention.py; zero rotation happens during this window


def max_angular_velocity_rad_per_frame(speed, wheelbase_pixels=WHEELBASE_PIXELS,
                                        max_steering_angle_degrees=MAX_STEERING_ANGLE_DEGREES):
    """How fast the vehicle CAN rotate at max steering lock, given current speed."""
    max_angle_rad = math.radians(max_steering_angle_degrees)
    return abs(speed) * math.tan(max_angle_rad) / wheelbase_pixels


def compute_incidence_degrees(velocity_x, velocity_y, wall):
    """
    Angle (degrees) between the given velocity vector and the wall's
    surface. 90 = straight into the wall (head-on), 0 = parallel/
    glancing. Shared by detection (check_boundary_ttc) and the live
    steering-phase exit check in safety/intervention.py, so both always
    agree on the exact same definition.
    """
    if wall in ("left", "right"):
        incidence_rad = math.atan2(abs(velocity_x), abs(velocity_y)) if velocity_y != 0 else math.pi / 2
    else:
        incidence_rad = math.atan2(abs(velocity_y), abs(velocity_x)) if velocity_x != 0 else math.pi / 2
    return math.degrees(incidence_rad)


def check_boundary_ttc(vehicle):
    """
    Checks all four arena walls. Returns a dict describing the single
    most urgent wall (if any wall is actually being approached with
    meaningful speed), or None if no wall currently poses a concern.
    """
    vx = vehicle.velocity_x
    vy = vehicle.velocity_y

    candidates = []

    if vx > MIN_CLOSING_SPEED_FOR_INTERVENTION:
        candidates.append(("right", ARENA_MAX_X - vehicle.x, vx))
    if vx < -MIN_CLOSING_SPEED_FOR_INTERVENTION:
        candidates.append(("left", vehicle.x - ARENA_MIN_X, -vx))
    if vy > MIN_CLOSING_SPEED_FOR_INTERVENTION:
        candidates.append(("bottom", ARENA_MAX_Y - vehicle.y, vy))
    if vy < -MIN_CLOSING_SPEED_FOR_INTERVENTION:
        candidates.append(("top", vehicle.y - ARENA_MIN_Y, -vy))

    if not candidates:
        return None

    speed_total = math.hypot(vx, vy)
    if speed_total < 0.01:
        return None

    best = None
    for wall, distance, closing_speed in candidates:
        raw_ttc = distance / closing_speed

        if raw_ttc > MAX_RELEVANT_TTC_FRAMES:
            continue

        incidence_degrees = compute_incidence_degrees(vx, vy, wall)
        incidence_rad = math.radians(incidence_degrees)

        max_ang_vel = max_angular_velocity_rad_per_frame(speed_total)
        if max_ang_vel < 1e-6:
            continue
        time_to_rotate_frames = incidence_rad / max_ang_vel

        required_lead_time = BRAKE_DURATION_FRAMES + (time_to_rotate_frames * SAFETY_MARGIN)

        result = {
            "wall": wall,
            "distance": distance,
            "raw_ttc_frames": raw_ttc,
            "incidence_degrees": incidence_degrees,
            "time_to_rotate_frames": time_to_rotate_frames,
            "would_intervene": raw_ttc < required_lead_time,
        }

        if best is None or raw_ttc < best["raw_ttc_frames"]:
            best = result

    return best