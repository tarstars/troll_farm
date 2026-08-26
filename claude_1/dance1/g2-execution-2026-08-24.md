# G-2 execution — real-game dance attribution: 462 episodes graded, both passes, six controls

- Task: `20260824-real-game-dance-attribution`
- Author: claude_1 · Reviewer: codex_1 (gate G-2) · Date UTC: 2026-08-24
- Definitions of record: `claude_1/dance1/definitions-g1-r3-2026-08-24.md`, ruled
  **DEFINITIONS_ACCEPTED** by `codex_1/reviews/real-game-dance-attribution-g1-r3-2026-08-24.md`
  (`20260824T172730Z`). Nothing in this document changes a definition.
- Status: **executed, controls PASS.** No bug ruling, no cure, no candidate, no Arena action.

**The caution that travels with every number below, and may not be dropped when one is quoted:
D-1 off replays is an UPPER BOUND.** The accepted adapter reconstructs plant clocks and the
reconstruction error direction *invents* dancing rather than hiding it. Every episode count here
is "at most this many".

---

## 0. What changed against the accepted definitions, before any count is read

**Class 3 is not called `SWAP_FLAP`. It is called `POSITIONAL_EXCHANGE`.** The definitions §3 K3
pre-committed that remedy — "any non-zero negative result prevents the causal name `SWAP_FLAP`;
the class is renamed to a purely descriptive `POSITIONAL_EXCHANGE` and re-ruled, not footnoted" —
and K3's negative side is **not** silent. The panel therefore runs K3's negative side **first, over
a corpus that contains none of the graded episodes**, resolves the name, and only then grades. No
code path can set that name from a class distribution; the resolved name is recorded in the
results file as `class_3_name_in_force`. The numbers below were produced under the descriptive
name from the first graded row onward, not renamed afterwards.

Two implementation choices that are **stronger** than what the definitions promised, both stated
rather than buried:

1. §3 K4 said I would *lift* the v3 payload grammar out of `run_gp3_parity.py` into
   `claude_1/dance1/narrate3_decode.py` and prove equivalence. I **import** it instead and never
   copy it, under an asserted source SHA-256 (`0537741d…f293bf`). A copy proved equivalent once can
   drift between the proof and the use; an import cannot. Same discipline §1 already required of
   `measure_blocker`.
2. A sixth control, **K0**, was added: the `progress()` re-statement that F7 needs must report *no*
   progress event on every transition strictly inside every window `detect_d1` emitted — the
   detector's own predicate. It fired on 462 transitions with 0 disagreements. K0 is a self-check,
   not a replacement for any defined control.

---

## 1. Provenance — what was graded, and its digest

| corpus | rows | source, pinned | package SHA-256 (verified against the shipping manifest) |
|---|---|---|---|
| batch 1 | 149 replays, agent 6652424, NARRATE v2 | `local_claude_1/narrate/games/` @`3256dafb` | 149 files, concatenation `1f60b3be…0397e` |
| batch 2 | 160 replays, agent 6652602, NARRATE v2 | `local_claude_1/narrate/read2/…jsonl.gz` @`3256dafb` | `84f46acb…18897` ✔ manifest |
| batch 3 | 160 replays, agent 6652642, NARRATE v3 | `local_claude_1/narrate/v3/…jsonl.gz` @`3256dafb` | `01169944…c3ceb` ✔ manifest |
| champion | 306 replays, door-1 lineage, 16 agent ids, **no telemetry** | `local_claude_1/dance-lineage/door1-games/` @`4b9bd563` | `57832fd9…95d227` ✔ manifest |

The champion package's episode list of record (`episodes-door1.json`, `d365855e…b58bee`, 382 rows)
was reproduced **exactly**: the panel's own `detect_d1` run over the 306 sanitised replays emitted
382 episodes and the `(game, unit, turn_start, turn_end)` key sets are equal — 382 matched, 0 only
here, 0 only in the record. That is an identity check, not a claim about the champion's play.

No battle listing exists for the champion agents; none is claimed and none was reconstructed. No
Arena action, submission, TestSession, fetch, sealed-map access or resident mutation occurred; the
resident's SHA-256 is unchanged.

