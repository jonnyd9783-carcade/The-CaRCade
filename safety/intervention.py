"""
safety/intervention.py

Milestone 7, Step B: the actual brake-then-steer intervention, per the
confirmed hypothesis in fleet-hardware.md. Unlike Step A's detection
(stateless, re-evaluated fresh every frame), this needs to remember
which phase it's in across frames — brake for a short duration, then
steer away, then return control to the player.

Starting values below are deliberately minimal/conservative, per
charter section 14's "as invisible and minimally intrusive as
possible" — placeholders to get something reasonable running now,
explicitly flagged for real tuning once more driving data exists.

Fixed via live testing: the steering phase used to run for a duration
precomputed ONCE at trigger time, using the speed at that moment. But
speed keeps dropping throughout braking and steering (friction decay),
so the real achievable rotation rate during steering ends up lower than
assumed — the stale duration under-rotates relative to what's actually
needed, hands back control still unsafe, and immediately re-triggers.
Fix: the steering phase now checks the LIVE, current incidence angle
every frame (via collision_check.compute_incidence_degrees, the same
formula detection uses) and only exits once it's genuinely below
SAFE_INCIDENCE_DEGREES. MAX_STEER_FRAMES is a defensive ceiling only.

Player-match early exit, per charter section 14's "as invisible as
possible" principle: braking ends early — moving into the steering
phase — if the player's own throttle OR steering already points the
same direction being commanded (either counts). This early exit only
advances braking into steering — it does NOT skip the steering phase
itself, which still runs its own separate exit logic: steering hands
full control back immediately if the player's own steering matches, or
once the live incidence angle is genuinely safe. Both matching checks
require input to clearly exceed MATCHING_INPUT_THRESHOLD, not noise.

CORNER BUG, found via live testing, now fixed: the original steering
logic picked a direction parallel to whichever SINGLE wall triggered
detection, with no awareness that a second, adjacent wall might also
be close (a corner). This could steer the vehicle away from one wall
directly into the other. Fix: steering direction is now chosen by
aiming toward the ARENA CENTER, not parallel to one specific wall.
Center-seeking naturally reduces closing velocity toward ALL nearby
walls at once, not just the one that happened to trigger — validated
via numeric simulation across all four corners, both forward and
reverse, plus the plain single-wall case, before being written here.
This also happens to resolve the earlier "arena-specific, not general"
limitation: aiming at a center point (or more generally, away from the
nearest boundary point) generalizes far better to non-rectangular
geometry than hardcoded per-wall candidate headings ever could.

Speed-based early exit, found via live testing: intervention could
keep running (braking or steering) even after speed had already dropped
enough that no real danger remained. Now, if vehicle.speed drops below
MIN_CLOSING_SPEED_FOR_INTERVENTION (the same threshold used to decide
whether to trigger in the first place) at any point during either
phase, the intervention ends immediately and hands back full control.

STEER_INTERVENTION_MAGNITUDE: steering strength during the steering
phase is a tunable 0-1 scale, not hardcoded to full lock. Since the
steering phase's exit is live (keeps steering until incidence actually
drops below SAFE_INCIDENCE_DEGREES, not a fixed duration), reducing this
just means slower rotation taking more frames to complete — the system
naturally compensates. At very low values, watch for the MAX_STEER_FRAMES
safety ceiling cutting off an incomplete turn before it finishes.

`status` property exposes `self.phase` under a name shared with
head_on_only.py's own status tracking, so main.py (and telemetry) can
report what any strategy is doing without needing to know its internal
structure.

BRAKE_DURATION_FRAMES lives in collision_check.py, not here — it's a
timing input to the trigger-condition calculation there, not just a
response-behavior parameter. Imported from there to avoid duplicating
the constant in two places.
"""

from dataclasses import dataclass
from vehicle.state import ARENA_MIN_X, ARENA_MAX_X, ARENA_MIN_Y, ARENA_MAX_Y
from safety.collision_check import (
    check_boundary_ttc,
    compute_incidence_degrees,
    BRAKE_DURATION_FRAMES,
    MIN_CLOSING_SPEED_FOR_INTERVENTION,
)
import math

ARENA_CENTER_X = (ARENA_MIN_X + ARENA_MAX_X) / 2
ARENA_CENTER_Y = (ARENA_MIN_Y + ARENA_MAX_Y) / 2

