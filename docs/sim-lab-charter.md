# Simulation Lab — Development Charter and Initial Build Specification

## 1. Purpose

I am building a simulation laboratory that will begin as a deliberately simple 2D environment and eventually grow into a sophisticated vehicle simulation, telemetry, state-estimation, safety-system, scenario-testing, and game-development platform.

The initial system should be extremely simple:

Connect an 8BitDo Bluetooth controller to a MacBook, display a black rectangular arena, and allow the controller to move a simple vehicle representation around that space.

However, I do not want the initial prototype to be disposable code.

I want the first version to establish a clean architecture that can grow through additional layers without repeatedly requiring the underlying system to be rewritten.

The philosophy is:

Start simple. Preserve structure. Add capability incrementally. Measure everything. Make experiments reproducible.

Your role is to guide me through this process, not simply generate large amounts of code.

I am not an experienced software developer. Explain important architectural decisions in plain language, help me understand what we are building, and work incrementally.

---

## 2. Development Philosophy

The project should be developed as an experimental laboratory rather than as a conventional application.

Every significant capability should be introduced as a layer.

The intended progression is approximately:

1. Controller input
2. Basic visualization
3. Vehicle state
4. Telemetry recording
5. Replay
6. Basic vehicle motion
7. Parameterized vehicle model
8. Simulated localization
9. Sensor noise
10. State estimation
11. Safety prediction
12. Safety intervention strategies
13. Scenario generation
14. Scenario replay
15. Ruleset comparison
16. Regression testing
17. Real-world telemetry ingestion
18. Simulation-versus-reality comparison
19. Continuous calibration
20. Operational data debrief and test generation

Do not implement future layers merely because they are mentioned here.

Instead, preserve architectural interfaces that make those future layers possible.

---

## 3. First Principle: Do Not Overbuild the First Version

The first milestone should be almost embarrassingly simple.

The first successful experiment should be:

8BitDo controller → input layer → moving object → black rectangular arena

The first version does not need:

- realistic physics
- UWB
- EKF
- collision prediction
- safety intervention
- networking
- 3D graphics
- sophisticated vehicle dynamics
- AI
- scenario generation
- databases
- fleet management

Those come later.

The objective of the first milestone is to establish a functioning laboratory that I can interact with.

Once it works, stop and let me experiment with it before adding major complexity.

---

## 4. Development Environment

The initial target platform is:

- MacBook Air
- macOS
- Bluetooth 8BitDo controller
- Python-based development is preferred initially
- A simple 2D visualization framework such as Pygame is appropriate unless there is a compelling reason to choose something else.

Do not introduce unnecessary dependencies.

Before installing anything, explain what it is for.

---

## 5. Initial Visualization

The initial screen should be deliberately minimal:

- black background
- white rectangular boundary representing the physical arena
- simple vehicle representation inside the rectangle
- no decorative graphics

The vehicle should eventually be represented by:

- a dot representing the approximate center of mass
- an orientation line passing through the dot
- a direction-of-travel line passing through the dot
- the two lines should intersect at the vehicle's center/dot

The distinction between:

vehicle orientation

and

actual direction of travel

is important and should remain explicit in the data model.

**Amendment (post-Milestone 1):** The orientation line (heading) was built and confirmed working in Milestone 1. The direction-of-travel line was deliberately deferred rather than built alongside it: until yaw/slip physics exists (Milestone 4), heading and direction of travel are mathematically identical, so a second line would have nothing distinct to show — drawing it now would not actually satisfy the "visually distinguish" goal, only appear to. The direction-of-travel line should be built once Milestone 4's physics can make it diverge from heading, and revisited sooner only if something concrete arises that calls for it before then (e.g. an early experiment that needs to visualize slip).

---

## 6. Controller Input

The initial controller should be an 8BitDo Bluetooth controller.

The input layer should be designed so that the physical controller is not tightly coupled to the vehicle model.

The system should conceptually have:

Controller → Input Mapping → Normalized Commands → Vehicle Model

This will eventually allow another controller or an automated test input to replace the physical controller without rewriting the vehicle system.

Controller inputs should eventually be represented in normalized terms such as:

- steering
- throttle
- brake
- buttons
- timestamp