---

## 2. The controls — every one fired, with its number

| control | number it fired on | result |
|---|---|---|
| **K0** progress() agreement with `detect_d1` | 462 in-window transitions | 0 disagreements — **PASS** |
| **K1** batch-1 detector identity | D-1 22 / 17 games, D-2 0, D-3 0 | exact — **PASS** |
| **K2** mechanism-layer reproduction of the frozen classifier | 38 D-1 episodes over 30 frozen situations | 0 mismatches — **PASS** |
| **K3** swap-tick detector | positive 9/9; negative 3,256 ticks over 141 pairs | remedy applied — see §2.1 |
| **K4** telemetry decode | 469 games, 0 refused | **PASS** |
| **K5** exhaustiveness | 4 batches, `classes_total == detector_total` in all four | **PASS** |
| determinism | second run, separate output directory | byte-identical — see §6 |

**K2 in full.** `mech` was computed from each frozen situation's own `all_own_peers_at_entry` /
`blocker` records — the exact return shape of the imported `measure_blocker` — and crosswalked to
the frozen `classify` output. All 38 agree: `BLOCKER_IDLE_ON_PLANT` 14 → `M2` (frozen `M2` 14),
`BLOCKER_IDLE_NO_PLANT` 3 + `BLOCKER_WORKING` 8 → `M1` (frozen `M1` 11), `PEERS_NO_BLOCKER` 4 →
`UNCLASSIFIED` (frozen 4), `NO_PEERS` 1 → `M3` (frozen 1). The library copy is named explicitly —
`oscillation-library-98628e98/library` — because the repository holds three copies and only that
one carries the 38 episodes the definitions name; the top-level `oscillation-library/` carries 36
and `oscillation-library-547fa706/library` carries 27. **The prohibition held**: the panel asserts
no telemetry field exists anywhere in the frozen situations and found none, so no telemetry-bearing
class could have turned a mechanism mismatch into a pass even in principle.

### 2.1 K3, and why class 3 lost its causal name

- **Positive side: 9 of 9.** Every `MANUFACTURED / swap` row in
  `claude_1/narrate2/results/idle-adjudication-2026-08-23.json` is reproduced by the F5 predicate
  at the recorded turn. The detector detects.
- **Negative side: not silent, and not close.** Over `data/raw/games/`, our pre-cure lineage
  (agents 6536563 / 6536359, both seats) supplies **141 game × seat pairs** — not 290; 290 is the
  replay count and only 141 of the 580 game × seat pairs are ours, which the definitions' phrasing
  elided and which I state rather than round. The F5 predicate fires **3,256 times in 132 of those
  141 pairs**. 0 adapter refusals.
- **Which of the two is in doubt — I do not pick.** One NEW diagnostic is published because it
  bears on the question and on nothing else: of the 3,256 ticks, **1,597 (49 %)** are turns where
  *both* units carried a `MOVE` command onto each other's cell, and 1,659 are not. The first shape
  is what a resolver-issued exchange would look like; the second is what two adjacent units
  coincidentally trading places would look like. **Neither shape proves intent**, and the
  diagnostic enters no predicate and no class. The two readings the record must keep open are:
  (a) the F5 predicate is far too broad to name a mechanism, or (b) `docs/RULES-LEDGER.md` R-1's
  premise — "today's resident never generates them, which is self-imposed", written 2026-08-16
  about *that day's* resident — is not a property of the pre-cure lineage that played these replays. The evidence above is
  consistent with both, and the 49 % split is the reason I will not choose between them here.
- **Consequence, applied not footnoted:** class 3 is `POSITIONAL_EXCHANGE` on both passes. Nothing
  in this document says the dance is swap-induced, and the class name no longer implies it.

---

## 3. The instrument pass — 469 games, 80 episodes

Batch counts, per the detector, before any class:

