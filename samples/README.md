# Sample recordings

A small, curated set of telemetry kept as the story of Milestone 7 and as
regression fixtures. Everything else in telemetry_runs/ stays local (gitignored).
Columns are described in docs/sim-lab-handoff.md (telemetry.py entry).

| File | What it is | Numbers to expect |
|---|---|---|
| 01_original_run.csv | Live drive under brake_and_steer, with the brake sign bug present | 2193 frames, 175 intervention frames, ends at (760, 437). No deadzone columns: replay needs --steer-deadzone 0.04 --throttle-deadzone 0.045 |
| 02_replay_wrong_deadzone.csv | Same input replayed with the old fixed 0.12 deadzone | Diverges from the original at frame 46, ends at (176, 560), 200 intervention frames |
| 03_replay_before_brake_fix.csv | Same input, correct deadzones, brake bug still present | Reproduces the original exactly (175 frames, ends at (760, 437)). Only 9 braking frames, all pushing along the car's motion |
| 04_replay_after_brake_fix.csv | Same input after the brake sign fix | 51 braking frames, 50 opposing the motion. 209 intervention frames, ends at (485, 560). The path differs because the recorded input includes the driver's reactions to the old behavior (replay is open-loop) |
| 05_golden_run.csv | Recording made after the fixes, with per-frame deadzone columns | 3650 frames. Replays exactly with no flags: 422 intervention frames, ends at (760, 252). Recorded on the keyboard fallback |

Reproduce the golden check:

    python3 strategy_replay.py samples/05_golden_run.csv

Reproduce the original run exactly:

    python3 strategy_replay.py samples/01_original_run.csv --steer-deadzone 0.04 --throttle-deadzone 0.045

Files 02 to 04 are outputs of earlier versions of the code and cannot be regenerated.
