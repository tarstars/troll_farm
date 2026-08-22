---
schema_version: 2
type: handoff
task_id: 20260822-alpha-progress-regrade
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260822T162844Z-20260822-alpha-progress-regrade-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260822T161349Z-20260822-alpha-progress-regrade-policy.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: acdda3a0f0da761cd692b9971b575f185003a573
artifact_paths: ["claude_1/regrade3/panel_progress_adapter.py", "claude_1/regrade3/panel_adapter_controls.py", "claude_1/regrade3/panel_regrade.py", "claude_1/regrade3/panel-adapter-controls-2026-08-22.json", "claude_1/regrade3/alpha-progress-regrade-2026-08-22.json", "claude_1/regrade3/alpha-progress-regrade-report-2026-08-22.md"]
created_utc: 2026-08-22T16:28:44Z
---

- To: codex_1 (G-1 review, instrument-first), local_claude_1 (integrator)
- CC: user
- Task: 20260822-alpha-progress-regrade
- Requires acknowledgement: yes

# DELIVERY: cure α re-graded with the two-clause test — 32 of 34 healed events carry restored progress, 2 are quiet-but-stalled, 0 window-absent

Full package: `claude_1/regrade3/alpha-progress-regrade-report-2026-08-22.md` at the pinned commit.
This message discharges the card `20260822-alpha-progress-regrade`.

## STEP 0, which the card required before anything was built: NO RE-RUN NEEDED

**The traces were retained.** Both packets of the 2026-08-21 rev-2 panel run survive under
`/tmp/claude-1000/swap-g2{,-floor}/games/games.jsonl.gz`, and they are proven to be *that* run:
re-running the accepted `claude_1/swap1/g2_grade.py` over them reproduces the published
`g2-panel-rev2-2026-08-21.json` **byte-identically**. Gate M is re-run inside the re-grade and
passes on all 240 games. No cost decision is owed and none was taken.

Named cost: those packets are scratch, `/tmp` does not survive a reboot, and the bulk roots are
unavailable today (`check_external_storage.py --intent read` → FAIL, exit 2), so they cannot be
archived. Both sha256 are pinned in the result JSON with the ~15 s rebuild command, so a re-run
can be **proven** identical rather than assumed.

On "20 games": 240 − 210 = **30** games have a changed command stream; exactly **20** of those
carry a base event, so 20 is the re-grade surface. Both numbers in the card are right and count
different things. The 210 unchanged games were not re-graded; they are used once, as control C4.

## G-1 — the instrument, which is what I am asking codex_1 to rule on FIRST

The predicate is **not copied — it is imported.** `panel_progress_adapter` defines no `grade`;
it calls `fixture_harness.grade`. C1 pins the harness file's sha256 and `inspect.getsource`
digests of `grade`, `had_progress`, `left_the_cycle`, `unit_positions`, so an edit to the
accepted harness fails the control rather than quietly changing what "progress" means.

**Two adapter judgements are load-bearing, and I am naming both rather than leaving them to be
found:**

1. **The identity substitution.** `grade()` gates on `reproduces_the_recorded_episode`, which in
   the fixture setting means *this run replays the recorded episode*. **That question is not
   askable of a cure arm** — measured today, not recalled: control C5 ran `fixture_harness`
   unmodified against `claude_1/picker2/candidate-cureC-p1p2.rs` on the card's four fixtures and
   got `NOT_REPRODUCIBLE_ON_BASE` **4 of 4** ("14 of 14 frozen window command lines differ"). A
   cure exists to change those lines. So the adapter supplies the question the card names —
   *does the candidate run contain the base episode's window* — through the same gating parameter,
   which is what keeps WINDOW_ABSENT a third outcome that cannot be folded into either other
   bucket. **It is a different question wearing the accepted question's key.**
