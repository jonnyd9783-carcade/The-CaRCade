# Translates raw controller input into normalized commands
# the vehicle model can understand. Nothing here knows
# anything about pygame or hardware specifics.

from dataclasses import dataclass

@dataclass
class NormalizedCommand:
    steering: float = 0.0   # -1.0 (full left) to 1.0 (full right)
    throttle: float = 0.0   # 0.0 to 1.0
    brake: float = 0.0      # 0.0 to 1.0