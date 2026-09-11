# Promotion Process

This document defines how an idea, decision, or finalized concept moves from a working chat into one of the Project's permanent segment files (Project knowledge). Reference this document whenever initiating a promotion.

## Trigger Phrase

> "Let's commit this concept."

Said at the natural end of a discussion, once an answer or decision has actually been reached — no need to name the target file explicitly. The concept and its context come from the conversation itself.

A more explicit form is also valid when you want to direct it yourself:

> "Initiate promotion of this concept to '<file>' and any other related files."

Either phrasing starts the same process below. If the target segment isn't named, identify it from context in step 2 and confirm it before drafting anything.

## The Segment Files

The Project's knowledge base is organized into functional segments. Each is a living document, updated only through promotion — never edited ad hoc from inside a chat.


| Segment                  | Covers                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| **Business Vision**      | Core concept, market positioning, launch phasing, target buyer, pricing philosophy       |
| **Tech / Charter**       | Simulation lab charter, software architecture, milestones, technical decisions           |
| **Fleet / Hardware**     | Vehicle platform, puck/localization hardware, maintenance intelligence, fleet management |
| **P&L / Pricing**        | Cost structure, pricing hypotheses, revenue model, financial assumptions                 |
| **Staffing / Ops**       | Operating model, staffing targets, service tiers, event logistics                        |
| **Fun / Safety Testing** | Safety philosophy, black-swan risk management, "don't smother the fun" testing plan      |


This list itself can grow — if a promoted concept doesn't cleanly fit an existing segment, that's a signal to consider whether a new segment file is warranted, not to force-fit it somewhere it doesn't belong.

## The Promotion Steps

When the trigger phrase is used, work through these steps in order:

**1. Confirm the concept.** Restate, in a sentence or two, exactly what's being promoted — so there's no ambiguity about what's going into the permanent record before anything is drafted.

**2. Identify the target file(s).** Confirm the primary file named in the request. Then actively consider: does this concept touch any other segment? (Example: a hardware decision that also affects the P&L, or a safety-testing decision that also belongs in the charter.) Name every file that should be touched, not just the one first mentioned. Consult `project-index.md` for the current map of segment files — including which segments don't have a dedicated file yet, in which case this promotion may be the one that creates it.

**3. Check for interdependencies and conflicts.** Before drafting anything, check the concept against the *current* content of every file it will touch — and against related content in other segment files, even ones not being edited. Specifically look for:

- Direct contradictions (this concept says X, an existing file says not-X)
- Stale assumptions the new concept invalidates elsewhere
- Related open questions in other files that this concept now answers or changes

Surface anything found before proceeding — a conflict found here is more valuable than one discovered later.

**4. Draft the clean write-up.** Write the concept in the voice and format of a permanent segment file — durable, decision-focused language, not conversational chat language. This is the text meant to actually replace or extend the target file's content.

**4a. Capture the reasoning.** Every promotion must include a brief note on *why* — the reasoning behind the decision, not just the decision itself. This is a deliberate change-control record: documenting human reasoning at the moment a decision is made, so that if the decision ever needs revisiting, the original context and tradeoffs are still available rather than lost. This also guards against boxing the business into a choice that was made for reasons no longer visible or remembered later, when reversing it could be expensive. The reasoning note should be short — a sentence or two is enough — but it is not optional.

**5. Present it for confirmation.** Show the draft (and any proposed edits to secondary files from step 2), along with the captured reasoning, before anything is finalized. End the presentation with the exact wording to type back:

> Type **"approve"** to commit this diff, or **"decline"** to discard it.

Nothing gets promoted without that exact confirmation. If the person responds with edits instead of approve/decline, revise the draft and present it again with the same closing prompt — don't guess at implicit approval from a partial response.

**6. Hand off for manual upload.** Chats cannot write to Project knowledge automatically. Once approved, the final step is the person copying the approved text into the actual Project knowledge file (uploading a replacement, or editing the file directly, depending on how the Project is set up). This document does not remove that manual step — it exists to make everything *before* that step rigorous, so the manual upload is just a copy-paste, not a drafting exercise.

## What Promotion Is Not

- Not a place to resolve open disagreements — if the concept isn't actually settled, it isn't ready for promotion yet.
- Not automatic — every promotion is a deliberate, reviewed action, not a background process.
- Not one-directional busywork — the interdependency check in step 3 is the actual value of this process; skipping it defeats the purpose.