The mapping should be configurable rather than buried throughout the code.

### 6a. Keyboard Fallback Input

If no game controller is detected within 10 seconds of launch, the system should automatically fall back to keyboard input rather than failing or blocking startup.

Arrow keys should map to steering and throttle (up/down for throttle, left/right for steering), with additional keys mapped for other functions (buttons, pause, etc.) as those needs arise.

This fallback must sit behind the same Input Mapping abstraction described above — the vehicle model and everything downstream should have no awareness of whether input originated from a physical controller or a keyboard. The only place that should know the difference is the input layer itself.

The purpose of this fallback is resilience, not a secondary primary input method: the physical controller remains the intended way to interact with the simulator, and the keyboard exists so development and testing are never blocked by a controller pairing, detection, or hardware issue.

---

## 7. Vehicle State

Even though the first vehicle is just a dot, establish a structured vehicle state.

At minimum, anticipate fields for:

- timestamp
- x position
- y position
- velocity x
- velocity y
- speed
- heading
- angular velocity
- acceleration
- steering input
- throttle input
- brake input

Also distinguish between:

ground truth state

and eventually:

estimated state

and:

measured/sensor state

Do not collapse these concepts into one set of variables.

The simulator will eventually need to know the difference between what actually happened and what the vehicle's sensors think happened.

---

## 8. Telemetry Architecture

Telemetry is a core requirement, not an afterthought.

Every simulation step should eventually be capable of producing a structured telemetry record.

The system should use a consistent timestamp and data schema.

Initially, telemetry can be written to a simple format such as CSV or JSONL.

The exact storage mechanism can evolve later.

The important requirement is that the system produces records that can eventually be replayed.

For example:

timestamp, vehicle_id, x, y, velocity_x, velocity_y, speed, heading, angular_velocity, acceleration, steering_input, throttle_input, brake_input

Do not invent unnecessary fields merely because they might someday be useful.

However, design the telemetry system so additional fields can be added without destroying compatibility with existing recordings.

---

## 9. Simulation Truth vs. Sensors

This distinction is extremely important.

The simulator should eventually maintain a "truth" state.

It may then generate simulated sensor measurements from that truth.

For example:

Truth: x = 4.21, y = 7.82, velocity = 3.6 m/s, heading = 41°

A simulated UWB system might produce: x = 4.25, y = 7.77

because of simulated measurement noise.

Later, an estimator such as an EKF can use those noisy measurements to estimate the actual state.

This architecture allows us to evaluate the estimator because we know the underlying truth.

---

## 10. Replay Is a First-Class Capability

Once telemetry recording exists, implement replay before adding too much complexity.

The system should eventually be able to:

1. Record a run.
2. Save it.
3. Load it later.
4. Replay it deterministically.
5. Visualize the replay.
6. Analyze the telemetry.

A recorded scenario should not depend on the original controller being connected.

This is important because recorded runs will eventually become test cases.

---

## 11. Reproducible Scenarios

The simulator should eventually support repeatable scenarios.

A scenario should describe initial conditions and relevant environmental conditions.

Examples:

- vehicle starting position
- initial velocity
- initial heading
- boundary geometry
- surface characteristics
- simulated sensor noise
- nearby vehicle states
- player input stream

A scenario should be reproducible.

If the same scenario is run twice with the same ruleset and deterministic settings, the result should be comparable.

Randomness should therefore be controllable with explicit random seeds where appropriate.

---

## 12. Vehicle Model Growth

Initially the vehicle can be extremely simple.

Later, the vehicle model should be parameterized.

Potential parameters include:

- mass
- center of mass
- wheelbase
- track width
- wheel dimensions
- steering limits
- steering response
- motor characteristics
- acceleration
- braking
- tire/surface interaction
- rolling resistance
- rotational inertia

Do not implement these until needed.

The important architectural principle is that the vehicle's behavior should eventually be generated by a vehicle model rather than arbitrary movement rules scattered throughout the application.

This will eventually allow a simulated vehicle to approximate a real vehicle.

### 12a. Tunable Parameter Reference Table

As the number of tunable values grows — speed, ramp rate, deadzone, calibration offsets, and eventually vehicle-model parameters from this section — these should eventually be consolidated into a single, easily accessible reference table (e.g. a config file or dataclass) rather than scattered as inline defaults throughout the codebase.

