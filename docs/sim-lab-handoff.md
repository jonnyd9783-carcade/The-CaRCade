# Sim Lab — Handoff Document for Cursor

This document briefs a new Claude session (in Cursor) on the current state of this project, so it can continue implementation without rediscovering context already established. Read this in full before touching any code.

The full project charter (architecture philosophy, all milestones, amendments) is a separate document — `sim-lab-charter.md` — and should be read alongside this one. This handoff covers *current state and practical conventions*; the charter covers *the plan and the reasoning*.

---

## 1. Project Location & Environment

- Project root: `~/sim_lab` on the user's MacBook Air (macOS)
- Python 3.9.6, virtual environment at `~/sim_lab/venv`
- Standard startup: 
  ```bash
  cd ~/sim_labsource venv/bin/activatepython3 main.py

  ```
- Git repo initialized. `.gitignore` excludes `venv/`, `__pycache__/`, `*.pyc`, `telemetry_runs/`.
- The user is **not an experienced software developer**. Explain architectural decisions in plain language, work in the smallest useful increments, wait for confirmation before moving on. See charter section 27 for the full working-style contract — it applies to this handoff's continuation exactly as it did before.

## 2. Current File Structure

```
sim_lab/
├── main.py
├── replay_main.py
├── telemetry.py
├── replay.py
├── input/
│   ├── controller.py
│   ├── keyboard_controller.py
│   └── mapping.py
├── vehicle/
│   └── state.py
├── render/
│   └── view.py
├── sensors/
│   └── simulated_position.py
├── estimation/
│   └── position_estimator.py
├── telemetry_runs/       (gitignored — timestamped CSV files per run)
└── venv/                 (gitignored)

```

## 3. Current State of Each File

