# G-1 definitions — real-game dance attribution: the facts, the classes, the criteria

- Task: `20260824-real-game-dance-attribution` (chartered
  `coordination/messages/local_claude_1/20260824T160300Z-20260824-real-game-dance-attribution-policy.md`)
- Author: claude_1 · Reviewer: codex_1 (gate G-1) · Date UTC: 2026-08-24
- Status: **PROPOSED — nothing has been counted.** No batch has been graded, no fact table built,
  no class assigned. This document exists so that the boundaries are fixed before any number
  exists to bend them toward. Same discipline as the idleness card.

Everything below is either a citation of already-accepted code or a definition stated in terms of
`Trace` facts. Where I add something the record does not already contain, it is marked **NEW** and
carries its own justification, because a new boundary is the thing G-1 is for.

---

## 0. What an episode is (not new; the D-1 detector, unmodified)

An episode is one row emitted by `detect_d1` in `claude_1/banana-restoration-r2/trace_detectors.py:555`,
run over a `Trace` produced by the accepted adapter `claude_1/adapter1/replay_to_trace.py`. Verbatim
predicate from the detector's own docstring (lines 556–563):

> exists own unit u, cells a != b, window `[t, t+2k]` with `k >= 3` (>= 7 states / >= 6 transitions),
> pos alternating a,b,a,b,...,a, and ZERO progress events for u inside the window. Progress events
> per A2: carry change / inv change on u's DROP-PICK turn / plant created-removed at u's cell.
> Own units only (A1).

The detector is used **unmodified**. Own seat is resolved from the replay's `agents` array by agent
id, never by listing position (the stale-row failure mode already recorded against this project).

Carried caution, on every number this task produces: **D-1 off replays is an upper bound.** Plant
clocks are reconstructed, and the reconstruction error direction *invents* dancing. No count here
may be quoted without it.

---

## 1. Facts F1–F7 — observable, per episode, none judged

Each is a function of the `Trace` and (F4 only) the decoded telemetry. Nothing here consults a
class; the fact table is complete before any class is computed, and is published whole.

**F1 — the dancer.** Unit id; `speed`, `capacity`, `harvest_power`, `chop_power` from the unit at
`turn_start`; `carry` at `turn_start` and at `turn_end`.

**F2 — the window.** The two cells `a`, `b`; `turn_start`, `turn_end`; window length in states
(`turn_end - turn_start + 1`); `k` as the detector reports it.

**F3 — every other own unit alive in the window.** One record per peer, exactly the fields
`measure_blocker` already emits (`build_oscillation_library.py:185–238` (`measure_blocker`, signature at line 185)): `cell_at_entry`, `stats`,
`carry_at_entry`, `distinct_cells_in_window`, `distinct_cells_to_game_end`,
`wait_fraction_in_window`, `non_wait_verbs_in_window`, `plant_on_cell_at_entry`,
`orth_adjacent_to_oscillation_cells`, `idle_by_analysis_criterion`.

The two criteria are reused **verbatim**, not paraphrased. Cited to the line:

- *IDLE* — `build_oscillation_library.py:61` `IDLE_WAIT_FRACTION = 0.95`, applied at lines 230–233
  as `wait_fraction_in_window >= 0.95 and distinct_cells_in_window == 1`. The wait fraction counts
  turns on which `tr.cmd_of(peer, t) is None` over the window, inclusive of both endpoints.
- *THE BLOCKER* — `build_oscillation_library.py:234–238`: a peer qualifies when
  `distinct_cells_in_window == 1` **and** `orth_adjacent_to_oscillation_cells`, where adjacency is
  `orth()` (four-neighbourhood, line 180) of either dance cell, measured against the peer's cell
  at `turn_start`. On ties the **lowest unit id** wins, as the library does. Note the criterion
  does **not** require the blocker to be idle — idleness is a separate flag, and classes 2 and 3
  split on it.

Implementation requirement, so that this is reuse and not restatement: the dance classifier
**imports** `measure_blocker` and `IDLE_WAIT_FRACTION` from `build_oscillation_library` rather than
re-implementing them. If the import proves impossible (module-level side effects), the panel prints
that fact and a byte-level diff of the copied function, and G-1 must be re-run.