This should also eventually expose a way to re-run calibration steps (such as controller center-point recalibration) on demand, not only at startup.

A centralized table serves two purposes: it makes the current tuning of the simulator visible at a glance, and it makes experiments (per section 19) easier to record precisely, since a run's parameters can be captured as a single snapshot rather than reconstructed from scattered code.

This is a lookup table of plain values, read once and referenced during the loop — it introduces no meaningful runtime cost. It should not be built until the number of scattered tunable values makes it worth consolidating; a couple of constants in `vehicle/state.py` do not yet warrant this.

---

## 13. Localization and State Estimation

Once the basic vehicle and telemetry systems are reliable, introduce simulated localization.

The eventual concept is:

True vehicle state → simulated sensor measurements → noisy measurements → estimator → estimated state

The initial localization system may be simple.

Later it may incorporate:

- UWB position
- IMU information
- heading
- velocity
- measurement noise
- dropouts
- uncertainty

Eventually an EKF or other estimator can be introduced.

Do not add an EKF merely because it is technically interesting.

First establish a measurable problem that requires state estimation.

---

## 14. Safety-System Research

The simulator will eventually become a laboratory for developing a safety system.

The philosophy is not to make driving feel artificially safe.

The goal is to allow players to crash and interact physically while preventing the types of collisions that remove a vehicle from meaningful gameplay or create unacceptable damage.

The safety system should ideally be:

as invisible and minimally intrusive as possible.

For example, if a player's input would produce an unnecessarily severe collision, the system might subtly modify the available command so that the resulting contact is less severe.

The simulator should allow multiple safety strategies to be developed independently.

Examples might include:

- projected trajectory
- boundary proximity
- predicted collision location
- velocity-dependent intervention
- steering-envelope limiting
- graduated intervention
- vehicle-to-vehicle prediction

These are experimental hypotheses, not established requirements.

### 14a. Eventual Comparison Interface

Once a safety system exists to evaluate, the visualization should eventually support directly comparing player intent against system output.

The window should widen to add two telemetry panels on the right side:

- **Top panel** — raw player input (what the stick/keyboard actually commanded).
- **Bottom panel** — system output after the safety layer has processed it (what the vehicle actually did).

Showing input and output side by side should make it easy to see, at a glance, what intervention — if any — was applied to a given input.

The main arena view should eventually support a **ghost overlay**: simultaneously showing the unassisted path the vehicle would have taken from raw player input, alongside the actual assisted/simulated path it really took under the active safety ruleset. This turns "did the safety system help, and how much" from an abstract question into something directly visible as two diverging lines on screen.

This interface depends on the safety system (this section) and telemetry recording (section 8) both existing first. It is not a near-term milestone — it belongs naturally alongside Milestone 7 (Safety Experiments) once there is an actual intervention system and recorded player-input stream to compare against.

---

## 15. Multiple Rulesets

The simulator should eventually allow multiple safety rulesets to be run against the same exact scenario and input history.

For example: Ruleset A vs. Ruleset B vs. Ruleset C

Each should receive identical starting conditions.

The system should be able to compare:

- intervention timing
- intervention magnitude
- predicted trajectory
- predicted impact
- resulting state
- player-control preservation
- collisions avoided
- unnecessary interventions
- other defined metrics

This will allow safety strategies to be compared experimentally rather than subjectively.

---

## 16. Scenario Library

The system should eventually maintain a structured scenario library.

Scenarios should be categorized.

Potential categories:

- boundary approach
- high-speed approach
- shallow-angle contact
- vehicle-to-vehicle interaction
- localization anomaly
- sensor dropout
- unexpected vehicle response
- safety intervention
- near miss
- actual failure
- regression case

Every important real-world failure should eventually be capable of becoming a reproducible simulation scenario.

---

## 17. Regression Testing

Every approved safety-system improvement should eventually be tested against the historical scenario library.

The basic philosophy should be:

Every problem we solve becomes a problem we never want to accidentally reintroduce.

Initially, running every scenario is acceptable.

As the library grows, it may be useful to have:

- fast critical regression suite
- complete regression suite
- specialized scenario families

