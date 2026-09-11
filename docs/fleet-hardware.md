# Fleet / Hardware

## Vehicle Platform

**Team Associated Reflex 14** — 1/14 scale, 4WD, three passive mechanical differentials, single motor/ESC. No per-wheel torque control on stock hardware.

**Confirmed real dimensions** (Team Associated official spec): length 304mm / 11.97in, width 202mm / 7.95in, wheelbase 188.5mm / 7.42in (Reflex 14B RTR, via Team Associated's official dealer portal spec page).

**Safety-intervention hypothesis, confirmed compatible with stock drivetrain:** brake-impulse to load the front tires, followed by a timed steering input to rotate away from rigid barriers. Per-wheel torque vectoring is explicitly ruled out for the foreseeable future — the stock drivetrain has no hardware path to it. Safety-intervention strategies (Milestone 7+) should assume brake+steer only, unless simulation testing conclusively proves that approach insufficient.

## Active Assumptions — Not Yet Verified Against Real Hardware

These are currently load-bearing in Sim Lab's code but have **not** been confirmed against physical measurement or a chosen vendor. Flagging explicitly so a future decision doesn't accidentally treat these as settled fact.

- **Simulated arena footprint: 25ft wide.** Given by Jonathan specifically to calibrate `PIXELS_PER_FOOT` in Sim Lab (→ `PIXELS_PER_FOOT = 28.8`). This is a **simulation-calibration input**, not a confirmed spec for the actual Phase 2 physical prototype arena (rc-arena-vision.md's ~$1,000-budget arena) or any later venue.
- **Implied simulated arena height: ~18.06ft.** Not independently chosen — a pure consequence of the 25ft-width assumption combined with the simulator's 800×600 (4:3) window, which was itself an arbitrary early technical choice (Milestone 0), not a real-world-driven decision.
- **Simulated position sensor noise: `POSITION_NOISE_STDDEV = 12` (~12cm).** Based on commonly cited real-world UWB accuracy literature (10–30cm typical range), **not** tied to any specific chosen UWB vendor or module — no hardware has been selected yet. Revisit once one is.
- **Boundary collision treats the vehicle as a single point**, ignoring its real footprint — a known simplification in Sim Lab's Milestone 4a work, more visually apparent now that the vehicle renders at true scale.
- **Max steering angle: `MAX_STEERING_ANGLE_DEGREES = 15` (degrees each direction).** No published spec exists for the Reflex 14's actual wheel throw — manufacturers rarely publish this, and it's often adjustable via the steering rack/turnbuckles. Initially estimated at 30–40° (typical off-road-buggy hobbyist range) but tuned down significantly after testing showed unrealistically fast spin rates when combined with `TOP_SPEED` — a reminder that this value is doing double duty as both a geometric assumption and a feel-tuning knob, not a verified fact. Revisit once real hardware can be measured directly.

No UWB vendor/module has been selected. This is the single highest-leverage open item — it affects position-noise accuracy, and eventually real-world calibration (Milestone 10) directly.
