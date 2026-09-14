from dataclasses import dataclass
import math

PIXELS_PER_FOOT = 28.8  # calibrated: 720px usable arena width = 25ft real-world width
REFLEX_14_LENGTH_INCHES = 11.97  # real vehicle length, per Team Associated spec (304mm)
REFLEX_14_WIDTH_INCHES = 7.95  # real vehicle width, per Team Associated spec (202mm)
WHEELBASE_INCHES = 7.42  # confirmed real spec (188.5mm), Team Associated dealer portal, Reflex 14B RTR

# PLACEHOLDER — no published spec exists for the Reflex 14's max wheel
# throw (manufacturers rarely publish this; it's often adjustable via
# the steering rack). Estimated from typical off-road-buggy range
# (30-40°), then tuned down further by feel to avoid unrealistically
# fast spin rates when combined with TOP_SPEED. Flagged as an
# unverified assumption in fleet-hardware.md — revisit once real
# hardware can be measured directly.
MAX_STEERING_ANGLE_DEGREES = 15

WHEELBASE_PIXELS = PIXELS_PER_FOOT * (WHEELBASE_INCHES / 12)

# --- Physics tuning constants (Milestone 4) ---
ACCELERATION = 0.12   # speed gained per frame at full throttle
FRICTION = 0.02        # fraction of speed lost per frame when coasting
TOP_SPEED = 6.0        # max magnitude of speed in either direction
MOMENTUM_LAG = 0.25

# PLACEHOLDER — active braking deceleration (Milestone 7 prerequisite).
# Applied only when throttle command opposes current motion direction
# (e.g. reverse throttle while still moving forward) — mechanically
# distinct from normal acceleration in the same direction as current
# motion, or from rest. Rough starting guess (~2.5x ACCELERATION);
# tune by feel once real driving/intervention data exists.
BRAKE_DECELERATION = 0.3

# --- Arena boundary constants (Milestone 4a) ---
ARENA_MIN_X = 40
ARENA_MAX_X = 760
ARENA_MIN_Y = 40
ARENA_MAX_Y = 560


@dataclass
class VehicleState:
    x: float = 400.0
    y: float = 300.0
    heading: float = 0.0
    direction_of_travel: float = 0.0
    speed: float = 0.0
    current_steering: float = 0.0
    current_throttle: float = 0.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    def apply_input(self, steering, throttle, steering_deadzone=0.12, throttle_deadzone=0.12,
                     ramp_rate=0.15,
                     acceleration=ACCELERATION, friction=FRICTION, top_speed=TOP_SPEED,
                     brake_deceleration=BRAKE_DECELERATION,
                     momentum_lag=MOMENTUM_LAG,
                     wheelbase_pixels=WHEELBASE_PIXELS,
                     max_steering_angle_degrees=MAX_STEERING_ANGLE_DEGREES):
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

        # --- Speed: accelerates from throttle, decays from friction ---
        # Braking (Milestone 7 prerequisite): if the throttle command
        # opposes current motion direction (driver actively fighting
        # existing momentum), use the stronger BRAKE_DECELERATION
        # instead of normal ACCELERATION. Same-direction driving, or
        # starting from rest in either direction, still uses ACCELERATION
        # — this is a real mechanical distinction, not just a stronger
        # version of normal driving. No extra state needed: as speed
        # crosses zero while braking, this same sign comparison
        # naturally reverts to ACCELERATION once actually moving in the
        # new direction — brake-to-stop-then-reverse falls out for free.
        is_braking = (t > 0 and self.speed < 0) or (t < 0 and self.speed > 0)
        if is_braking:
            self.speed += t * brake_deceleration
        else:
            self.speed += t * acceleration

        self.speed -= self.speed * friction

        if self.speed > top_speed:
            self.speed = top_speed
        elif self.speed < -top_speed:
            self.speed = -top_speed

        # --- Wheelbase-aware steering (Milestone 7 prerequisite) ---
        steering_angle_degrees = s * max_steering_angle_degrees
        steering_angle_degrees = max(-max_steering_angle_degrees,
                                      min(max_steering_angle_degrees, steering_angle_degrees))

        steering_angle_rad = math.radians(steering_angle_degrees)
        effective_forward_speed = -self.speed
        angular_velocity_rad_per_frame = (effective_forward_speed * math.tan(steering_angle_rad)) / wheelbase_pixels
        self.heading += math.degrees(angular_velocity_rad_per_frame)

        # --- Velocity vector has momentum — it chases the heading-derived
        # target direction rather than snapping to it instantly ---
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