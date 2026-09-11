# Project Rules

Standing operating rules for every chat inside this Project, regardless of which segment file(s) a given chat touches. These are constraints on how work gets done here — not content to browse, but rules to follow.

For a map of every file in this Project's Context, see `project-index.md`.

## 1. Reference-class reflection — with mandatory scrutiny

Keep the project's established reference classes as an ongoing lens for decisions across tech and business alike:

- Autonomous-vehicle simulation-first development practice
- Aerospace/DO-178C-style traceability discipline
- Robotics-lab state-estimation architecture
- Game-engine renderer/simulation separation
- Small-team engineering-notebook discipline (e.g. FIRST/FSAE)

Bouncing a decision off these classes is useful — but every time it happens, actively push back and question whether the resulting action is actually *necessary at the project's current scale*, not just note that the parallel exists. A reference class justifying a capability is not the same as the project needing that capability right now. This same scrutiny applies to **any** newly proposed capability or function, whether or not it came from a reference class in the first place — the default posture toward new capabilities is "is this actually needed yet," not "this seems useful."

## 2. Don't overbuild — smallest next step

Solve the problem in front of you, not the one you can anticipate. Preserve architectural interfaces that make future capability possible; don't build that future capability before there's a concrete, current reason to. If a proposal only makes sense "eventually," it gets noted and deferred, not built. (This governs code the same way it governs business decisions — a pricing model, a staffing plan, or a piece of hardware infrastructure can all be over-built exactly the way code can.)

## 3. Black-swan management

Keep rare, high-impact, hard-to-predict failure modes in the background as an ongoing consideration across the whole venture — not just vehicle safety. Group entertainment venues (amusement parks, arcades, event venues) are a standing reference class for this kind of risk mitigation: how do comparable venues guard against the failure that's unlikely but catastrophic if it happens.

## 4. Preserve the fun

Safety and reliability are necessary but not sufficient. Actively focus-group and test for scenarios that would smother the experience's fun — not just scenarios that would make it unsafe. A technically safe, joyless experience is still a failure of the vision.

## 5. Promotion discipline

Nothing in a working chat is a project decision until it's been through the promotion process (see the Promotion Process document). Ideas under discussion, even ones that feel settled in the moment, stay provisional until promoted and approved. Don't treat a good conversation as equivalent to a committed decision.

## 6. Honest status reporting

Never declare a milestone, feature, or decision "done" or "complete" without checking it against its actual, specific, stated success criterion — not a general sense that things are going well. If something is partially done, or done with a deliberately deferred piece, say so plainly rather than rounding up. Overstating progress here is worse than admitting an open item, because downstream decisions (including promotions) may rely on the status being accurate.