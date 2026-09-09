from dataclasses import dataclass
import math

PIXELS_PER_FOOT = 28.8  # calibrated: 720px usable arena width = 25ft real-world width
REFLEX_14_LENGTH_INCHES = 11.97  # real vehicle length, per Team Associated spec (304mm)
REFLEX_14_WIDTH_INCHES = 7.95  # real vehicle width, per Team Associated spec (202mm)

# --- Physics tuning constants (Milestone 4) ---
# Per-frame constants, tuned assuming a fixed 60fps tick (matches the rest
# of the system — no dt/real-time integration yet). Plain module-level
# constants for now; per charter section 12a these get consolidated into a
# config table later, once there are enough of them to justify it.
ACCELERATION = 0.08   # speed gained per frame at full throttle
FRICTION = 0.02        # fraction of speed lost per frame when coasting
TOP_SPEED = 4.0        # max magnitude of speed in either direction

# How quickly the velocity vector "catches up" to heading each frame.
# 1.0 = velocity snaps instantly to heading (old behavior, no momentum).
# Lower values = more lag/drift — direction of travel visibly trails heading
# during sharp turns or speed changes. This is what makes the direction-of-
# travel line meaningfully different from the orientation line.
MOMENTUM_LAG = 0.15

# --- Arena boundary constants (Milestone 4a) ---
# These MUST currently match render/view.py's SCREEN_WIDTH, SCREEN_HEIGHT,
# and ARENA_MARGIN by hand — there is no shared config yet. If the arena
# size ever changes in view.py, these need to be updated here too. This
# duplication is a known, deliberate simplification; a good candidate for
# the deferred consolidated config table (section 12a), not worth solving
# now for a single set of four numbers.
ARENA_MIN_X = 40
ARENA_MAX_X = 760
ARENA_MIN_Y = 40
ARENA_MAX_Y = 560


@dataclass
class VehicleState:
    x: float = 400.0
    y: float = 300.0
    heading: float = 0.0
    direction_of_travel: float = 0.0  # angle of actual velocity vector, degrees
    speed: float = 0.0
    current_steering: float = 0.0
    current_throttle: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    def apply_input(self, steering, throttle, steering_deadzone=0.12, throttle_deadzone=0.12,
                     ramp_rate=0.15, turn_rate=3.0,
                     acceleration=ACCELERATION, friction=FRICTION, top_speed=TOP_SPEED,
                     momentum_lag=MOMENTUM_LAG):
        if abs(steering) < steering_deadzone:
            steering = 0.0
        if abs(throttle) < throttle_deadzone:
            throttle = 0.0

        self.current_steering += (steering - self.current_steering) * ramp_rate
        self.current_throttle += (throttle - self.current_throttle) * ramp_rate

        s = self.current_steering
        t = self.current_throttle
        s = (s ** 2) * (1 if s >= 0 else -1)
        t = (t ** 2) * (1 if t >= 0 else -1)

        self.heading += s * turn_rate

        self.speed += t * acceleration
        self.speed -= self.speed * friction

        if self.speed > top_speed:
            self.speed = top_speed
        elif self.speed < -top_speed:
            self.speed = -top_speed

        heading_rad = math.radians(self.heading)
        target_velocity_x = -math.sin(heading_rad) * self.speed
        target_velocity_y = math.cos(heading_rad) * self.speed

        self.velocity_x += (target_velocity_x - self.velocity_x) * momentum_lag
        self.velocity_y += (target_velocity_y - self.velocity_y) * momentum_lag

        if self.velocity_x != 0.0 or self.velocity_y != 0.0:
            self.direction_of_travel = math.degrees(
                math.atan2(self.velocity_x, -self.velocity_y)
            )

        self.x += self.velocity_x
        self.y += self.velocity_y

        hit_wall = False

        if self.x < ARENA_MIN_X:
            self.x = ARENA_MIN_X
            hit_wall = True
        elif self.x > ARENA_MAX_X:
            self.x = ARENA_MAX_X
            hit_wall = True

        if self.y < ARENA_MIN_Y:
            self.y = ARENA_MIN_Y
            hit_wall = True
        elif self.y > ARENA_MAX_Y:
            self.y = ARENA_MAX_Y
            hit_wall = True

        if hit_wall:
            self.speed = 0.0
            self.velocity_x = 0.0
            self.velocity_y = 0.0