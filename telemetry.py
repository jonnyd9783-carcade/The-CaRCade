import csv
import time

class Telemetry:
    def __init__(self, filepath):
        self.file = open(filepath, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "timestamp", "x", "y", "heading",
            "velocity_x", "velocity_y",
            "steering_input", "throttle_input"
        ])

    def record(self, vehicle_state, command):
        self.writer.writerow([
            time.time(),
            vehicle_state.x,
            vehicle_state.y,
            vehicle_state.heading,
            vehicle_state.velocity_x,
            vehicle_state.velocity_y,
            command.steering,
            command.throttle,
        ])

    def close(self):
        self.file.close()