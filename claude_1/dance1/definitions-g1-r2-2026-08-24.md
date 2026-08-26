# G-1 definitions r2 — real-game dance attribution: the facts, the classes, the criteria

- Task: `20260824-real-game-dance-attribution`
- Author: claude_1 · Reviewer: codex_1 (gate G-1, second ruling) · Date UTC: 2026-08-24
- Supersedes: `claude_1/dance1/definitions-g1-2026-08-24.md` (r1, `agent/claude_1@3c87ab0b`),
  ruled **REVISION_REQUIRED** by `codex_1/reviews/real-game-dance-attribution-g1-2026-08-24.md`.
- Status: **PROPOSED — nothing has been counted.** No batch graded, no fact table built, no class
  assigned, no episode inspected, in r1 or in this revision.

## r2 changelog — what moved and why, before anything else

1. **R1 (blocking) repaired.** F3's population is narrowed to *peers alive at `turn_start`*, which
   is exactly what the imported `measure_blocker` enumerates
   (`build_oscillation_library.py:198`, `for p in st0.own_units()`). Later-appearing peers move to
   a new, separately-named fact **F3b**, which is **NEW** measurement and does not claim verbatim
   import. Their effect on blocker classification is stated: **none**, by construction — and the
   episodes where that matters are counted and published rather than left implicit (§1, F3/F3b).
2. **R2 (blocking) repaired.** A **mechanism layer** is defined (§2), computed from F3 alone with
   telemetry structurally unavailable, with an exact crosswalk to **all four** frozen classifier
   outputs including legacy `UNCLASSIFIED`. K2's pass is defined at that layer and telemetry is
   forbidden from touching it (§3, K2).
3. **The precedence changed, and the reason is a published refutation, not a peeked count.** r1 put
   `SWAP_FLAP` first, justified by the charter's hypothesis that the dance is swap-induced. The
   coordinator's `20260824T162800Z` policy refutes that hypothesis as an origin: the champion has
   no swap rule and dances at 16.8 % against the very-old bot's 17.4 %, +0.00 pts over 2,268 games.
   The justification for privileging swap is therefore gone, so the ordering is re-derived (§2.2).
   No class distribution exists for either ordering; the choice is still being made blind.
4. Four non-blocking requirements adopted verbatim (F5 clamp, telemetry-refusal accounting, K3
   joint premise, swap × blocker cross-tab) plus the coordinator's short-window question (§4).

Everything below is either a citation of already-accepted code or a definition stated in terms of
`Trace` facts. Anything the record does not already contain is marked **NEW**.

---

## 0. What an episode is (not new; the D-1 detector, unmodified)

An episode is one row emitted by `detect_d1`
(`claude_1/banana-restoration-r2/trace_detectors.py:555`) over a `Trace` from the accepted adapter
`claude_1/adapter1/replay_to_trace.py`. Verbatim predicate from the detector's docstring:

> exists own unit u, cells a != b, window `[t, t+2k]` with `k >= 3` (>= 7 states / >= 6 transitions),
> pos alternating a,b,a,b,...,a, and ZERO progress events for u inside the window. Progress events
> per A2: carry change / inv change on u's DROP-PICK turn / plant created-removed at u's cell.
> Own units only (A1).

Used **unmodified**. Own seat resolved from the replay's `agents` array by agent id, never by
listing position.

Carried caution on every number this task produces: **D-1 off replays is an upper bound.** Plant
clocks are reconstructed and the reconstruction error direction *invents* dancing. No count here
may be quoted without it.

---

## 1. Facts — observable, per episode, none judged

The fact table is complete before any class is computed and is published whole.

**F1 — the dancer.** Unit id; `speed`, `capacity`, `harvest_power`, `chop_power` at `turn_start`;
`carry` at `turn_start` and at `turn_end`.

**F2 — the window.** Cells `a`, `b`; `turn_start`, `turn_end`; window length in states; `k` as the
detector reports it.

**F3 — peers alive at `turn_start`.** *(narrowed in r2; verbatim import)* One record per own unit
other than the dancer that is present in `tr.state(turn_start).own_units()`, carrying exactly the
fields `measure_blocker` emits (`build_oscillation_library.py:185–238`): `cell_at_entry`, `stats`,
`carry_at_entry`, `distinct_cells_in_window`, `distinct_cells_to_game_end`,
`wait_fraction_in_window`, `non_wait_verbs_in_window`, `plant_on_cell_at_entry`,
`orth_adjacent_to_oscillation_cells`, `idle_by_analysis_criterion`.

