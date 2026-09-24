"""
safety/head_on_only.py

Milestone 7 — second safety strategy, for genuine comparison against
safety/intervention.py's brake-then-steer sequence.

Deliberately different design philosophy: two fully INDEPENDENT,
live-gated triggers (not a sequenced state machine):

- Steering: active only while incidence angle indicates a fairly
  head-on approach AND within STEER_TRIGGER_MAX_TTC_FRAMES. Uses this
  codebase's existing incidence convention (measured from the wall's
  surface, 90=head-on, 0=glancing) — the standard "angle of incidence"
  (measured from the wall's normal) threshold of 45 degrees translates
  to our_incidence > 45 to trigger. Ends the instant incidence drops
  back to 45 or below (recomputed live every frame, no phase/duration
  to complete).

- Braking: active only as a last-resort emergency response, when raw
  TTC drops below EMERGENCY_BRAKE_TTC_FRAMES. Fully decoupled from the
  steering trigger — can fire independently, or alongside steering in
  a severe case.

Bug found via live testing: as originally built, steering had NO
distance/TTC gate at all — only the angle check plus
check_boundary_ttc's generic MAX_RELEVANT_TTC_FRAMES=90 ceiling (which
exists for STRATEGY 1's needs, not this one). At full speed that meant
steering could trigger ~18.8ft from the wall, nearly the width of the
entire arena — way too early. STEER_TRIGGER_MAX_TTC_FRAMES is a new,
dedicated, much tighter gate for THIS strategy specifically, kept
separate from collision_check.py's shared constant so strategy 1's
behavior stays completely unaffected — keeps the two strategies
properly independent and separately tunable.

Each axis only overrides itself when its own condition is active;
otherwise the player's own input passes through untouched on that
axis. No player-match or speed-based early-exit logic here (unlike
intervention.py) — this strategy is inherently self-releasing, since
both conditions are re-evaluated fresh every single frame rather than
committing to a multi-frame maneuver.

`self.status` mirrors intervention.py's `status` property under the
same shared name, so main.py (and telemetry) can report what any
strategy is doing without needing to know its internal structure. Since
this strategy has no phases, status just reflects which trigger(s), if
any, are currently active this frame.

Reuses check_boundary_ttc() purely for its raw geometry output (wall,
distance, raw_ttc, incidence) — deliberately ignores its
"would_intervene" field, which reflects STRATEGY 1's own timing logic,
not this strategy's independent thresholds.
"""

from dataclasses import dataclass
from safety.collision_check import check_boundary_ttc
from safety.steering_geometry import choose_steer_sign

HEAD_ON_THRESHOLD_DEGREES = 45      # our convention (measured from wall surface); >45 = within 45deg of head-on
STEER_TRIGGER_MAX_TTC_FRAMES = 30    # placeholder — dedicated, tighter gate than collision_check's generic 90-frame ceiling
EMERGENCY_BRAKE_TTC_FRAMES = 6        # last-resort only — about 100ms at 60fps
EMERGENCY_BRAKE_MAGNITUDE = 1.0       # full strength, given how late this fires
STEER_MAGNITUDE = 1.0                 # full lock; tune down if it feels too aggressive


@dataclass
class InterventionCommand:
    steering: float = 0.0
    throttle: float = 0.0


class HeadOnOnlyIntervention:
    def __init__(self):
        self.steer_sign = 0
        self.status = "idle"

    def update(self, vehicle, player_command):
        check = check_boundary_ttc(vehicle)

        steering_active = False
        braking_active = False

        if check is not None:
            if check["incidence_degrees"] > HEAD_ON_THRESHOLD_DEGREES and check["raw_ttc_frames"] < STEER_TRIGGER_MAX_TTC_FRAMES:
                steering_active = True
                self.steer_sign = choose_steer_sign(vehicle)
            if check["raw_ttc_frames"] < EMERGENCY_BRAKE_TTC_FRAMES:
                braking_active = True

        if steering_active and braking_active:
            self.status = "steering+braking"
        elif steering_active:
            self.status = "steering"
        elif braking_active:
            self.status = "braking"
        else:
            self.status = "idle"

        if not steering_active and not braking_active:
            return player_command, False

        final_steering = self.steer_sign * STEER_MAGNITUDE if steering_active else player_command.steering

        if braking_active:
            brake_sign = -1 if vehicle.speed < 0 else 1
            final_throttle = brake_sign * EMERGENCY_BRAKE_MAGNITUDE
        else:
            final_throttle = player_command.throttle

        return InterventionCommand(steering=final_steering, throttle=final_throttle), True