| batch | games | D-1 episodes | games with ≥1 episode | share of games | D-2 | D-3 |
|---|---|---|---|---|---|---|
| batch 1 (v2, 6652424) | 149 | 22 | 17 | 11.4 % | 0 | 0 |
| batch 2 (v2, 6652602) | 160 | 24 | 18 | 11.3 % | 0 | 0 |
| batch 3 (v3, 6652642) | 160 | 34 | 30 | 18.8 % | 0 | 0 |
| **total** | **469** | **80** | **65** | **13.9 %** | **0** | **0** |

Batch 3 reads higher than batches 1 and 2 (18.8 % of games against 11.4 % and 11.3 %). **I do not
report that as a difference between the instruments.** The three batches are different
submissions played on different ladder days against different opponents, the corpora were not
randomised, and nothing here controls for that; it is one number beside another number.

### 3.1 The classes

| class | count | of 80 |
|---|---|---|
| `BLOCKED_BY_IDLE_TEAMMATE` | **EMPTY** | 0 % |
| `BLOCKED_BY_WORKING_TEAMMATE` | 34 | 42.5 % |
| `POSITIONAL_EXCHANGE` (class 3) | 3 | 3.8 % |
| `GOAL_FLIP` | **EMPTY** | 0 % |
| `FIXED_TARGET_NO_BLOCKER` | 22 | 27.5 % |
| `NO_TARGET` | **EMPTY** | 0 % |
| `UNCLASSIFIED` | 21 | 26.3 % |

Per batch: batch 1 — 6 / 5 / 1 / 10 (working / fixed-target / exchange / unclassified); batch 2 —
13 / 6 / 1 / 4; batch 3 — 15 / 11 / 1 / 7. Three classes are EMPTY and are reported EMPTY, not
merged away.

**The mandatory `mech` split of the no-blocker classes.** All 46 no-blocker episodes are
`PEERS_NO_BLOCKER`; `NO_PEERS` is **0**. Every one of the 80 episodes has **exactly one** peer
alive at `turn_start` — this is a two-unit team throughout — so "no peer existed" never happens on
this pass and the class 3–7 rows cannot be hiding a lone-unit population.

**Where the ambiguous rows went, which is the thing the reviewer said to aim at.** 21 episodes are
`UNCLASSIFIED` and every one of them is the same shape: no blocker, F4 = `MIXED`. `NO_TARGET` is
empty — **there is no episode in which the dancer wanted nothing.** Of the 36 `MIXED` windows, 30
contain no `NONE` turn at all and 31 carry **two or more distinct real targets** inside the window
(28 windows show 2 distinct values, 8 show 3). So the honest description of `UNCLASSIFIED` here is
not "we could not tell": it is **the dancer's stated want changed during the window, but not with
the clean period-2-to-4 alternation `GOAL_FLIP` requires.** `GOAL_FLIP` is empty because that tidy
shape does not occur, not because target churn does not occur.

**Telemetry refusals: zero.** 469 of 469 games decoded whole, so no episode is in `UNCLASSIFIED`
for the reason `TELEMETRY_REFUSED`, and K5's identity holds without that term.

**The v3 `available` question.** All 34 batch-3 episodes carry at least one window turn on which
the discarded best candidate was a real target — but that only diverts an episode out of
`NO_TARGET`, and `NO_TARGET` is empty, so it moved nothing. The number that matters and is
published for the owner: on exactly **2 window turns** across all 34 batch-3 episodes did the
picker record `chosen = NONE` while `available` was a real target. The v2 blind spot the v3
instrument was built to see into is, on these episodes, nearly empty.

### 3.2 Required table — swap × blocker cross-tab (so class 3 erases nothing)

| | `BLOCKER_WORKING` | `PEERS_NO_BLOCKER` |
|---|---|---|
| dancer in ≥1 swap tick | 8 | 3 |
| no dancer swap tick | 26 | 43 |

**11 of 80 episodes contain a dancer swap tick; only 3 carry class 3**, because 8 of them have a
blocker and the blocker classes come first. This is exactly the cell-for-cell reconstruction the
definitions promised: under r1's rejected ordering (swap first) class 3 would have held **11**
episodes and `BLOCKED_BY_WORKING_TEAMMATE` **26**. Both readings are in the record; neither is the
headline.

### 3.3 Required table — class × window length (the coordinator's short-window question)

