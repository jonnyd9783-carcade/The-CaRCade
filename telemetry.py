import csv
import time
import os

class Telemetry:
    def __init__(self, folder="telemetry_runs"):
        os.makedirs(folder, exist_ok=True)
        timestamp_str = time.strftime("%Y-%m-%d_%H%M%S")
        filepath = os.path.join(folder, "run_" + timestamp_str + ".csv")

        self.file = open(filepath, "w", newline="")
        self.writer = csv.writer(self.file)
        header_row = ["timestamp", "x", "y", "heading", "velocity_x", "velocity_y", "steering_input", "throttle_input"]
        self.writer.writerow(header_row)
        print("Recording telemetry to: " + filepath)

    def record(self, vehicle_state, command):
        row = [
            time.time(),
            vehicle_state.x,
            vehicle_state.y,
            vehicle_state.heading,
            vehicle_state.velocity_x,
            vehicle_state.velocity_y,
            command.steering,
            command.throttle,
        ]
        self.writer.writerow(row)

    def close(self):
        self.file.close()