`vehicle/state.py` — `VehicleState` dataclass: `x`, `y`, `heading`, `direction_of_travel`, `speed`, `current_steering`, `current_throttle`, `velocity_x`, `velocity_y`. **Calibration update:** `PIXELS_PER_FOOT` changed from placeholder `20` to calibrated `28.8` (720px usable arena width = 25ft real-world width, per Jonathan's stated arena footprint — implies ~18.06ft real-world arena height as a consequence of the existing 4:3 screen aspect ratio, not an independent choice). Added `REFLEX_14_LENGTH_INCHES`/`REFLEX_14_WIDTH_INCHES` — see `fleet-hardware.md` for sourcing and confirmed real dimensions; this file just holds the pixel-conversion constants. **Milestone 4 update:** the ramp-hack has been replaced with a frame-based accel/friction/top-speed model. **Physics retune:** `ACCELERATION=0.12`, `FRICTION=0.02`, `TOP_SPEED=6.0` (up from the original `0.08`/`0.02`/`4.0`), tuned by feel; equilibrium (`ACCELERATION/FRICTION`) matches `TOP_SPEED` exactly by design, so the clamp is the real governing limit, not an unreachable ceiling. `speed` is a persistent scalar: throttle accelerates it, friction decays it each frame, clamped to `TOP_SPEED`. Velocity is derived from `speed`/`heading` but has momentum of its own (`MOMENTUM_LAG = 0.15`) — it chases the heading-derived target rather than snapping to it instantly, which lets `direction_of_travel` diverge from `heading` during turns or speed changes. `direction_of_travel` is computed via `math.atan2(velocity_x, -velocity_y)` — this specific sign combination was arrived at after two incorrect attempts and confirmed via numeric simulation against this codebase's actual heading/velocity sign convention (forward corresponds to negative `speed`, per `mapping.py`'s unmodified pass-through of `axis_1`). Still frame-based, not `dt`-based — no real-time integration yet (see deferred work below). **Milestone 4a update:** added `ARENA_MIN_X/MAX_X/MIN_Y/MAX_Y` constants (must stay manually in sync with `SCREEN_WIDTH`/`SCREEN_HEIGHT`/`ARENA_MARGIN` in `render/view.py` — tracked cross-file duplication). On any wall contact: position clamped to boundary edge, full stop (speed + both velocity components zeroed), matching the milestone's own success-criterion wording ("stops or is blocked"). Vehicle treated as a point for collision — known simplification, more visually apparent now that the vehicle renders at true scale.

`input/controller.py` — `Controller` class wrapping a pygame joystick. Currently calibrates and reads `axis_1` **(throttle) and** `axis_2` **(steering)** — remapped from the original axis_0/axis_1 scheme partway through development, per the user's preference for right-stick-steers / left-stick-throttle. `calibrate(samples=30, delay=0.01, margin=0.03)` samples resting stick values, stores `center_offset`, and **dynamically computes deadzone** from the actual measured noise (worst-case deviation from average + margin) rather than a fixed guess — this was a deliberate late-session upgrade after a fixed `0.08`/`0.12` deadzone proved insufficient for the real controller's noise floor, and directly resolved a previously-reported hands-off drift issue. `read_raw()` returns `{"axis_1": ..., "axis_2": ...}`, offset-corrected.

`input/keyboard_controller.py` — `KeyboardController` fallback. `KEY_BINDINGS` dict at the top maps action names (`throttle_up`, `throttle_down`, `steer_left`, `steer_right`) to `pygame.K_*` constants — currently arrow keys, but the user explicitly wants these editable/ergonomically remappable, so keep them in this dict, never hardcoded elsewhere. `read_raw()` returns `{"steering": ..., "throttle": ...}`.

`input/mapping.py` — `NormalizedCommand` dataclass (`steering`, `throttle`, `brake`) — the universal shape both input sources produce. `map_controller_input(raw)` reads `raw["axis_2"]` for steering, `raw["axis_1"]` for throttle (matches the remap above). `map_keyboard_input(raw)` reads `raw["steering"]`/`raw["throttle"]` directly. **Nothing downstream of this file should ever reference axis numbers or raw dict keys directly** — `main.py` only ever touches `NormalizedCommand` fields.

`render/view.py` — `View` class. `SCREEN_WIDTH=800`, `SCREEN_HEIGHT=600`, `ARENA_MARGIN=40`. `draw(vehicle_state, sensor_reading=None, estimated_state=None)` clears to black, draws the white arena boundary rectangle, draws the heading line (white) and direction-of-travel line (yellow, diverges from heading once momentum causes velocity direction to differ from heading — confirmed visually correct as of Milestone 4). **Milestone 5/6 update:** vehicle body now rendered as a rectangle rotated to heading (real length/width sourced from `fleet-hardware.md`, converted via `PIXELS_PER_FOOT`), replacing the original placeholder dot — corner-rotation math deliberately re-derived using the same sin/-cos convention already established for the heading/travel lines, specifically to avoid a repeat of the earlier `atan2` sign bug. Draws a hollow magenta circle for the simulated sensor reading (if provided) and a hollow green circle for the estimated position (if provided) — both optional parameters, default `None`.

`sensors/simulated_position.py` *(new — Milestone 5)* — `SensorReading` dataclass (`x`, `y`) + `SimulatedPositionSensor` class. Holds a reference to a `VehicleState` at construction (not a copy); `.read()` takes no arguments, reads the vehicle's current position fresh each call and adds Gaussian noise (`POSITION_NOISE_STDDEV=12`, ~12cm — see `fleet-hardware.md` for the real-UWB-accuracy sourcing and the note that no vendor/module has been chosen yet). Designed explicitly for hardware swap: a future `UWBPositionSensor` would implement the identical `read() -> SensorReading` interface, pulling from real hardware instead — `main.py` and `render/view.py` would need zero changes. Mirrors the Controller/KeyboardController → `NormalizedCommand` pattern already proven in this codebase.

`estimation/position_estimator.py` *(new — Milestone 6)* — `EstimatedState` dataclass (`x`, `y`) + `PositionEstimator` class. Implements a simple **predict-correct blended estimator**, deliberately NOT a full EKF, per charter section 13's explicit warning not to add one before a demonstrated need. Predict step advances the last estimate using `vehicle.velocity_x`/`velocity_y` (not ground-truth position) to preserve the truth/measured/estimated separation — velocity is treated as available independently of position sensing (e.g. odometry/IMU in a real system). Correct step blends that prediction with the noisy sensor reading via a tunable `correction_gain` (0–1). Same three-part swappable-interface pattern now used consistently across the whole codebase: input → sensing → estimation, each with a stable minimal interface and a swappable implementation behind it. **Confirmed via live gain testing (0.05/0.3/0.5):** behaves as a genuine trust-weighted blend, not degenerate at either extreme — even near-zero gain retains a small residual correction (a gain of exactly 0 would be pure dead-reckoning drift). **Important, explicitly-confirmed caveat:** the predict step uses this simulation's own deterministic physics — the same model that generates ground truth — so the estimator's apparent accuracy is not representative of real-hardware performance; it validates the architecture, not a real-world accuracy number. Upgrading to an EKF-style estimator should be triggered by a demonstrated accuracy gap once real UWB data exists (Milestone 10), not by the mere existence of real data.

`telemetry.py` — `Telemetry` class. On init, creates `telemetry_runs/` if needed and opens a new CSV file named `run_<YYYY-MM-DD_HHMMSS>.csv`. **Milestone 6 update:** header row extended to `timestamp, x, y, heading, direction_of_travel, velocity_x, velocity_y, steering_input, throttle_input, sensor_x, sensor_y, estimated_x, estimated_y`. `record(vehicle_state, command, sensor_reading=None, estimated_state=None)` appends one row per frame; sensor/estimate columns write blank if those arguments aren't supplied, keeping the method backward-compatible. `close()` must be called on clean exit to flush the file. **Recording does not start at program launch** — `main.py` withholds calling `record()` until the first input frame that exceeds the measured deadzone, so idle time before a driver actually touches the controls doesn't pollute the recording (and doesn't force a long wait when replaying).

`replay.py` *(new — Milestone 3)* — `Replay` class. On init, reads an entire telemetry CSV into memory via `csv.DictReader` (rows come back as string-valued dicts — not auto-converted to numbers). `has_next()` / `next_frame()` step through the rows one at a time.

`replay_main.py` *(new — Milestone 3)* — standalone entry point, separate from `main.py`, taking a CSV filepath as a command-line argument (`python3 replay_main.py telemetry_runs/run_....csv`). Validates the file exists first and prints a friendly message (not a raw traceback) if it doesn't. Each frame, pulls the next row from `Replay`, converts `x`/`y`/`heading` to floats, and feeds them directly into the same `View.draw()` used for live driving — completely bypassing the controller, `KeyboardController`, and `vehicle.apply_input()`. Currently plays back at a flat 60fps, one row per frame — it does **not** yet honor the CSV's recorded `timestamp` values for real-time-accurate pacing (a known, accepted simplification, not a bug). **Milestone 6 update:** also reconstructs `SensorReading`/`EstimatedState` objects from the CSV's sensor/estimate columns and restores `direction_of_travel`, passing all three into `View.draw()` so replay reproduces the full live picture (truth, noise, estimate, travel line) — not just position/heading. Gracefully falls back to `None`/matching-heading for older recordings that predate these columns, so pre-Milestone-6 runs still replay without crashing, just without the new markers.

`main.py` — Orchestrates live driving (not replay — that's `replay_main.py`, a separate entry point). On startup: waits up to 10 seconds for a controller; if found, calibrates it and reads its measured deadzone values; if not found after 10 seconds, falls back to `KeyboardController`. The arena is drawn during this wait so the window isn't blank. Main loop: polls events, checks for the Start button (button 8) to trigger mid-session recalibration, reads input → maps to `NormalizedCommand` → applies to vehicle → records telemetry (only once recording has actually started — see `telemetry.py` above) → draws → ticks the clock at 60fps (`pygame.time.Clock`, critical for smooth, non-lurching motion). Calls `telemetry.close()` before exit.

## 4. Hardware: Confirmed Controller Mapping (8BitDo SN30 Pro)

**Critical finding: use a wired USB-C connection, not Bluetooth.** Bluetooth pairing (in the mode that registers as "Nintendo Switch Pro Controller" to pygame/SDL) technically works and axes read correctly, but button detection was **intermittently unreliable** over Bluetooth across many test attempts — the exact same test script that reliably caught all 20 buttons over USB-C repeatedly failed to detect some or all buttons over Bluetooth, with no code difference. This was never fully root-caused; wired was adopted as the practical fix and has been reliable in every subsequent session. **Do not attempt to "fix" this and move back to Bluetooth without a very good reason and the user's buy-in** — it cost significant time to work around originally.

Detected as: `Nintendo Switch Pro Controller` (6 axes, 20 buttons, 0 hats — D-pad reports as buttons, not a hat/POV switch).

**Axis map (confirmed, tested twice via isolated one-at-a-time scripts):**


| Axis | Control                    | Notes                                                  |
| ---- | -------------------------- | ------------------------------------------------------ |
| 0    | Left stick horizontal      | unused (was originally steering; remapped — see below) |
| 1    | Left stick vertical        | **currently used: throttle**                           |
| 2    | Right stick horizontal     | **currently used: steering**                           |
| 3    | Right stick vertical       | unused                                                 |
| 4    | Left trigger (ZL), analog  | resting 0.0, pressed -1.0                              |
| 5    | Right trigger (ZR), analog | resting 0.0, pressed -1.0                              |


**This is the current, active mapping — not a historical note.** The user deliberately requested right stick for steering / left stick for throttle partway through development (a shift from the original left-stick-does-both scheme), and `input/controller.py` and `input/mapping.py` were both updated accordingly. Do not "fix" this back to axis_0/axis_1 — that would undo an intentional change.

**Button map (confirmed via ordered test sweep):**


| Button # | Control                                          |
| -------- | ------------------------------------------------ |
| 0        | A                                                |
| 1        | B                                                |
| 2        | X                                                |
| 3        | Y                                                |
| 4        | ZL (digital)                                     |
| 6        | ZR (digital)                                     |
| 9        | L (left shoulder)                                |
| 10       | R (right shoulder)                               |
| 7        | Select / −                                       |
| 8        | Start / + (**currently bound to recalibration**) |
| 11       | Left stick click                                 |
| 12       | Right stick click                                |
| 13       | D-pad UP                                         |
| 14       | D-pad DOWN                                       |


D-pad LEFT/RIGHT were never conclusively isolated (didn't register as distinct button numbers in testing) — low priority, not currently used by anything.

## 5. Cursor-Specific Gotcha: Paste Truncation

Across sessions, pasting full-file replacements into Cursor's editor **repeatedly and silently truncated multi-line code** — cutting off function bodies mid-statement, sometimes leaving a syntactically broken file, sometimes (worse) leaving a *syntactically valid but incomplete* method (e.g., a function that silently did nothing after its first line, with no error at all — this caused a confusing "nothing moves" bug that took real time to trace back to a truncated paste rather than a logic error).

**Likely root cause identified late in the process:** doing select-all → delete → paste too quickly in succession, without letting Cursor's editor state catch up between each step.

**Practical mitigations already adopted, worth continuing:**

- Prefer flatter code (avoid deeply nested multi-line function calls; break complex expressions into intermediate variables) — simpler paste payloads truncate less often
- After any full-file paste, scroll to confirm the **last line** of the intended file is actually present before saving
- Pace out select-all / delete / paste as distinct, unhurried actions rather than firing them rapidly

If continuing to work interactively with the user via chat-and-paste (rather than Cursor's own agent editing files directly), continue applying these mitigations.

## 6. Deliberately Deferred Work (Do Not Build Prematurely)

- **Direction-of-travel line:** DONE as of Milestone 4 (previously listed as deferred to Milestone 4). See updated `vehicle/state.py` / `render/view.py` entries in section 3 above.
- **Wheelbase-aware steering model:** raised during Milestone 4 physics discussion. Real future need identified (Milestone 7 avoidance maneuvers need realistic turning geometry, not just direct heading-rotation), but deliberately deferred — no current system (no collision, no safety intervention yet) to validate it against. Build this immediately before Milestone 7 work begins, not before.
- **Frame-based physics, no** `dt`**:** Milestone 4's physics model deliberately stayed per-frame (assumes fixed 60fps), matching the existing convention (replay is also flat 60fps). Introducing real delta-time integration was consciously deferred rather than bundled into the same change as accel/friction — treat as its own future step if/when decoupling from fixed 60fps becomes necessary.
- **Event-queue-based button handling** (`JOYBUTTONDOWN`/`JOYBUTTONUP`) for a future safety arm/disarm toggle, as opposed to the current state-polling approach: flagged as worth considering, but explicitly deferred to Milestone 7 (Safety Experiments), when an actual arm/disarm toggle will exist to make the distinction matter. Current polling approach is fine for everything built so far.
- **Consolidated tunable-parameter reference table** (charter section 12a): a good future idea for centralizing `speed`, `ramp_rate`, deadzone values, etc. into one config location — explicitly **not to be built yet**, since only a handful of scattered constants currently exist and don't yet warrant the overhead.
- **Torque-vectoring / per-wheel torque control** as a safety-intervention strategy: explicitly ruled out for the foreseeable future. See `fleet-hardware.md` for the real vehicle platform's drivetrain constraints. Safety intervention strategies should assume brake-impulse + timed-steering only, unless simulation testing conclusively proves that approach insufficient.
- **Radius/shape-aware boundary collision** (Milestone 4a): currently point-based, ignoring the vehicle's rendered footprint. More visually noticeable now that the vehicle renders at true scale (Milestone 5). Not worth the added complexity yet — the visual overlap is minor.
- `dt`**/timestamp-aware prediction in the estimator** (Milestone 6): `PositionEstimator.update()` currently takes raw per-frame `velocity_x`/`velocity_y` with no explicit `dt` — fine only because the whole system is still frame-based. Tied to the same still-deferred move off frame-based physics above, not a new, separate deferral.
- **EKF upgrade trigger** (Milestone 6): explicitly NOT triggered by "real UWB data exists" alone — must be a demonstrated accuracy gap between the cheap estimator and real hardware (Milestone 10), per charter section 13.

## 7. Milestone Status (see charter section 29 + amendments for full detail)


| Milestone                  | Status                                                                                                                                                                                                                                                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0 — First Contact          | ✅ Done. Controller (or keyboard fallback) drives a dot smoothly around the arena.                                                                                                                                                                                                                                 |
| 1 — Vehicle Representation | Foundation done: real `heading`, orientation line, velocity tracking (`velocity_x`/`velocity_y`), `PIXELS_PER_FOOT` constant in place. Direction-of-travel line built and confirmed correct as of Milestone 4 (see section 6 above).                                                                              |
| 2 — Telemetry              | ✅ Done. CSV recording confirmed working with real driving data; per-run timestamped files; recording now correctly withheld until the first real input (fixed a bug where idle time before driving was captured).                                                                                                 |
| 3 — Replay                 | ✅ Done. `replay.py` + `replay_main.py` load a recorded telemetry CSV and reproduce that run deterministically, without the controller connected — confirmed against multiple real recorded runs, including one exercised through the keyboard fallback. Friendly error handling added for a missing/bad filepath. |
| 4 — Basic Physics          | ✅ Done. Accel/friction/top-speed model, tested and tuned by feel. Direction-of-travel line built and confirmed correct (see section 6).                                                                                                                                                                           |
| 4a — Boundary Collision    | ✅ Done. Point-based collision, full stop on contact with any wall. Tested against all four walls and corners.                                                                                                                                                                                                     |
| 5 — Sensor Simulation      | ✅ Done for position noise. Simulated Gaussian noise on position, controllable amount via `POSITION_NOISE_STDDEV`. Swappable-interface design for future real UWB hardware.                                                                                                                                        |
| 6 — State Estimation       | ✅ Done, first pass. Simple predict-correct blended estimator (not an EKF). Estimated state confirmed comparable against known simulation truth, both live and in reproducible recorded/replayed form.                                                                                                             |
| 7–10                       | Not started. See charter for full detail on each. Wheelbase-aware steering (see section 6 above) is a prerequisite for Milestone 7.                                                                                                                                                                               |


## 8. Immediate Next Task: Wheelbase-Aware Steering (Milestone 7 Prerequisite)

Milestones 4a, 5, and 6 are done. The next concrete gap before Milestone 7 (Safety Experiments) can begin is wheelbase-aware steering — flagged since Milestone 4 as a real future need (avoidance maneuvers need realistic turning geometry, not direct heading-rotation) but deliberately deferred until there was a concrete system to validate it against. That system (collision, Milestone 4a) now exists.

**Context worth knowing before starting:** current steering rotates `heading` directly and uniformly, regardless of speed — no turning radius, no wheelbase geometry. See charter section 12/28 and section 6 above for the original deferral reasoning.

Follow the same incremental, explain-then-implement working style used throughout this project so far (charter section 27). Do not jump ahead to Milestone 7 itself without the user's explicit go-ahead.