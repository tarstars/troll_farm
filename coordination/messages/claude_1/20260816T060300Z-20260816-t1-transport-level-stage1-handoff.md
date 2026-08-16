---
schema_version: 2
type: handoff
task_id: 20260816-t1-transport-level
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260816T060300Z-20260816-t1-transport-level-stage1-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 07c983d35ba8743c56f6b8a3044ea66c83ee74d5
artifact_paths: ["claude_1/t1/fixture_harness.py", "claude_1/t1/baseline-resident-2026-08-16.json"]
created_utc: 2026-08-16T06:03:00Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260816-t1-transport-level
- Requires acknowledgement: yes

# handoff: T-1 stage 1 — harness RED on all 34, and it caught an inert check inside itself

## For the owner, in plain terms

Before changing the trolls' behaviour, we need a test that can tell whether a change actually
helped. That test now exists and it currently **fails on all 34 recorded situations** — which is
correct, because nothing has been fixed yet. The failing baseline is what makes a later "fixed"
mean something.

Two things worth your attention. First, the test **caught a bug in itself**: one of its two
checks was silently switched off, so it would have declared situations cured for the wrong
reason. Second, **four of the 34 are not yet properly covered** — the stall cases. They report
the right answer today, but only one of their two checks is actually running.

## Delivered

Artifact `07c983d35ba8743c56f6b8a3044ea66c83ee74d5` on `agent/claude_1`, pushed and
remote-verified. **No fix code exists**; this is the instrument only.

**Result: 0 FIXED / 34** on the unmodified resident, as required before any fix lands.

## Why the replay is a re-run, and why that is legitimate

The frozen situations record **only our own side's command line** — the opponent's commands are
not in the library. A situation therefore cannot be played back; there is nothing to drive the
opponent with. But the provenance records `map_id`, `map_class`, `opponent_profile`, `seed`,
`generation_attempt` and `seat`, which is enough to **regenerate the game that produced it**.

Verified before the harness was written, not assumed: rebuilding all 34 maps through
`fuzz_panel.build_skeleton` reproduces each situation's `static_map_rows` **byte-identically,
34/34**. A reconstruction that does not match aborts rather than grading a different game.

## The bug the harness found in itself — please read this one

`codex_1`'s brief says the harness is *"the instrument everything else is judged by — vacuous-check
history applies"*. It applied immediately, to me.

My episode-overlap filter read `t_start` / `t_end`. **Those keys do not exist** — episodes carry
`turn_start` / `turn_end`. Every `.get()` fell through to its default, **every episode was
filtered out, and `detector_silent` was therefore always True**. The detector half of the grading
rule was **inert**. A T-1 candidate would have been graded on the progress clause alone, and any
situation where the unit happened to move would have been reported FIXED with the detector never
consulted.

My first self-test passed anyway, because the case that should have caught it passed for the
wrong reason — `NOT_FIXED` via the progress clause. **I wrote the docstring warning about exactly
this trap and then shipped it in the same file.**

Repaired, and the repair is guarded rather than trusted: `check_replay_fidelity()` now **requires
every frozen D-1 episode to reproduce exactly** on the resident run. OSC-006 reproduces `unit 2,
turns 12–20, k=4, cells [[1,3],[2,3]]` — exact against the frozen record. If the clause ever goes
quiet for plumbing reasons again, the baseline run aborts instead of reporting a clean sweep.

## Controls — 7 cases, and the two that carry the weight

- **the grader CAN return FIXED**, on a non-stuck window of the same real trace. A grader that
  can only say NOT_FIXED would produce an identical 0/34 baseline and be worthless the moment it
  later said FIXED.
- **the detector clause is observed FIRING** (episodes-in-window ≥ 1), not merely not-crashing.

Plus: quiet-but-stalled is still NOT FIXED with the detector muted by hand; the fidelity check
aborts when an episode fails to reproduce; a wrong map aborts rather than grading another game.

## KNOWN GAP — stage 1b, and I am not calling stage 1 complete without naming it

The harness runs `detect_d1` only. **P4 liveness is not evaluated** — it lives in the panel, not
in `trace_detectors`, and there is no `detect_p4` entry point.

So for the **4 `P4_STALL` situations (OSC-031…034) the "detector silent" clause is vacuously
True.** They grade `NOT_FIXED` on the progress clause alone. That verdict is right today, but it
is reached by one working check and one inert one — and an inert check is not a check. **A T-1
candidate could silence nothing on those four and still be graded by progress only.**

The 30 `D1_EPISODE` situations are fully covered: detector clause fires, frozen episode required
to reproduce.

**Wiring P4 is stage 1b and I will do it before any T-1 fix is graded against the stalls.** I am
flagging rather than proceeding to stage 2 as if the instrument were finished.

## Grading rule — as frozen, not softened

FIXED = detector silent over the window **AND** progress restored. Progress deliberately reuses
D-1's own definition (carry change / inventory change on a DROP-PICK turn / plant appearing or
disappearing under the unit) rather than a second definition of my own, plus "left the frozen
cycle". Quiet-but-stalled is NOT FIXED — the 08-09 20/20 lesson.

## Boundaries

Resident byte-exact `98628e98…` — measured before and after. `rust/`, `cgauto/` and the frozen
library untouched. No Arena action, no banana code, no D1-B door-pricing change. I have **not**
looked at the prediction registry while building, and will not tune against it.

## Next

Stage 1b (wire P4), then stages 2→4. `codex_1` reviews the harness first, per your ordering — it
is the instrument, and it has already demonstrated it can be wrong in a way that flatters the
result.
