---
schema_version: 2
type: handoff
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260820T202851Z-20260820-pair-selector-anti-benching-progress.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260820T205740Z-20260820-pair-selector-anti-benching-phase3-generator-handoff.md
artifact_ref: agent/claude_1
artifact_commit: 1c7aed39ba0bad926bbd99f69257652e7bfb2c13
artifact_paths: ["claude_1/picker2/phase3-generator-route-2026-08-20.md", "claude_1/picker2/idle_shape.py", "claude_1/picker2/idle-shape-2026-08-20.json", "claude_1/picker2/make_route_probe.py", "claude_1/picker2/route_census.py", "claude_1/picker2/route-census-2026-08-20.json"]
created_utc: 2026-08-20T20:57:40Z
---

- To: local_claude_1
- CC: codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes

# Phase 3 DELIVERED — the card's premise was wrong, and correcting it moves the defect

This discharges my own deferral card (the self-addressed `...202851Z-...-progress.md`). It is a
**measurement**. It proposes nothing, builds no candidate, and licenses no extension of P1 or P2.

## The card asked why the anchor's candidate list is EMPTY. It is never empty.

On every idle turn of all four ruled fixtures, on **both** bases, the list is exactly **one**
entry — the `WAIT` that `main_candidates` seeds it with. `main_candidates` and
`endgame_candidates` both open `let mut out=vec![MoisanBot::wait()]`, so an empty list was never
reachable. My Phase-2 handoff said "offered no work at all"; the accurate statement is **offered
the seed and nothing else**.

## One route, 100% of the time — and it is lossy

Every one of those turns takes `main_candidates`' `idle_regeneration && chops.is_empty()`
fallback (`chops=0`, `idle_harvest=0`, `bank=0`, `carried=0`, `free_cap=2`). That fallback
returns a **fresh** `vec![wait()]` rather than extending the `out` it already built — and on
OSC-013 that discard is not harmless:

| OSC-013 idle turns | generator had | returned |
|---|---|---|
| 31–99 (69, contiguous) | nothing but its own `WAIT` | the seed |
| 100–200 (**101**, contiguous) | **two `PICK`s, score 7500 / 7499, target Cell((2,1))** | the seed |

The split is exactly at turn 100 — the `view.turn>=100` guard on the safe-regeneration replant
block that pushes those `PICK`s. Byte-for-byte the same on the door-1 base. So the 170 turns are
**two different phenomena**, not one: on 69 the generator had nothing, on 101 it had work and the
fallback threw it away.

## What this settles for the programme

**The residual stall on these turns is NOT a selector defect.** The selector is handed a
one-element list and returns the only element in it. P1 and P2 are doing what they were built to
do and are correctly untouched. The three detector-quiet-but-stalled fixtures are a generator
question, exactly as the card asserted — the card was right about the location and wrong about
the mechanism.

## What I am NOT claiming

That keeping those two `PICK`s restores progress. They would have to be selected, be legal, and
move the unit out of the cycle; none of that is measured here and the last is the grader's bar.
Nor that the discard is a defect at all — `idle_regeneration` may be deliberately exclusive of
the replant block. **Whether that fallback should extend `out` instead of replacing it is a
design question for the owner. I am not answering it by building something.** The claims about a generator
gap that I withdrew on 2026-08-17 came from exactly this step; this stops before that line.

## Gates — five, each fails the run rather than degrading it

Parity (both probes byte-identical to the uninstrumented candidate's command stream, per fixture
per arm); coverage (exactly one `PS3FINAL` row per window turn, no gaps or duplicates);
**cross-probe agreement** (`PS3FINAL n` read at `by_id.insert` must equal the *selector* probe's
`PS2CAND` row count for the same unit and turn — two independent taps, one list); one route row
per unit per turn; exact-once anchoring or the build is refused. All passed. A cross-check that
must be 0 — an idle turn with non-`WAIT` work in the list — is 0 everywhere, so this reader and
`gate_bench.py` agree on which turns are idle.

The route tap is not a constant: employed turns come back `main:CHOPS` and `main:FULL_BANK`.

## Replay

    python3 claude_1/picker2/idle_shape.py
    python3 claude_1/picker2/make_route_probe.py
    python3 claude_1/picker2/route_census.py

`run_gates.py` is **deliberately unmodified** — codex_1 reproduced the Phase-2 package as it
stands and Phase 3 does not perturb a reproduced artifact.

## Cards

**DEFERRED: the owner's design question above** — may the `idle_regeneration` fallback extend
`out` instead of replacing it? Nothing may be built against it until it is ruled. Note the
scope: it can only bear on 101 of OSC-013's 170 idle turns and on **none** of OSC-004 /
OSC-017 / OSC-034, where the generator genuinely produced nothing. A change justified by the 101
must not be reported as addressing the rest.

**DEFERRED: card 2 (sentinel build)**, unchanged, still blocked on the single ruling — may
`actionable_set()` be extracted into `scripts/inbox_sweep.py` so `main()` and the sentinel share
ONE code path?

Unchanged and still open: **VM disk** (unowned, flagged not claimed).

No Arena action taken or authorized.
