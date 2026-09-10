# The CaRCade — Sim Lab

> A scrappy Python/Pygame sim lab where a tiny virtual RC car learns real physics, gets haunted by noisy GPS-ghost readings, and slowly grows a state estimator to see through the fog. All in service of a real driver-assist safety system, before any real car gets hurt. 🏎️💨

## What this is

This is the simulation-first testbed behind **The CaRCade** — a physical multiplayer gaming platform where teams drive intelligent RC vehicles inside an instrumented arena. Before any physical hardware gets built, the driver-assistance safety system is designed, tested, and validated here, in a simple 2D Pygame simulator.

The guiding philosophy: **think small, act fast.** Every capability is built as the smallest possible step that answers a real question — no speculative features, no premature complexity. Full architectural reasoning lives in the project's charter and handoff docs (see `docs/` if included).

## Status

Development proceeds in incremental milestones. As of the latest commit:


| Milestone                                      | Status    |
| ---------------------------------------------- | --------- |
| 0 — Controller input, moving dot               | ✅ Done    |
| 1 — Vehicle representation (heading, velocity) | ✅ Done    |
| 2 — Telemetry recording                        | ✅ Done    |
| 3 — Replay                                     | ✅ Done    |
| 4 — Basic physics (accel/friction/momentum)    | ✅ Done    |
| 4a — Boundary collision                        | ✅ Done    |
| 5 — Simulated sensor noise                     | ✅ Done    |
| 6 — State estimation (predict-correct)         | ✅ Done    |
| 7 — Safety experiments                         | ⏳ Next up |


## Tech stack

- Python 3.9
- [Pygame](https://www.pygame.org/) for the 2D visualization loop
- 8BitDo Bluetooth/USB-C controller for input, with automatic keyboard fallback
- No external physics/ML dependencies — everything is built from first principles to stay simple, tunable, and easy to reason about

## Architecture

The codebase is organized so that real hardware can eventually swap in for simulated pieces with minimal disruption:

```
Controller/Keyboard → Input Mapping → NormalizedCommand → Vehicle Model
Vehicle Model (truth) → Simulated Sensor → SensorReading → Estimator → EstimatedState
```

Each stage exposes a small, stable interface (`read()`, `apply_input()`, `update()`) so a simulated piece — like `SimulatedPositionSensor` — can later be replaced by a real hardware equivalent (e.g. a UWB localization reader) without touching anything downstream.

```
sim_lab/
├── main.py                        # live driving entry point
├── replay_main.py                 # deterministic replay of a recorded run
├── telemetry.py                   # CSV recording
├── replay.py                      # CSV playback
├── input/                         # controller + keyboard input, normalized
├── vehicle/                       # ground-truth physics model
├── render/                        # Pygame visualization (a window into the sim, not its core)
├── sensors/                       # simulated position sensor (noise model)
├── estimation/                    # predict-correct position estimator
└── telemetry_runs/                # recorded runs (gitignored)
```

## Running it

bash

```bash
cd sim_lab
python3 -m venv venv
source venv/bin/activate
pip install pygame
python3 main.py
```

Connect a controller before launch, or just wait — after 10 seconds with no controller detected, it falls back to keyboard control automatically (arrow keys).

### Replaying a recorded run

bash

```bash
python3 replay_main.py telemetry_runs/run_<timestamp>.csv
```

Reproduces a prior run deterministically — ground truth, simulated sensor noise, and the estimator's output all replay together, without needing the controller connected.

## Design notes worth knowing

- **Simulation truth vs. measurement vs. estimate are always kept separate** — the codebase never collapses "what actually happened" with "what a noisy sensor reported" or "what the estimator believes," even though today all three live in the same simulation.
- **The current state estimator is a simple predict-correct blend, not a Kalman filter** — built deliberately simple first, per the rule: don't reach for more sophisticated estimation until a real, demonstrated need justifies it.
- **Physics is frame-based (fixed 60fps), not delta-time integrated** — a known, deliberate simplification, flagged for revisit if the system ever needs to run at a variable frame rate.

## License

Private project — not currently licensed for reuse.