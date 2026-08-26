---
schema_version: 2
type: handoff
task_id: 20260821-episode-identity-regrade
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
message_id: coordination/messages/claude_1/20260821T105300Z-20260821-episode-identity-regrade-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260821T104355Z-20260821-episode-identity-regrade-policy.md"]
supersedes: []
created_utc: 2026-08-21T10:53:00Z
artifact_ref: agent/claude_1
artifact_commit: 5d54a723d1ead699a346d416b232e66e2b4aa266
artifact_paths: ["claude_1/t1/fixture_harness.py", "claude_1/regrade2/identity_gate_controls.py", "claude_1/regrade2/identity-gate-controls-2026-08-21.json", "claude_1/regrade2/regrade34.py", "claude_1/regrade2/regrade34-identity-2026-08-21.json", "claude_1/regrade2/owner-note-what-fixed-meant-2026-08-21.md"]
---

- To: codex_1 (instrument-first review, G-1/G-2/G-3)
- CC: local_claude_1, user
- Task: 20260821-episode-identity-regrade
- Requires acknowledgement: yes
- Base commit: 5d54a723d1ead699a346d416b232e66e2b4aa266

# Identity gate is in the shared harness, and the champion's 8 FIXED go to ZERO

ACK of the CARD at `20260821T104355Z`. All four deliverables are here; it is one wake behind the
α G-1 remedy step, as the priority said. Measurement and tooling only — no bot changed, no case
re-ruled.

## Deliverable 1 — the gate, lifted not paraphrased

`check_window_commands` and `check_entry_state` now live in `claude_1/t1/fixture_harness.py`,
**byte-identical** to the accepted `claude_1/regrade1/real_end_regrade.py`; `RegradeError` is
aliased to `HarnessError` rather than renamed precisely so the bodies did not have to change.
`episode_identity` wraps them so an undecodable window or entry state is a verdict, not a
traceback. `grade()` takes the verdict as a **required** argument and reads it before any recorded
turn bound, cell or unit id; a call without one raises. Failing fixtures grade
`NOT_REPRODUCIBLE_ON_BASE` — never FIXED, never NOT_FIXED.

`run_situation` keeps its 4-tuple for the seven existing callers; `run_situation_ex` is the new
one that also returns the command lines.

## Deliverable 2/3 — the re-grade, side by side

`claude_1/regrade2/regrade34-identity-2026-08-21.json`, both arms, every row annotated with the
real end turn and grace-only bound **read from** the accepted `20260821-p4-stalls-real-end-regrade`
artifact (subject arm) rather than recomputed.

| | before the gate | identity enforced |
|---|---|---|
| FIXED | 8 | **0** |
| NOT_FIXED | 26 | 11 |
| NOT_REPRODUCIBLE_ON_BASE | — | **23** |

The champion reproduces OSC-001, 002, 005, 012, 013, 017, 021, 024, 026, 027, 030 — the same 11
local_claude_1 named, reached independently through the harness. Seven of the eight lost FIXEDs
differ on **every** frozen command line in their window (OSC-034 on 4 of 94). Of the 23: 18 caught
by both halves, 3 by commands alone, and **2 by the entry board alone — OSC-032 and OSC-033**,
the pair that motivated the card. A command-only gate would have waved through exactly the cases
it was built for.

## Deliverable 4 — the owner note

`claude_1/regrade2/owner-note-what-fixed-meant-2026-08-21.md`. Its headline: the right reading is
**"unmeasured", not "regressed"** — the eight rows asked a real question of the wrong game.

## Validation

- `python3 claude_1/t1/fixture_harness.py --self-test` — **17 cases PASS**, including four new
  ones: the gate accepts the subject on its own episode, rejects a same-count/one-unit-moved
  board, fails closed on an undecodable entry state, and `grade()` refuses to run without a
  verdict. The pre-existing 13 are untouched and still pass.
- `python3 claude_1/regrade2/identity_gate_controls.py` — **11/11**. G-1: `inspect.getsource` of
  both lifted functions compared character-for-character against the accepted module, plus a
  sha256 pin on that file (`370122fada39ac85…`), plus an AST proof that `identity` is referenced
  at line 344 and the gated inputs (`d1_episodes` 368, `p4_violations` 371, `had_progress` 380,
  `left_the_cycle` 381) only after. G-2: the champion is rejected on OSC-032 **and the record
  shows its window-command half passed with 0/110 mismatches**, which is the non-vacuity evidence
  that the two halves are not one check written twice.
- `python3 claude_1/regrade2/regrade34.py` — rc 0. Two fail-closed corpus gates inside it: the
  subject arm must reproduce **34/34** (it does) and the champion arm must **not** reproduce all
  34, or the gate would never have been observed rejecting on the measured arm.
- `sha256sum rust/src/bin/yamo_orchard_live.rs` — `fff6669b…`. `git status --short` — clean.

## Known failures and assumptions

- The prior `claude_1/picker2/sweep34-door1-base.json` is **not** overwritten; it is the
  before-column and stays as the artifact of its own task.
- Every consumer of the harness now sees the new vocabulary. That is the intended bite: α's G-2
  and anti-benching 3c both read this grader.
- No re-ruling, no library re-freeze. Whether to re-freeze on the champion is the owner's and I
  make no recommendation here.

## Requested action

Instrument-first review of G-1/G-2, then the G-3 table and note. If you want the byte-equivalence
proof stronger than `inspect.getsource`, say so and I will pin per-function digests as well.

## DEFERRED: anti-benching Phase 3a

Not started this wake and not abandoned: the diagnosis card `20260820-pair-selector-anti-benching`
Phase 3a is read-only and next in my queue, and it now inherits a correction from this work —
of its four named fixtures **013 and 017 reproduce on the champion; 004 and 034 do not** and will
be reported NOT_REPRODUCIBLE rather than diagnosed. Unblock: nothing; it is mine to run next wake.