# --- Placeholder tuning constants, minimal starting point ---
BRAKE_THROTTLE_MAGNITUDE = 0.5     # half-strength brake command, not a full slam
STEER_INTERVENTION_MAGNITUDE = 1.0  # 0-1 scale; 1.0 = full lock (original behavior)
SAFE_INCIDENCE_DEGREES = 30          # steering phase exits once incidence drops below this
MAX_STEER_FRAMES = 90                # defensive ceiling only — should rarely if ever be hit
MATCHING_INPUT_THRESHOLD = 0.2       # player input must clearly exceed this to count as "matching", not noise


def _shortest_signed_angle_diff(target, current):
    return (target - current + 180) % 360 - 180


def _choose_steer_sign(vehicle):
    """
    Picks +1 or -1 steering command to rotate heading toward the arena
    center, accounting for the fact that steering's rotational effect
    flips sign depending on current forward/reverse motion (confirmed
    behavior from wheelbase-aware steering work). Aiming at center
    (rather than parallel to whichever single wall triggered detection)
    naturally handles corners: it reduces closing velocity toward ALL
    nearby walls at once, not just one — see module docstring.
    """
    dx = ARENA_CENTER_X - vehicle.x
    dy = ARENA_CENTER_Y - vehicle.y
    target_heading = math.degrees(math.atan2(dx, -dy))

    heading_mod = vehicle.heading % 360
    diff = _shortest_signed_angle_diff(target_heading, heading_mod)
    desired_heading_change_sign = 1 if diff > 0 else -1

    effective_forward_speed_sign = 1 if -vehicle.speed > 0 else -1
    return desired_heading_change_sign * effective_forward_speed_sign


def _matches_direction(player_value, commanded_sign):
    """True if the player's own input clearly points the same direction
    as commanded_sign (not just incidental stick noise)."""
    if commanded_sign > 0:
        return player_value > MATCHING_INPUT_THRESHOLD
    elif commanded_sign < 0:
        return player_value < -MATCHING_INPUT_THRESHOLD
    return False


@dataclass
class InterventionCommand:
    steering: float = 0.0
    throttle: float = 0.0


class SafetyIntervention:
    def __init__(self):
        self.phase = "idle"  # "idle" | "braking" | "steering"
        self.frames_remaining = 0  # only meaningful during "braking"
        self.brake_throttle_sign = 0
        self.steer_sign = 0
        self.target_wall = None
        self.steer_frame_count = 0  # safety-ceiling counter during "steering"

    @property
    def status(self):
        return self.phase

    def update(self, vehicle, player_command):
        """
        Returns (final_command, intervening_bool). When not intervening,
        final_command is just the player's original command, untouched.
        """
        if self.phase == "idle":
            check = check_boundary_ttc(vehicle)
            if check and check["would_intervene"]:
                self.phase = "braking"
                self.frames_remaining = BRAKE_DURATION_FRAMES
                self.brake_throttle_sign = -1 if vehicle.speed < 0 else 1
                self.steer_sign = _choose_steer_sign(vehicle)
                self.target_wall = check["wall"]
            else:
                return player_command, False

        if self.phase == "braking":
            if abs(vehicle.speed) < MIN_CLOSING_SPEED_FOR_INTERVENTION:
                self.phase = "idle"
                return player_command, False

            throttle_matches = _matches_direction(player_command.throttle, self.brake_throttle_sign)
            steering_matches = _matches_direction(player_command.steering, self.steer_sign)
            if throttle_matches or steering_matches:
                self.phase = "steering"
                self.steer_frame_count = 0
                return player_command, False

            command = InterventionCommand(
                steering=0.0,
                throttle=self.brake_throttle_sign * BRAKE_THROTTLE_MAGNITUDE,
            )
            self.frames_remaining -= 1
            if self.frames_remaining <= 0:
                self.phase = "steering"
                self.steer_frame_count = 0
            return command, True

        if self.phase == "steering":
            if abs(vehicle.speed) < MIN_CLOSING_SPEED_FOR_INTERVENTION:
                self.phase = "idle"
                return player_command, False

            if _matches_direction(player_command.steering, self.steer_sign):
                self.phase = "idle"
                return player_command, False

            command = InterventionCommand(
                steering=self.steer_sign * STEER_INTERVENTION_MAGNITUDE,
                throttle=0.0,
            )
            self.steer_frame_count += 1

            current_incidence = compute_incidence_degrees(
                vehicle.velocity_x, vehicle.velocity_y, self.target_wall
            )
            if current_incidence < SAFE_INCIDENCE_DEGREES or self.steer_frame_count >= MAX_STEER_FRAMES:
                self.phase = "idle"
            return command, True

        return player_command, False