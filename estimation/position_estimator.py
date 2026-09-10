"""
estimation/position_estimator.py

Milestone 6 (State Estimation) — first pass, deliberately NOT a full EKF,
per the charter's explicit warning not to reach for one before a
demonstrated need exists.

Implements a simple predict-correct blended estimator:
  - Predict: advance the last estimate using the vehicle's own velocity,
    treated as available independently of position sensing (e.g. via
    commanded motion or IMU/odometry in a real system) — NOT via ground
    truth position, preserving the truth/measured/estimated separation.
  - Correct: blend that prediction with the noisy position measurement,
    weighted by correction_gain.

Important caveat: in this simulation, the "predict" step uses the exact
same deterministic physics that generates ground truth. This estimator
will look better here than it would against a real vehicle with real
unmodeled disturbance (motor variance, wheel slip, drift). This
experiment validates the architecture, not a proven real-world accuracy
number.
"""

from dataclasses import dataclass


@dataclass
class EstimatedState:
    x: float = 0.0
    y: float = 0.0


class PositionEstimator:
    def __init__(self, initial_x, initial_y, correction_gain=0.05):
        self.estimate = EstimatedState(x=initial_x, y=initial_y)
        self.correction_gain = correction_gain

    def update(self, velocity_x, velocity_y, measured_x, measured_y):
        predicted_x = self.estimate.x + velocity_x
        predicted_y = self.estimate.y + velocity_y

        corrected_x = predicted_x + self.correction_gain * (measured_x - predicted_x)
        corrected_y = predicted_y + self.correction_gain * (measured_y - predicted_y)

        self.estimate = EstimatedState(x=corrected_x, y=corrected_y)
        return self.estimate