The population is **the imported function's own population**, stated once and not restated
elsewhere: peers alive at `turn_start`. This is narrower than r1's "every other own unit alive in
the window" and the difference is real, not cosmetic.

The two criteria are reused **verbatim**:

- *IDLE* — `IDLE_WAIT_FRACTION = 0.95` (line 61), applied at lines 230–233 as
  `wait_fraction_in_window >= 0.95 and distinct_cells_in_window == 1`. The wait fraction counts
  turns on which `tr.cmd_of(peer, t) is None`, inclusive of both endpoints.
- *THE BLOCKER* — lines 234–238: `distinct_cells_in_window == 1` **and**
  `orth_adjacent_to_oscillation_cells`, adjacency being `orth()` (four-neighbourhood, line 180) of
  either dance cell measured against the peer's cell at `turn_start`. Lowest unit id wins ties. The
  criterion does **not** require the blocker to be idle; idleness is a separate flag.

Implementation requirement: the classifier **imports** `measure_blocker` and `IDLE_WAIT_FRACTION`
from `build_oscillation_library`. If import proves impossible (module-level side effects), the
panel prints that fact and a byte-level diff of the copied function, and G-1 is re-run.

*One property of the imported function I record rather than repair.* `measure_blocker` filters
`None` out of `cells_win` and counts a dead peer's absent command as a wait, so a peer alive at
`turn_start` that **dies mid-window** can read as a single-cell idle blocker. That is the accepted
function's behaviour and I do not change it. I add one **NEW** observable per F3 record,
`turns_alive_in_window` (count of turns in `[turn_start, turn_end]` with `tr.pos(peer, t)` not
`None`), which is a fact only: it enters no criterion and no class. Episodes whose selected blocker
has `turns_alive_in_window < window_length` are cross-tabbed in the report (§4). If that count is
material the report says so as a limitation of the inherited criterion; it does not silently
re-rule them.

**F3b — peers that appear later in the window.** **NEW**, and marked as new precisely because it is
not `measure_blocker`. One record per own unit other than the dancer that is **absent** from
`tr.state(turn_start).own_units()` but present in `tr.state(t).own_units()` for some
`t` in `(turn_start, turn_end]`: unit id, `first_turn_present`, `cell_at_first_presence`,
`distinct_cells_in_[first_turn_present, turn_end]`, `wait_fraction` over that same sub-range,
`orth_adjacent_to_oscillation_cells` evaluated at `cell_at_first_presence`, and a derived flag
`late_stationary_adjacent` = (`distinct_cells` == 1 **and** `orth_adjacent…`).

**How a later-appearing stationary adjacent peer affects blocker classification: it does not.** The
blocker is whatever imported `measure_blocker` returns over F3's population, full stop; F3b enters
no class predicate and cannot create, replace or veto a blocker. The alternative reading is kept
recoverable two ways: every such episode carries the sub-tag **`LATE_PEER_STATIONARY_ADJACENT`** on
its row, and the report publishes the count of episodes that (a) have `late_stationary_adjacent`
true and (b) received a no-blocker class, which is exactly the set of episodes a broader population
could have moved. If that set is non-empty it is named in the owner brief as a bounded sensitivity,
with its size, not folded into the headline.

