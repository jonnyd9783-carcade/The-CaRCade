"""
safety/steering_geometry.py

Shared center-seeking steering-direction logic, used by every safety
strategy. One validated implementation, not copies to keep in sync,
since this involves the sign-flip subtleties (forward/reverse steering
inversion) that have been a repeated source of bugs in this project.

REVERSE BUG, found via live testing, now fixed: the original version
rotated the vehicle's NOSE toward the arena center. That is only
correct when moving forward, where nose and direction of travel are
the same. In reverse the vehicle moves OPPOSITE its nose, so turning
the nose toward center turned the direction of travel AWAY from center
- steering into the wall. Now the direction of TRAVEL (heading when
moving forward, heading + 180 when reversing) is what gets rotated
toward center. The separate steering-command sign flip for reverse
(steering's effect on heading inverts when backing up) is unchanged.
Validated numerically over 67 position/direction scenarios, forward
and reverse: 0 wrong-way turns in either direction after the fix
(reverse was wrong in all 67 before it).
"""

import math
from vehicle.state import ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y

ARENA_CENTER_X = (ARENA_MIN_X + ARENA_MAX_X) / 2
ARENA_CENTER_Y = (ARENA_MIN_Y + ARENA_MAX_Y) / 2


def shortest_signed_angle_diff(target, current):
    return (target - current + 180) % 360 - 180


def choose_steer_sign(vehicle):
    """
    Picks +1 or -1 steering command so the vehicle's direction of
    TRAVEL rotates toward the arena center. Center-seeking naturally
    reduces closing velocity toward ALL nearby walls at once, which
    handles corners correctly.
    """
    dx = ARENA_CENTER_X - vehicle.x
    dy = ARENA_CENTER_Y - vehicle.y
    target_heading = math.degrees(math.atan2(dx, -dy))

    # Forward = negative speed in this codebase. In reverse, the
    # direction of travel is opposite the nose.
    if vehicle.speed < 0:
        travel_heading = vehicle.heading
    else:
        travel_heading = vehicle.heading + 180

    diff = shortest_signed_angle_diff(target_heading, travel_heading % 360)
    desired_heading_change_sign = 1 if diff > 0 else -1

    effective_forward_speed_sign = 1 if -vehicle.speed > 0 else -1
    return desired_heading_change_sign * effective_forward_speed_sign