| class | k = 3 | k > 3 |
|---|---|---|
| `BLOCKED_BY_WORKING_TEAMMATE` | 11 | 23 |
| `FIXED_TARGET_NO_BLOCKER` | 12 | 10 |
| `UNCLASSIFIED` | 11 | 10 |
| `POSITIONAL_EXCHANGE` | 0 | 3 |

34 of 80 episodes are the minimum-length `k = 3` window. Beside it, the evidence the coordinator
asked for — the selected blocker's `distinct_cells_to_game_end`, which asks whether a "blocker" is a
unit that genuinely never moves or one that merely stood still for seven turns:

- at `k = 3` (11 blocked episodes): the blocker later visits 7, 9, 22, 26, 32 (×4), 36, 39 and 40
  distinct cells. **Not one of them is a unit that stays put.**
- at `k > 3` (23 blocked episodes): 10 blockers visit **exactly one cell for the entire game**, 8
  visit 2, and the rest 4 to 36.

**No count is adjusted by this table.** It is the evidence for the owner's ruling on whether the
inherited criterion is load-bearing at `k = 3`, and my reading of it — offered as a reading, not a
measurement — is that the short-window blocked episodes are a materially different object from the
long-window ones, and that a future definition may want to say so.

### 3.4 Required tables — late-peer sensitivity and blocker liveness

Both are **empty, and empty is the informative answer**: 0 episodes have a later-appearing
stationary adjacent peer (F3b is empty throughout — with one peer alive at entry and a two-unit
team there is nobody to arrive), and 0 episodes have a blocker that died mid-window. The
inherited criterion's dead-peer artefact, which r2 recorded rather than repaired, **did not fire
once** on either pass. It cost the headline nothing.

### 3.5 How the dances ended (F7)

`DANCER_PROGRESS` 52, `HOLDING_PEER_MOVED` 16, `GAME_END_NO_EVENT` 9, `SWAP_TICK_WITH_DANCER` 3.
The dance is overwhelmingly self-terminating within the game; 9 of 80 ran to the final turn.

---

## 4. The champion pass — 306 games, 382 episodes, no telemetry

Classes, under the r3 precedence (1–3 then `NO_TELEMETRY` for every remaining row):

| class | count | of 382 |
|---|---|---|
| `BLOCKED_BY_IDLE_TEAMMATE` | 16 | 4.2 % |
| `BLOCKED_BY_WORKING_TEAMMATE` | 146 | 38.2 % |
| `POSITIONAL_EXCHANGE` | 14 | 3.7 % |
| `NO_TELEMETRY` | 206 | 53.9 % |
| `GOAL_FLIP` / `FIXED_TARGET_NO_BLOCKER` / `NO_TARGET` / `UNCLASSIFIED` | **n/a (no telemetry)** | — |

The four instrument-only rows are marked `n/a (no telemetry)` and never `0`, exactly as the
definitions require: a zero would assert that a predicate ran and found nothing.

`mech` split of the no-blocker classes: `NO_TELEMETRY` — `PEERS_NO_BLOCKER` 201, `NO_PEERS` 5;
`POSITIONAL_EXCHANGE` — `PEERS_NO_BLOCKER` 13, `NO_PEERS` 1. Swap × blocker: 23 of 382 episodes
contain a dancer swap tick, of which 9 have a working blocker, 1 has no peers and 13 have peers and
no blocker — so class 3 again reports 14 where a swap-first ordering would report 23.

F7: `DANCER_PROGRESS` 218, `HOLDING_PEER_MOVED` 75, `GAME_END_NO_EVENT` 79, `SWAP_TICK_WITH_DANCER`
10. Late-peer sensitivity 0 rows; blocker liveness 0 rows.

## 4.1 The cross-corpus comparison — `mech` and classes 1–3, the same layer on both sides

This is the only comparison the definitions permit between the two passes, and it is exact: same
imported function, same population, same fields, no telemetry on either side.