**F4 — telemetry (the dancer's stated want).** Per turn in `[turn_start, turn_end]`, the dancer's
`chosen` target as `(kind, cell|None)` from the decoded NARRATE payload; on batch 3 also
`available` (v3's discarded best candidate). The raw per-turn sequence is kept on the row. The
summary label is **NEW**, defined over the sequence of `chosen` values:

- `NONE` — every turn's `chosen` is the bare `NONE` target.
- `CONSTANT` — every turn's `chosen` is one and the same non-`NONE` value.
- `ALTERNATING` — at least two distinct non-`NONE` values, no `NONE` present, and the sequence is
  periodic with period p, 2 <= p <= 4, over the whole window. Distinct targets and p stored.
- `MIXED` — anything else, including any window mixing `NONE` with a real target and any aperiodic
  multi-target sequence.
- `REFUSED` — **NEW in r2**: the episode's game did not decode whole. See K5 accounting below.

`ABSENT` (v3) is never folded into `NONE`; a window containing `ABSENT` for the dancer is `MIXED`
and the raw sequence shows it.

*Telemetry-refusal accounting (adopted from the review, non-blocking R-list).* A game whose
telemetry does not decode whole is refused whole by the decoders' existing fail-closed rule. Its
D-1 episodes are **not removed**: each becomes an episode-level fact row with F4 = `REFUSED`, a
refusal reason, and every non-telemetry fact (F1, F2, F3, F3b, F5, F6, F7) fully populated. Such
episodes remain in the detector total, are eligible for the mechanism-layer classes 1–3 (which do
not read telemetry), and land in `UNCLASSIFIED` with reason `TELEMETRY_REFUSED` only if no blocker
is present. "Refused whole" means no telemetry field is read for that game; it never means an
episode leaves the denominator.

**F5 — swap ticks.** **NEW.** For each turn `t` in the inspected range, a swap tick is an
**unordered pair** of own units `{u, v}` with `pos(u,t) = A`, `pos(v,t) = B`, `A != B`,
`pos(u,t+1) = B` and `pos(v,t+1) = A` — an exchange between **consecutive states**, both legs in
the same tick. Recorded: turn, pair, and whether the dancer is one of the two. Purely positional.

*Boundary clamp (adopted from the review).* The nominal range is `[turn_start - 2, turn_end]`; the
effective range is `[max(1, turn_start - 2), min(turn_end, tr.T - 1)]`. Turn indices run `1..tr.T`
(`trace_detectors.py:458`, and the module's own loops at lines 513 and 525 start at 1), so `1` is
the trace's first turn; the upper clamp exists because the predicate reads `t+1`. Every row carries
**`f5_inspected_range`** (the effective `[lo, hi]`) and **`f5_lookback_turns_available`** (0, 1 or
2). A truncated lookback is a stated property of that row, never a silent zero.

Two units passing through the same pair of cells on *different* turns cannot fire this: the
predicate reads a single transition and requires both units to move in it, in opposite directions,
between the same two cells. What it **cannot** distinguish is a resolver-issued swap from a
coincidental simultaneous exchange of two adjacent units — which is what K3 bounds, and if K3's
negative side is non-zero the class is renamed and re-ruled rather than reported.

**F6 — opponents.** Per turn in the window: any opponent unit standing on `a`, on `b`, on the
dancer's `chosen` target cell for that turn, or orthogonally adjacent to the dancer's own cell.
Stored per turn, summarised as a count of qualifying turns. No claim about opponents' reasons is
made anywhere in this task.

**F7 — how it ended.** The first event strictly after `turn_end`, the earliest of: a progress event
for the dancer under `detect_d1`'s own `progress()` definition; a peer that held one cell during the
window moving off it; a swap tick involving the dancer; the dancer's death; or game end with no such
event. Exactly one label per row, in that order of precedence, with the turn at which it fired.

---

## 2. Classes

### 2.1 The mechanism layer — F3 only, telemetry structurally absent (**NEW in r2**)

`mech(episode)` is a function of F3 alone: the imported `measure_blocker` over peers alive at
`turn_start`, and nothing else. It reads no telemetry, no swap tick, no opponent, no F3b. Exactly
one of five values:

| `mech` | predicate |
|---|---|
| `NO_PEERS` | `peers` is empty |
| `BLOCKER_IDLE_ON_PLANT` | blocker is not None, `idle_by_analysis_criterion`, `plant_on_cell_at_entry` non-null |
| `BLOCKER_IDLE_NO_PLANT` | blocker is not None, `idle_by_analysis_criterion`, no plant on its entry cell |
| `BLOCKER_WORKING` | blocker is not None, not `idle_by_analysis_criterion` |
| `PEERS_NO_BLOCKER` | `peers` non-empty and blocker is None |

Disjoint and exhaustive over the frozen function's own return shape. **Every episode row in every
pass carries `mech`**, including the no-telemetry champion pass. The crosswalk to the frozen
classifier's four outputs is in §3, K2.

### 2.2 The real-game classes — precedence 1–7, first match wins

Exhaustive and disjoint by construction: the seven predicates are evaluated in order, the first
that holds is assigned, class 7's predicate is constant-true. Co-occurring conditions stay on the
row as facts and are never folded into a second class.

1. **`BLOCKED_BY_IDLE_TEAMMATE`** — `mech` is `BLOCKER_IDLE_ON_PLANT` (sub-tag `ON_PLANT`, the
   library's M2 shape) or `BLOCKER_IDLE_NO_PLANT` (sub-tag `NOT_ON_PLANT`, idle-M1).
2. **`BLOCKED_BY_WORKING_TEAMMATE`** — `mech` is `BLOCKER_WORKING` (library working-M1).
3. **`SWAP_FLAP`** — no blocker; at least one F5 swap tick in which the dancer is one of the two.
4. **`GOAL_FLIP`** — no blocker; F4 is `ALTERNATING`.
5. **`FIXED_TARGET_NO_BLOCKER`** — no blocker; F4 is `CONSTANT`. Sub-tag `OPPONENT_ON_TARGET` when
   an opponent stands on the target cell for at least half the window's turns (F6).
6. **`NO_TARGET`** — no blocker; F4 is `NONE` throughout. On batch 3 `available` is consulted first:
   if the discarded best candidate is a real target on any window turn the episode is **not**
   `NO_TARGET` — it is `UNCLASSIFIED` with the `available` sequence on the row, because a want the
   picker saw and refused is a different thing from no want at all.
7. **`UNCLASSIFIED`** — everything else: facts published, no class asserted. Includes F4 `MIXED`
   with no blocker, F4 `REFUSED` with no blocker, and the batch-3 `available` case above.

**Classes 3–7 are always reported split by `mech` ∈ {`NO_PEERS`, `PEERS_NO_BLOCKER`}.** This is the
r2 repair of the second half of R2: the no-blocker classes no longer conflate "no peers existed"
with "peers existed and none qualified", even though both are legitimately no-blocker for the
real-game class. The split is mandatory in the table, not optional colour.

**Why the precedence changed.** r1 ranked `SWAP_FLAP` first because the charter's leading hypothesis
was that the survivor is swap-induced; the coordinator's `20260824T162800Z` policy refutes that as
an origin (the champion has no swap rule and dances at the very-old bot's rate). The remaining
reasons point the other way: the mechanism layer is the layer K2 validates against a frozen,
already-reviewed classifier, so aligning the real-game precedence with it means the two cannot
disagree by construction; and `SWAP_FLAP` is now the weaker predicate of the two, since F5 cannot
separate a resolver swap from a coincidental exchange while the blocker criterion is inherited and
reviewed. Both readings stay exactly recoverable: the report publishes the **swap × blocker
cross-tab** (§4), from which r1's ordering counts can be reconstructed cell for cell. I record
plainly that this is a boundary moved after r1 — moved on a published refutation, with no class
distribution in existence under either ordering.

Two properties stated as claims for codex_1 to attack rather than as facts:

- **Disjointness** is trivially true given first-match precedence; the *ordering* is the substantive
  choice, argued above.
- **Exhaustiveness** is by the catch-all, which is not a virtue. The numbers that matter are how
  many episodes land in 6 and 7 — the two places an inconvenient row could hide. Both are reported
  with full fact rows, not just counts.

Empty classes are reported as **EMPTY**, never merged away.

**Second pass (champion of record, 306 games / 382 episodes, no telemetry).** Classes 4, 5 and 6
collapse to a single `NO_TELEMETRY` class, reported as such. Classes 1, 2, 3, 7 and the whole
mechanism layer are computed identically, because none of them reads telemetry — so the pass
comparison the coordinator asked for is exactly the `mech` distribution plus classes 1–3, on
identical definitions. That pass does not begin until G-1 is accepted, and does not gate the first.

---

## 3. Controls, and what each is allowed to prove

- **K1 identity** — batch 1 must reproduce D-1 **22 episodes / 17 games**, D-2 0, D-3 0, exactly. A
  mismatch halts the task; it is not reconciled by adjusting the adapter.

- **K2 mechanism-layer reproduction of the frozen classifier** *(rewritten in r2)*. Run `mech` over
  the frozen library's 38 D-1 episodes and compare against the frozen `classify` label recorded for
  each. The crosswalk is total over **all four** frozen outputs:

  | `mech` | frozen `classify` output | frozen predicate that produces it |
  |---|---|---|
  | `NO_PEERS` | `M3` | `if not peers` (line-1 branch) |
  | `BLOCKER_IDLE_ON_PLANT` | `M2` | blocker idle **and** plant on entry cell |
  | `BLOCKER_IDLE_NO_PLANT` | `M1` | blocker present, falls through the M2 branch |
  | `BLOCKER_WORKING` | `M1` | blocker present, not idle |
  | `PEERS_NO_BLOCKER` | `UNCLASSIFIED` | `peers` non-empty and `blocker is None` |

  The crosswalk is a total function `mech -> legacy` (many-to-one: two `mech` values map to `M1`).
  **K2 passes only when, for all 38 episodes, `crosswalk(mech(e)) == frozen_label(e)`.** Every
  disagreement is listed with both labels and the deciding field. Three explicit prohibitions,
  written because each is a way this control could be made vacuous:
  1. **Telemetry may not enter K2 at any point.** The K2 panel asserts the telemetry input is
     absent before it runs, and F4 is not computed on the K2 path. A telemetry-bearing class can
     never turn a mechanism mismatch into a pass. The real-game class may use telemetry; K2's
     claimed reproduction is separate and exact.
  2. **`M3` is not broadened.** `M3` corresponds to `NO_PEERS` and to nothing else. r1's sentence
     "M3 maps to no blocker" is withdrawn as wrong: it silently merged `PEERS_NO_BLOCKER` into
     `M3`, which the frozen classifier calls `UNCLASSIFIED`.
  3. **The telemetry split is not exercised by K2** — library transcripts carry no telemetry — and
     must not be claimed as validated by it.

- **K3 swap-tick detector** — must fire on the 9 known `MANUFACTURED / swap` rows
  (`claude_1/narrate2/results/idle-adjudication-2026-08-23.json`, matched on game/turn/unit) and be
  **silent** over the 290 tracked replays under `data/raw/games/` (agents 6536563 / 6536359, both
  seats). **The premise is weaker than the card implies:** `docs/RULES-LEDGER.md` R-1 records
  *"today's resident never generates them, which is self-imposed"* as of 2026-08-16 — about that
  date's resident, not a verified property of those replays. The negative side is therefore a
  **joint** test of detector and premise: if it fires, the report names which of the two is in doubt
  and does not pick the convenient one. Both counts reported. **Any non-zero negative result
  prevents the causal name `SWAP_FLAP`**; the class is renamed to a purely descriptive
  `POSITIONAL_EXCHANGE` and re-ruled, not footnoted.

- **K4 telemetry decode** — the v2 decoder's panel (`claude_1/narrate1/run_narrate_panel.py`)
  re-run on batches 1 and 2, and a v3 decode of batch 3. There is no standalone v3 *replay* decoder;
  v3 decoding lives inside `claude_1/narrate3/run_gp3_parity.py:67`. I will lift that grammar into
  `claude_1/dance1/narrate3_decode.py` unchanged in behaviour (`ABSENT` never folded into `NONE`,
  version token refused rather than guessed, game refused whole) and prove equivalence on the gp3
  parity corpus before using it. Every refused game listed by reason; nothing partially decoded.

- **K5 exhaustiveness and refusal accounting** *(extended in r2)* — per batch, the classes must sum
  to the **detector's** episode count, with telemetry-refused episodes included in that sum under
  their non-telemetry class or `UNCLASSIFIED(TELEMETRY_REFUSED)`. The report prints, per batch:
  detector episodes, classified episodes, refused-telemetry episodes, and the identity
  `classes_total == detector_total`. Each class is exercised by a control or a real row, or reported
  EMPTY.

- **Determinism** — the results file byte-identical on a second run.

A vacuous pass is a failure: each control reports its number, and `PASS` prints only when every
control fired.

---

## 4. Required report tables (**NEW in r2**, from the review's non-blocking list and the charter)

The report is not free to omit these:

1. **swap × blocker cross-tab** — F5-dancer-swap present/absent against `mech`, all five values. It
   exists so `SWAP_FLAP` does not erase a co-occurring blocker mechanism from the owner brief, and
   so r1's precedence counts remain reconstructable.
2. **class × window length** — every class split at `k = 3` against `k > 3`. This is the
   coordinator's short-window question: whether `BLOCKED_BY_IDLE_TEAMMATE` absorbs episodes whose
   "blocker" is merely adjacent by coincidence for a 7-turn window. The library's criterion was
   written for long windows. Beside it, for class 1 and 2 rows, the distribution of the blocker's
   already-emitted `distinct_cells_to_game_end` — a peer that holds one cell for seven turns and
   then visits twenty is a different object from one that never moves, and that field measures the
   difference without adding a criterion. **No count is adjusted by this table**; it is the evidence
   for whether the inherited criterion is load-bearing at `k = 3`, reported for the owner's ruling.
3. **late-peer sensitivity** — episodes with `late_stationary_adjacent` true that received a
   no-blocker class (F3b), with size and rows.
4. **blocker liveness** — episodes whose selected blocker has `turns_alive_in_window` less than the
   window length (F3).
5. **mech split of classes 3–7** — `NO_PEERS` against `PEERS_NO_BLOCKER`, mandatory.

---

## 5. What this does not decide

No bug-versus-correct-caution ruling, no cure, no candidate, no behaviour change, no Arena action,
no prevalence claim beyond the batches actually graded, no statement about any opponent's reasons,
and — after the coordinator's refutation — **no origin claim for the dance at all**. The
classification says what happened; the owner rules on what it means, afterwards, if at all.

## 6. The ruling I am asking for

`DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`, one wake. If revision is required I republish and do
not grade in the meantime. If the definitions turn out wrong on contact with the data after
acceptance, that is a G-1 revision published as such — not a boundary quietly moved once the counts
are visible.
