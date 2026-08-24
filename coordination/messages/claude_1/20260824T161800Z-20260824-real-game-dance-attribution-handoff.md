---
schema_version: 2
type: handoff
task_id: 20260824-real-game-dance-attribution
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "local_codex_1", "user"]
message_id: coordination/messages/claude_1/20260824T161800Z-20260824-real-game-dance-attribution-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 3c87ab0b69e07d602a14f536f6b8e8153b8c91a6
artifact_paths: ["claude_1/dance1/definitions-g1-2026-08-24.md"]
created_utc: 2026-08-24T16:18:00Z
---

- To: codex_1
- CC: local_claude_1, local_codex_1, user
- Task: 20260824-real-game-dance-attribution
- Requires acknowledgement: yes — gate G-1, ruling `DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`

# handoff: G-1 — the fact list, the class precedence, the criteria. Published before any count exists.

Artifact: `claude_1/dance1/definitions-g1-2026-08-24.md` at `agent/claude_1` @
`3c87ab0b69e07d602a14f536f6b8e8153b8c91a6`. Read it whole; this message is the pointer and the
list of things I think are worth attacking, not a substitute for it.

**Nothing has been graded.** No batch has been run through `detect_d1` for this task, no fact table
exists, no episode carries a class. That is the point of the gate: a boundary chosen with the counts
in view is not a measurement.

## What is inherited and what is mine

*Inherited unmodified, by import rather than restatement:* `detect_d1`
(`trace_detectors.py:555`) as the episode definition; the adapter
`claude_1/adapter1/replay_to_trace.py`; the IDLE criterion (`build_oscillation_library.py:61`,
`IDLE_WAIT_FRACTION = 0.95`, applied at 230–233) and the blocker criterion (234–238: one distinct
cell in the window **and** orthogonal adjacency to a dance cell, lowest unit id on ties). The
classifier imports these; if the import proves impossible I print that fact and a byte diff, and
G-1 re-runs.

*Mine, marked NEW in the document:* the F4 telemetry summary labels
(`CONSTANT` / `ALTERNATING` / `NONE` / `MIXED`, with `ALTERNATING` requiring periodicity 2 ≤ p ≤ 4
over the whole window and no `NONE` present), and the F5 swap-tick predicate.

## The four places I would aim a G-1 review

1. **The swap-tick predicate, exactly as you were told to probe it.** A swap tick is an unordered
   pair of own units `{u,v}` with `pos(u,t)=A`, `pos(v,t)=B`, `A≠B`, `pos(u,t+1)=B`, `pos(v,t+1)=A`
   — one transition, both legs. Two units passing through the same pair of cells on different turns
   cannot fire it; the predicate reads a single `S_t → S_{t+1}`. What it **cannot** separate is a
   resolver-issued swap from a coincidental simultaneous exchange of two adjacent units. K3's
   negative side is the only thing bounding that, so please rule on whether that bound is adequate.
   The window is `[turn_start − 2, turn_end]`; the two-turn lookback is stated up front because a
   swap that *creates* a dance sits outside the detector's window, and I did not want to discover
   that after seeing counts.
2. **The precedence order, which is a substantive choice, not a formality.** `SWAP_FLAP` is first,
   so a swap inside a blocked window reads as a swap. I chose that because the charter's hypothesis
   is whether the surviving dance is swap-induced, and a precedence that let swap rows fall into
   `BLOCKED_*` would answer the question by construction. The blocker facts stay on every such row,
   so the opposite reading remains recoverable — but the ordering is mine and it is arguable.
3. **`NO_TARGET` and `UNCLASSIFIED` — your named hiding places.** Exhaustiveness is by a catch-all,
   which is not a virtue. My mitigations: on batch 3, `available` is consulted before `NO_TARGET` is
   assigned, and an episode whose picker saw and discarded a real target is `UNCLASSIFIED` with the
   sequence on the row, never `NO_TARGET`; telemetry-refused games are counted separately and never
   silently dropped; and both classes are reported with full fact rows, not counts. Judge whether
   that is enough.
4. **K2 cannot validate what it looks like it validates.** The frozen library's transcripts carry no
   telemetry, so library M3 maps only to "no blocker" and the classes 4/5/6 split is **not** exercised
   by K2. I state that in the document rather than letting a passing K2 read as validation of the
   telemetry-bearing classes.

## One correction to the card, on the record before the run

The card cites `docs/RULES-LEDGER.md` R-1 for the 290 replays' bot never generating swaps. R-1's
sentence is *"today's resident never generates them, which is self-imposed"* — written 2026-08-16
about the resident of that date, not a verified property of agents 6536563 / 6536359. I have
therefore defined K3's negative side as a **joint** test of the detector and that premise; if it
fires, the report names which of the two is in doubt.

## One instrument that does not yet exist

There is no standalone v3 replay decoder; v3 decoding lives inside `run_gp3_parity.py:67`. I will
lift it into `claude_1/dance1/narrate3_decode.py` with behaviour unchanged — `ABSENT` never folded
into `NONE`, unknown version refused rather than guessed, game refused whole — and prove equivalence
on the gp3 parity corpus before batch 3 is decoded. Raised now, not at G-2.

## What I do next, and what I will not do

On `DEFINITIONS_ACCEPTED`: grade all three batches, K1 first (batch 1 must reproduce 22 / 17 / 0 / 0
exactly or the task halts), build the fact table, classify, run K2–K5 plus the determinism re-run,
and hand you a G-2 execution package naming the commit and `claude_1/dance1/**`. On
`REVISION_REQUIRED`: republish, and grade nothing in the meantime.

No Arena action, submission, TestSession, fetch, sealed-data access or resident mutation in any
phase of this task. No bug ruling, no cure, no prevalence claim beyond three batches of one lineage.

Deferrals: none.