| `mech` | instrument (80) | champion (382) |
|---|---|---|
| `BLOCKER_IDLE_ON_PLANT` | 0 — 0.0 % | 3 — 0.8 % |
| `BLOCKER_IDLE_NO_PLANT` | 0 — 0.0 % | 13 — 3.4 % |
| `BLOCKER_WORKING` | 34 — 42.5 % | 146 — 38.2 % |
| `PEERS_NO_BLOCKER` | 46 — 57.5 % | 214 — 56.0 % |
| `NO_PEERS` | 0 — 0.0 % | 6 — 1.6 % |

**The two corpora agree on the shape of the mechanism** — a working blocker in roughly four
episodes in ten, no qualifying blocker in roughly five and a half — and disagree only on the idle
blocker, which is 0 % on one side and 4.2 % on the other. On the champion side 6 episodes have no
peer alive at entry at all, which cannot happen on the two-unit instrument.

I am **not** reporting the 42.5 % vs 38.2 % gap as a difference. Different lineages, different
ladder days, different opponents, no randomisation, and the D-1 upper-bound caution applies to both
numerators.

---

## 5. What the blocker actually is, on both passes — the finding I did not expect

`BLOCKED_BY_IDLE_TEAMMATE` is **empty across 469 instrument games** and holds 16 of 382 champion
episodes. The mechanism the entire frozen oscillation library was built around — 14 of its 38
episodes are `M2`, the idle occupier standing on a live plant — is essentially **absent from real
games**. What replaces it, measured from the already-emitted fields:

- **Instrument (34 blocked episodes):** the blocker's wait fraction is **0.00 in 33 of 34** — it is
  working every single turn. **24 of 34 are standing on a plant** while doing so, and the commonest
  verb sets are `CHOP+DROP+PICK+PLANT` (12) and `CHOP+MOVE` (11). **10 of 34 never leave that cell
  for the rest of the game.**
- **Champion (162 blocked episodes):** 101 of 162 stand on a plant; **73 of 162 never leave the
  cell for the rest of the game**; the idle tail is real but small (16 episodes at wait fraction
  ≥ 0.9).

So the real-game shape is: *a teammate parked on a plant, working it, indefinitely, orthogonally
adjacent to the two cells the dancer is bouncing between.* The library's IDLE criterion —
`wait_fraction >= 0.95 and distinct_cells_in_window == 1` — **cannot see it**, because the peer is
not waiting. It is the M2 geometry with the M2 idleness test failing.

Stated with the boundary it deserves: this is a description of what the fact table contains, not a
causal claim. It says the criterion inherited from the fuzz-panel library sorts real games into a
different bin than it sorts panel games; it does not say the resolver is wrong, and I make no
bug ruling here.

---

## 6. Reproduction, determinism, artefacts

    python3 claude_1/dance1/run_dance_panel.py --inputs <inputs>

with `<inputs>` populated from the pinned commits in §1. The panel writes three files. The whole
panel was re-run over the same inputs into a separate output directory and all three are
**byte-identical**, recorded in `claude_1/dance1/results/determinism-2026-08-24.json`:

| artefact | rows | SHA-256 (identical on both runs) |
|---|---|---|
| `results/dance-panel-2026-08-24.json` | counts, tables, all six controls | `dc3286f3…8560a` |
| `results/dance-facts-instrument-2026-08-24.json` | 80 episodes, every fact F1–F7 | `7cd3631c…937b6` |
| `results/dance-facts-champion-2026-08-24.json` | 382 episodes, every non-telemetry fact | `55562205…b43e627` |

Code: `claude_1/dance1/dance_facts.py`, `dance_controls.py`, `run_dance_panel.py`,
`narrate3_decode.py`. The fact table is published **whole** — all 462 rows, every peer record,
every per-turn telemetry sequence, every swap tick — so any reader can re-derive every count in
this document, or apply a different rule and see what it costs.

---

## 7. What this does not decide

No bug-versus-correct-caution ruling. No cure, no candidate, no behaviour change, no Arena action,
no prevalence claim beyond the four corpora actually graded, no statement about any opponent's
reasons, and — after the coordinator's `20260824T162800Z` refutation and K3's negative result —
**no origin claim for the dance at all.** The classification says what happened; the owner rules on
what it means, afterwards, if at all.
