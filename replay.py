import csv

class Replay:
    def __init__(self, filepath):
        self.rows = []
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.rows.append(row)
        self.index = 0

    def has_next(self):
        return self.index < len(self.rows)

    def next_frame(self):
        row = self.rows[self.index]
        self.index += 1
        return row