The system should compare versions rather than merely report pass/fail.

An improvement that reduces collisions but dramatically increases unnecessary intervention is not automatically an improvement.

---

## 18. Experimental Development

I want to be able to create divergent strategies without damaging the baseline.

Use version control from the beginning.

The repository should have a known-good baseline.

Experimental changes should be isolated using branches or equivalent version-control mechanisms.

A change should ideally follow:

Hypothesis → Implementation → Simulation → Regression testing → Analysis → Decision

Do not modify unrelated parts of the system while implementing an experiment.

When possible, preserve the ability to completely reproduce an earlier result.

---

## 19. Development Notebook / Experiment Record

For significant experiments, maintain a lightweight record:

- **Hypothesis** — What do I believe?
- **Reason** — Why do I believe it?
- **Experiment** — What will test the hypothesis?
- **Success criteria** — What result would convince me?
- **Failure criteria** — What result would disprove or weaken it?
- **Result** — What actually happened?
- **Decision** — Keep / modify / reject / investigate.

Do not turn every tiny coding task into paperwork.

Use this primarily for meaningful experiments and architectural decisions.

---

## 20. Real-World Calibration

Eventually the system should support comparison between:

Model prediction and physical vehicle telemetry.

A physical test should be capable of recording:

- player input
- estimated state
- safety intervention
- commanded vehicle response
- measured vehicle response
- actual outcome

The system should preserve the distinction between:

what the player requested, what the safety system allowed, and what the vehicle actually did

This allows the simulator to be calibrated against reality.

---

## 21. Continuous Calibration

Eventually, normal operation can contribute to improving the vehicle model.

The system can compare:

expected physical response against observed physical response

and gradually improve calibrated estimates of vehicle behavior.

However:

Adaptive learning must never casually rewrite hard safety limits.

A learned model may improve prediction accuracy.

It should not autonomously redefine fundamental safety boundaries.

Learned parameters should have confidence levels and sufficient data before being considered reliable.

Unexpected deviations should also be treated as potential maintenance indicators.

---

## 22. Evening Data Debrief

Eventually, operational telemetry should be summarized during shutdown.

The system should identify potentially interesting events such as:

- unusual interventions
- near misses
- high-energy contacts
- model/reality discrepancies
- localization anomalies
- repeated vehicle-specific behavior
- unusual vibrations or sensor behavior
- unexpected physical responses

The debrief should not merely dump telemetry.

It should identify patterns requiring attention.

For example:

Vehicle 06 produced significantly greater yaw response than predicted during three high-speed boundary approaches.

The system may then recommend creating a test scenario.

---

## 23. Automatically Generated Test Scenarios

Eventually, an analysis system such as Claude may assist in identifying scenario families from real-world problems.

For example:

High-speed shallow-angle boundary approaches

could become a parameterized scenario family with variables such as:

- speed
- approach angle
- distance
- steering input
- sensor noise
- vehicle configuration

The system can then generate many individual test cases.

The AI may:

- identify patterns
- classify events
- suggest scenario families
- generate test descriptions
- compare results
- recommend investigations

But AI recommendations should remain separate from approved safety behavior.

Human review should determine what becomes an accepted requirement or safety-system change.

---

## 24. Weekly Debug / Improvement Session

The eventual workflow should support a recurring development cycle:

Daily operation → telemetry → evening debrief → interesting events identified → candidate scenarios generated → weekly debug session → scenarios replayed → proposed improvements tested → complete regression suite → candidate physical testing → results returned to the system

This creates a continuous improvement loop.

---

## 25. Architectural Separation

Maintain clear separation between:

- **Input** — What the player/controller requests.
- **Vehicle Model** — What the vehicle would physically do.
- **Sensor Simulation** — What the sensors report.
- **State Estimation** — What the system believes the vehicle is doing.
- **Prediction** — What the system expects to happen next.
- **Safety** — How player commands may be modified.
- **Game** — What the game wants the vehicle to accomplish.
- **Telemetry** — What happened and when.
- **Scenario System** — How situations are reproduced.
- **Analysis** — What the collected data tells us.

Do not allow these responsibilities to become tangled.

---

## 26. Game Engine Compatibility

