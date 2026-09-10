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
        header_row = [
            "timestamp", "x", "y", "heading", "direction_of_travel",
            "velocity_x", "velocity_y",
            "steering_input", "throttle_input",
            "sensor_x", "sensor_y", "estimated_x", "estimated_y",
        ]
        self.writer.writerow(header_row)
        print("Recording telemetry to: " + filepath)

    def record(self, vehicle_state, command, sensor_reading=None, estimated_state=None):
        row = [
            time.time(),
            vehicle_state.x,
            vehicle_state.y,
            vehicle_state.heading,
            vehicle_state.direction_of_travel,
            vehicle_state.velocity_x,
            vehicle_state.velocity_y,
            command.steering,
            command.throttle,
            sensor_reading.x if sensor_reading is not None else "",
            sensor_reading.y if sensor_reading is not None else "",
            estimated_state.x if estimated_state is not None else "",
            estimated_state.y if estimated_state is not None else "",
        ]
        self.writer.writerow(row)

    def close(self):
        self.file.close()