2. **The P4 side-scope composition, and it changed the answer on all 16 P4 events.** A panel P4
   violation is worded about the **side** ("no own-inventory/own-cargo progress over turns
   42-200") and carries no unit id; the progress clause is unit-scoped. The adapter grades each P4
   event once per own unit and composes: silent AND *at least one* own unit progressed. On every
   one of the 16, exactly one of two own units progressed and the other did not — so under this
   OR the P4 half is 16/16, and under an AND it would be **0/16**. Per-unit rows are in the JSON
   so you can recompute rather than trust. The D-1 half does not depend on this either way.

The predicate itself was **not** modified, so the card's STOP condition was not reached.

**Controls, all five PASS and each can fail:** C1 pins; C2 `grade(identity=None)` refuses;
C3 WINDOW_ABSENT reachable and not folded (past-horizon window, absent unit); C4 the detector
clause is live — all **43** base events of all **240** games graded against the **base** arm come
back STILL_FIRING, 0 offenders, and 43 = 27 D-1 + 16 P4 is α's base column exactly; C5 fires
**both ways** on the card's own cases — OSC-004/013/017 → QUIET_BUT_STALLED, OSC-034 →
HEALED_WITH_PROGRESS, reproducing the ruled outcome.

## G-2 — the answer, not a finding until G-1 is ruled on

| shape | base | α's old headline | HEALED_WITH_PROGRESS | QUIET_BUT_STALLED | WINDOW_ABSENT | STILL_FIRING |
|---|---|---|---|---|---|---|
| D-1 | 27 | healed 18, new 0 | **16** | **2** | **0** | 3 (+6 in unchanged games) |
| P4 | 16 | healed 16, new 0 | **16** | **0** | **0** | 0 |
| **total** | **43** | **healed 34** | **32** | **2** | **0** | 3 |

- The detector-silent count **reproduces the headline exactly** — 18 and 16 — arrived at by
  grading each event's own window instead of subtracting two totals.
- `new = 0` holds: 27 base D-1 = 21 in changed games + 6 in unchanged; the candidate's 9 = those
  6 + the 3 still firing. No candidate episode is unaccounted for.
- WINDOW_ABSENT = 0 is a measurement, not a missing one: C3 shows the bucket is reachable.

The two that come off the headline: `m028/s1/D-1@26-32/u0` (cells [7,4] [8,4]) and
`m040/s0/D-1@176-200/u0` (cells [2,4] [3,4]) — detector silent, no progress event in the window,
`left_cycle` True in both, i.e. exactly the three-cell no-progress loop codex_1's accepted
finding 1 of 2026-08-16 removed from the verdict. Per-event table with all 34 events and every
changed game named is in the report.

**Against the amended bar** the card carries — healed *with progress* minus new — the arithmetic
is **32 − 0 = +32, positive**. I state that arithmetic; I do not declare G-2 passed. That is the
integrator's, and the other G-2 clauses and the three open questions on `20260821-swap-r1-cure`
are untouched.

## What this does NOT claim

Not a G-2 pass, not G-3/G-4 qualification, no Arena action, no candidate edit, no new cure, no
widening, no change to the accepted predicate, no re-ruling of any case, nothing on the residual
13 / P3 applicability / the cure-arm basket criterion, and nothing resting on `chatgpt_1`'s
position document, which is unpublished and is not cited here.

## For the owner, in plain words

We asked whether α's numbers were the alarm going quiet or the troll going back to work.
Thirty-four events, re-checked one at a time with the stricter test we already owned: **thirty-two
are real work restored, two are the alarm going quiet over a troll still doing nothing.** α is not
the flattered cure P1+P2 turned out to be.

One caution, which is why a reviewer sees this before you act on it. Sixteen of the thirty-two
rest on a judgement I had to make: the P4 alarm is about the whole side, the progress test we own
is about one troll. I read "the side progressed" as "at least one troll progressed", because that
is how P4 itself is written — but on every one of those sixteen, one troll worked and the other
did not. Read the stricter way, that half would be zero instead of sixteen. codex_1 is being asked
to rule on exactly that; the other half, 16 of 18, does not depend on it.

## Reproduce

```
python3 claude_1/regrade3/panel_adapter_controls.py     # G-1, five controls
python3 claude_1/regrade3/panel_regrade.py              # G-2, the table
```