The eventual simulator may become a foundation for a more sophisticated game environment.

Therefore, avoid making the visualization layer the center of the architecture.

The underlying systems should be capable of operating independently of the renderer.

The same vehicle model, telemetry, scenario system, and safety logic should eventually be capable of being driven by:

- a simple 2D visualization
- automated test input
- recorded telemetry
- eventually a richer game environment
- eventually physical vehicle interfaces

The first renderer is only a window into the simulation.

---

## 27. How I Want You to Work With Me

I want you to act as a technical guide and development partner, not simply a code generator.

When a task is complicated:

1. Explain the objective.
2. Explain the architecture.
3. Break the task into the smallest useful step.
4. Have me implement or test that step.
5. Wait for the result.
6. Diagnose problems.
7. Only then move to the next layer.

Do not give me 500 lines of code when 50 lines will prove the concept.

Prefer small working increments.

When there are multiple reasonable technical approaches, explain the tradeoffs and recommend one.

Do not pretend that an experimental idea is proven.

Clearly distinguish:

- established fact
- engineering assumption
- hypothesis
- estimate
- experiment
- observed result

---

## 28. Do Not Prematurely Solve Future Problems

This document describes the eventual direction of the system.

It is not a command to implement everything immediately.

The current objective should always be the smallest next step that produces useful information.

If the current task is: Connect an 8BitDo controller and move a dot. → Do not introduce an EKF.

If the current task is: Test a simple boundary rule. → Do not build fleet management.

If the current task is: Determine whether noisy localization can support the required state estimate. → Do not build the game.

Build only what is needed to answer the current question while keeping the architecture clean enough to support the next question.

---

## 29. Initial Milestones

Use these as a rough roadmap, not a rigid schedule.

**Milestone 0 — First Contact**
- MacBook development environment
- Python
- Pygame
- 8BitDo Bluetooth connection
- black screen
- white rectangular boundary
- movable white dot

Success criterion: I can move the dot with the controller.

**Milestone 1 — Vehicle Representation**

Add: center dot, orientation line, direction-of-travel line, basic velocity, heading

Success criterion: I can visually distinguish where the vehicle points from where it is traveling.

**Milestone 2 — Telemetry**

Record: timestamp, position, velocity, heading, controller input

Success criterion: A complete run can be saved and inspected.

**Milestone 3 — Replay**

Load recorded telemetry and reproduce the run.

Success criterion: A recorded run can be replayed without the controller.

**Milestone 4 — Basic Physics**

Introduce controlled acceleration, steering, and braking.

Success criterion: The simulated vehicle has predictable, tunable behavior.

**Amendment (post-Milestone 4):** The physics model was implemented as a frame-based accel/friction/top-speed scheme (not a mass/force model) — the smallest model satisfying "predictable, tunable behavior," per Section 12's guidance not to add sophistication before it's needed. A momentum mechanism was added to the velocity vector (separate from speed itself) so that direction-of-travel can diverge from heading — this is what finally makes Milestone 1's direction-of-travel line meaningful, as anticipated in Section 5's original amendment. Wheelbase-aware steering was discussed and deliberately deferred: a genuine future need (Milestone 7 avoidance-maneuver realism) is not the same as a present need, per Section 28 and project-rules.md rule 1 — it will be built immediately before Milestone 7 work begins, when there's a concrete system to validate it against.

**Milestone 4a — Boundary Collision**

The arena boundary has existed as a visual rectangle since Milestone 0, but the vehicle has had no awareness of it as a physical constraint — it could be driven straight through the wall with no consequence.

This milestone adds basic collision detection between the vehicle and the arena boundary: the vehicle should stop or be blocked at the wall rather than passing through it. This does not yet need any of the graduated/invisible safety-intervention behavior described in section 14 — it is a prerequisite for that, not the safety system itself.

Real physics (Milestone 4) needs to exist first, since a collision needs actual momentum/velocity to respond to. Safety-intervention design (Milestone 7) needs this to exist first, since there must be something concrete to intervene against before graduated intervention strategies can be designed or compared.

Success criterion: The vehicle cannot be driven through the arena boundary; contact with the wall is detected and has a consequence (e.g. the vehicle stops or is blocked), even in the simplest possible form.

