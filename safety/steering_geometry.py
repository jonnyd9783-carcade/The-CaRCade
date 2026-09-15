"""
safety/steering_geometry.py

Shared center-seeking steering-direction logic, used by every safety
strategy. Extracted from intervention.py rather than duplicated, since
this involves the same kind of sign-flip subtlety (forward/reverse
steering inversion) that's been a repeated source of bugs this
project — one validated implementation, not two copies to keep in sync.
"""

import math
from vehicle.state import ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y

ARENA_CENTER_X = (ARENA_MIN_X + ARENA_MAX_X) / 2
ARENA_CENTER_Y = (ARENA_MIN_Y + ARENA_MAX_Y) / 2


def shortest_signed_angle_diff(target, current):
    return (target - current + 180) % 360 - 180


def choose_steer_sign(vehicle):
    """
    Picks +1 or -1 steering command to rotate heading toward the arena
    center. Center-seeking naturally reduces closing velocity toward
    ALL nearby walls at once (handles corners correctly) — validated
    via numeric simulation across all four corners, forward and
    reverse, before being written into strategy 1.
    """
    dx = ARENA_CENTER_X - vehicle.x
    dy = ARENA_CENTER_Y - vehicle.y
    target_heading = math.degrees(math.atan2(dx, -dy))

    heading_mod = vehicle.heading % 360
    diff = shortest_signed_angle_diff(target_heading, heading_mod)
    desired_heading_change_sign = 1 if diff > 0 else -1

    effective_forward_speed_sign = 1 if -vehicle.speed > 0 else -1
    return desired_heading_change_sign * effective_forward_speed_sign