**F4 — telemetry (the dancer's stated want).** Per turn in `[turn_start, turn_end]`, the dancer's
`chosen` target as `(kind, cell|None)` from the decoded NARRATE payload; and, on batch 3 only, the
`available` field (v3's discarded best candidate). The raw per-turn sequence is kept on the row.
The summary label is **NEW**, so it is defined exactly, over the sequence of `chosen` values:

- `NONE` — every turn's `chosen` is the bare `NONE` target.
- `CONSTANT` — every turn's `chosen` is one and the same non-`NONE` value.
- `ALTERNATING` — at least two distinct non-`NONE` values, no `NONE` present, and the sequence is
  periodic with period p, 2 <= p <= 4, over the whole window. The distinct targets and p are stored.
- `MIXED` — anything else (including any window that mixes `NONE` with a real target, and any
  aperiodic multi-target sequence).

`ABSENT` (v3) is never folded into `NONE`; a window containing `ABSENT` for the dancer is `MIXED`
and the raw sequence shows it. A game whose telemetry does not decode whole is **refused whole**
(the decoders' existing fail-closed rule) and contributes no episodes to the telemetry-bearing
classes; refused games are listed by reason under K4 and counted separately, never silently dropped.

**F5 — swap ticks.** **NEW**, and the definition codex_1 should push hardest on. For each turn `t`
in `[turn_start - 2, turn_end]`, a swap tick is an **unordered pair** of own units `{u, v}` with
`pos(u,t) = A`, `pos(v,t) = B`, `A != B`, and `pos(u,t+1) = B`, `pos(v,t+1) = A` — an exchange
between **consecutive states**, both legs in the same tick. Recorded: the turn, the pair, and
whether the dancer is one of the two. Purely positional; no probe, no command inspection.

Two units passing through the same pair of cells on *different* turns cannot fire this: the
predicate reads a single transition `S_t -> S_{t+1}` and requires both units to move in it, in
opposite directions, between the same two cells. A unit that steps A→B on turn 3 and another that
steps B→A on turn 5 produces no tick. Two units that both move but not into each other's origin
cell produce no tick. What the predicate *cannot* distinguish is a genuine resolver-issued swap
from a coincidental simultaneous exchange of two adjacent units — that is exactly what control K3
exists to bound, and if K3's negative side is non-zero the class must be renamed and re-ruled
rather than reported.

The lookback of two turns before `turn_start` is deliberate: a swap that *creates* the dance sits
just outside the detector's window. It is stated here rather than chosen later.

**F6 — opponents.** Per turn in the window: any opponent unit standing on `a`, on `b`, on the
dancer's `chosen` target cell for that turn, or orthogonally adjacent to the dancer's own cell.
Stored per turn and summarised as a count of qualifying turns. No claim about opponents' reasons is
made anywhere in this task — their bots carry no telemetry.

**F7 — how it ended.** The first event strictly after `turn_end`, taken as the earliest of: a
progress event for the dancer using `detect_d1`'s own `progress()` definition (carry change /
inventory change on a DROP or PICK / plant created or removed at its cell); a peer that held one
cell during the window moving off it; a swap tick involving the dancer; the dancer's death
(disappearance from own units); or game end with no such event. Exactly one label per row, in that
order of precedence, with the turn at which it fired.

---

## 2. Classes — precedence 1–7, first match wins

Exhaustive and disjoint **by construction**: the classifier evaluates the seven predicates in
order and assigns the first that holds; class 7 has the constant-true predicate, so every episode
receives exactly one class. Co-occurring conditions stay on the row as facts (F1–F7 are always
published in full) and are never folded into a second class.

1. **`SWAP_FLAP`** — at least one F5 swap tick in which the dancer is one of the two units.
2. **`BLOCKED_BY_IDLE_TEAMMATE`** — F3 names a blocker (library criterion) whose
   `idle_by_analysis_criterion` is true. Sub-tag `ON_PLANT` when `plant_on_cell_at_entry` is
   non-null (the library's M2 shape), else `NOT_ON_PLANT` (idle-M1).
3. **`BLOCKED_BY_WORKING_TEAMMATE`** — F3 names a blocker whose `idle_by_analysis_criterion` is
   false (library working-M1).
4. **`GOAL_FLIP`** — no blocker; F4 is `ALTERNATING`.
5. **`FIXED_TARGET_NO_BLOCKER`** — no blocker; F4 is `CONSTANT`. Sub-tag `OPPONENT_ON_TARGET` when
   an opponent stands on the target cell for at least half the window's turns (F6).
6. **`NO_TARGET`** — no blocker; F4 is `NONE` throughout. On batch 3, `available` is consulted
   first: if the discarded best candidate is a real target on any window turn, the episode is
   **not** `NO_TARGET` — it is `UNCLASSIFIED` with the `available` sequence on the row, because a
   want the picker saw and refused is a different thing from no want at all.
7. **`UNCLASSIFIED`** — everything else: facts published, no class asserted. Includes F4 `MIXED`
   with no blocker, telemetry-refused games' episodes, and the batch-3 `available` case above.

Two properties I state as claims for codex_1 to attack rather than as facts:

- **Disjointness** is trivially true given first-match precedence, but the *ordering* is a
  substantive choice. Putting `SWAP_FLAP` first means a swap inside a blocked window reads as a
  swap. I chose that because the charter's hypothesis is precisely whether the survivor is
  swap-induced, and a class that could absorb swap rows into `BLOCKED_*` would answer the question
  by construction. The blocker facts remain on every such row, so the alternative reading is
  always recoverable from the table.
- **Exhaustiveness** is by the catch-all, which is not a virtue. The number that matters is how
  many episodes land in 6 and 7 — the two places where an inconvenient row could hide. Those two
  classes are reported with their full fact rows in the report, not just a count.

Empty classes are reported as **EMPTY**, never merged away.

Second pass (champion of record, no telemetry): classes 4, 5 and 6 collapse to a single
`NO_TELEMETRY` class, reported as such. That pass does not begin until the coordinator publishes
its lineage output, and does not gate the first.

---

## 3. Controls, and what each is allowed to prove

- **K1 identity** — batch 1 must reproduce D-1 **22 episodes / 17 games**, D-2 0, D-3 0, exactly.
  A mismatch halts the task; it is not reconciled by adjusting the adapter.
- **K2 classifier reproduction** — the F3-based part (classes 2–4) run over the frozen library's 38
  D-1 episodes must reproduce M1 / M2 / M3. Mapping asserted in advance: library M2 →
  `BLOCKED_BY_IDLE_TEAMMATE(ON_PLANT)`; library M1 → `BLOCKED_BY_IDLE_TEAMMATE(NOT_ON_PLANT)` when
  the blocker is idle, `BLOCKED_BY_WORKING_TEAMMATE` when it is not; library M3 (no peers at all) →
  `GOAL_FLIP` or `FIXED_TARGET_NO_BLOCKER` or `NO_TARGET` per F4, **which library transcripts do
  not carry** — so on library episodes M3 maps to "no blocker", and the telemetry split is not
  exercised by K2 and must not be claimed as validated by it. Every disagreement listed with its
  reason. This forces the classifier to be a function of `Trace` facts alone.
- **K3 swap-tick detector** — must fire on the 9 known `MANUFACTURED / swap` rows
  (`claude_1/narrate2/results/idle-adjudication-2026-08-23.json`, matched on game/turn/unit) and
  must be **silent** over the 290 tracked replays under `data/raw/games/` (agents 6536563 / 6536359,
  both seats), whose bot is held never to generate swaps. **The provenance of that premise is weaker than the
  card implies and I say so here rather than after the run:** `docs/RULES-LEDGER.md` R-1 records
  *"today's resident never generates them, which is self-imposed"* as of 2026-08-16 — a statement
  about the resident of that date, not a verified property of the 6536563 / 6536359 replays. So the
  negative side is a **joint** test of the detector and the premise: if it fires, the report says
  which of the two is being doubted and does not silently pick the convenient one. Both counts
  reported. A non-zero negative side does not become a footnote: it retires the class name.
- **K4 telemetry decode** — the v2 decoder's panel (`claude_1/narrate1/run_narrate_panel.py`)
  re-run on batches 1 and 2, and a v3 decode of batch 3. **Note for G-1:** the record has no
  standalone v3 *replay* decoder — v3 decoding currently lives inside
  `claude_1/narrate3/run_gp3_parity.py:67`. I will lift that grammar into
  `claude_1/dance1/narrate3_decode.py` unchanged in behaviour (`ABSENT` never folded into `NONE`,
  version token refused rather than guessed, game refused whole) and prove equivalence on the
  gp3 parity corpus before using it. Every refused game listed by reason; nothing partially decoded.
- **K5 exhaustiveness** — classes sum to the episode count per batch; each class exercised by a
  control or a real row, or reported EMPTY.
- **Determinism** — the results file byte-identical on a second run.

A vacuous pass is a failure: each control reports its number, and `PASS` prints only when every
control fired.

---

## 4. What this does not decide

No bug-versus-correct-caution ruling, no cure, no candidate, no behaviour change, no Arena action,
no prevalence claim beyond these three batches of one lineage, no statement about any opponent's
reasons. The classification says what happened; the owner rules on what it means, afterwards, if
at all.

## 5. The ruling I am asking for

`DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`, one wake. If revision is required I republish this
document and do not grade in the meantime. If the definitions turn out wrong on contact with the
data after acceptance, that is a G-1 revision published as such — not a boundary quietly moved once
the counts are visible.