**Amendment (post-Milestone 4a):** Boundary collision was implemented as point-based (ignoring the vehicle's rendered footprint) with a full-stop response on contact — the smallest form satisfying the milestone's own success-criterion wording ("stops or is blocked"). Radius-aware collision was considered and deferred; the visual overlap it would fix is minor and not worth the added complexity yet.

**Milestone 5 — Sensor Simulation**

Introduce simulated noisy measurements.

Success criterion: I can control the amount and type of simulated sensor error.

**Amendment (post-Milestone 5):** Sensor simulation was built using the same swappable-interface pattern already proven for controller input (section 6): `SimulatedPositionSensor` holds a reference to ground truth and exposes a no-argument `read() -> SensorReading` method, so a future real UWB reader can implement the identical interface with zero downstream changes. This directly supports the eventual real-hardware transition anticipated in sections 9 and 20. Position noise (Gaussian, tunable amount) was implemented; additional noise types (dropouts, bias) are architecturally supported but not built — not yet needed.

**Milestone 6 — State Estimation**

Introduce an estimator such as an EKF if the experiment demonstrates the need.

Success criterion: Estimated state can be compared against known simulation truth.

**Amendment (post-Milestone 6):** A simple predict-correct blended estimator was built, deliberately not an EKF, per this section's own instruction not to add one before a demonstrated need. Gain testing (0.05/0.3/0.5) confirmed the estimator behaves as a genuine trust-weighted blend, not degenerate at either extreme — even near-zero gain retains a residual correction, consistent with the underlying math. **Important, explicitly-confirmed limitation:** because the predict step uses this simulation's own deterministic physics (the same model that generates ground truth), the estimator's apparent accuracy is not representative of real-hardware performance. The trigger for upgrading to an EKF-style estimator is a demonstrated accuracy gap once real UWB data exists (Milestone 10) — not the mere existence of real data.

**Amendment (post-wheelbase-steering, pre-Milestone-7):** Wheelbase-aware steering was implemented as bicycle-model kinematics, the smallest model that makes turning both speed-dependent and geometrically bounded — satisfying the real future need identified back at Milestone 4 (avoidance-maneuver realism) without adding full tire-slip dynamics, which remains explicitly deferred (see Milestone 4's amendment). Two real vehicle parameters were required: wheelbase (confirmed via manufacturer spec) and max steering angle (no manufacturer spec exists; treated as an explicit placeholder per `fleet-hardware.md`'s established pattern for unverified assumptions). Reverse-steering was made to correctly invert relative to forward, matching real Ackermann-steering physics — verified via numeric simulation before shipping, continuing this project's practice of not trusting sign-convention changes without independent verification (per the direction-of-travel sign bug earlier in Milestone 4).

**Milestone 7 — Safety Experiments**

Begin implementing simple safety hypotheses.

Success criterion: Identical player inputs can be tested under different safety strategies.

**Milestone 8 — Scenario Library**

Create repeatable scenarios and automated testing.

**Milestone 9 — Regression Engine**

Run historical scenarios against new ruleset versions.

**Milestone 10 — Physical Calibration**

Compare simulated predictions against physical telemetry.

---

## 30. The Most Important Rule

Do not let the sophistication of the eventual vision cause the initial development to become complicated.

The project begins with:

A black rectangle, a white dot, and an 8BitDo controller.

If that works, we add one useful layer.

Then another.

Every layer should earn its place by answering a question, solving a problem, or enabling the next experiment.

The ultimate objective is not to create an impressive simulator.

It is to create a repeatable experimental environment in which I can safely explore, measure, compare, learn, and eventually validate the technology behind the real system.

That environment should become progressively more capable while remaining understandable, testable, reversible, and grounded in actual data.

---

## Initial instruction to Claude

Start by helping me accomplish Milestone 0 only.

Do not build anything beyond what is necessary to connect the 8BitDo controller and move the white dot inside the black-and-white rectangular arena.

Before writing code, explain the proposed project structure briefly and tell me what we are about to do.

Then guide me through the implementation one step at a time.

Do not proceed to Milestone 1 until Milestone 0 is working.

---

*Amended after Milestone 0 was completed: added section 6a (Keyboard Fallback Input).*
