# Phase 2 — P1+P2 built on BOTH bases, full gate battery, two ready-with-gates packages

- Task: `20260820-pair-selector-anti-benching` · Phase 2 (the owner's D1 + D2 rulings)
- Author: claude_1 · Reviewer: codex_1 (unified review of both packages **as one unit**)
- Date: 2026-08-20 · Replay: `python3 claude_1/picker2/run_gates.py`
- No Arena action taken. The queue slot is the owner's D3 ruling, not this package's business.

## The one-line verdict, before any number

**The bench is gone; the situations are mostly not cured.** P1+P2 removes the self-inflicted
deadlock on every ruled fixture that is red on its base, and the 240-game panel improves
substantially on both bases with **zero de-novo blocks**. But by the standing T-1 grader
(*detector silent AND progress restored*), the fix converts three of four cure-C fixtures into
**detector-quiet-but-still-stalled** — the exact outcome that grading rule was written to refuse.
That is a result, not a defect in the measurement, and it is stated first because it is the thing
a reader would otherwise take twenty minutes to discover.

## What was built

One patch generator, two subjects, per the card.

| base | subject sha256 | candidate | candidate sha256 |
|---|---|---|---|
| cure-C | `ad3bfefe4b2326f4…` | `claude_1/picker2/candidate-cureC-p1p2.rs` | `d127cf861ad7f145…` |
| door-1 | `547fa706cc1c684a…` | `claude_1/picker2/candidate-door1-p1p2.rs` | `5e1f4df406480f67…` |

**P1** — inside the existing two-unit pair loop, drop a pair in which one unit's command is a
`MOVE` onto a cell whose occupant is our own other unit *that the same pair orders to* `WAIT`.
**P2** — on an *exact* tie, prefer the pair with fewer `WAIT`s, replacing "first pair enumerated
wins", which is `BTreeMap` key order and was never designed. **Nothing else changed.**

`select()` gains one input, `unit_cells`, because the selector genuinely does not have positions
today; it is built at the existing call site from `my_units` before that Vec is moved, and there
is no other caller. The **>2-unit greedy fallback is deliberately untouched** and is named here
rather than quietly covered: the measured mechanism lives entirely in the two-unit pair arm.

### Builder guards, and the cross-base identity actually measured

`make_pair_selector_candidate.py` refuses an un-allowlisted subject digest, refuses any anchor
that does not match exactly once, and — after patching — recomputes the selection-region spans
and requires that **nothing outside them changed**. Two independent statements of "one patch":

- the **diff body** (every `-`, `+` and context line) is byte-identical across the two bases,
  sha256 `af8f710ce50336e3…`. The `@@` headers are excluded because they carry absolute line
  numbers and the door-1 base is 8 lines shorter by construction; both offset sets are printed
  rather than hidden.
- the **patched regions themselves** are byte-identical across bases (`select` block
  `61854e3c7c8ec1fc…`, 5054 bytes; assembly `298c3fbd6e2761e4…`, 2619 bytes). Step 0 measured
  them identical *before* the patch; they are identical *after* it. That is the property the
  dual-base ruling actually rests on.

## Gate 1 — fail-first: BENCHED on the base, EMPLOYED under the candidate

One probe builder taps **both** loop shapes, so *benched* means the same thing on the base and
under P1+P2: *the selector returned `WAIT` for the anchor unit while that unit's own candidate
list held at least one non-`WAIT` candidate*. Three gates run before any row is read — parity
against `regression_tests.run_binary_custom` on the uninstrumented arm, one `PS2TURN` block per
window turn with no gaps or duplicates, and **P1 observed firing** (a clause that never fires is
the inert check this programme has shipped before).

| base | fixture | benched on base | benched under P1+P2 | verdict |
|---|---|---|---|---|
| cure-C | OSC-004 | 12 | **0** | REPAIRED |
| cure-C | OSC-013 | 187 | **0** | REPAIRED |
| cure-C | OSC-017 | 194 | **0** | REPAIRED |
| cure-C | OSC-034 | 94 | **0** | REPAIRED |
| door-1 | OSC-004 | **0** | 0 | not red on this base |
| door-1 | OSC-013 | 187 | **0** | REPAIRED |
| door-1 | OSC-017 | 194 | **0** | REPAIRED |
| door-1 | OSC-034 | **0** | 0 | not red on this base |

**Two of the four ruled fixtures are not benched at all on the door-1 base.** The forecast hunk
already employs the unit there. Redness is therefore measured per base and never inherited; had
it been inherited, this package would have reported two failures against a fixture with nothing
to repair. P1 fired on every candidate arm (3, 5, 3, 1 dropped pairs on cure-C; 3, 9, 3, 2 on
door-1), so nothing below rests on a silent clause.

`gate_employment.py` is the uninstrumented cross-check on the command stream that actually
reaches the referee, and it agrees.

### The honest half of gate 1

Benched → 0 does **not** mean working. On cure-C OSC-013 the anchor unit is employed on 17 of 187
window turns and idle-with-nothing-offered on the other 170. The bench is gone because the pair
that caused it is gone; what the unit does with the freedom is a different question, and the
all-34 sweep below is where it is answered.

## Gate 2 — all-34 sweep, the standing FIXED grader

| base | FIXED on base | FIXED under P1+P2 | change |
|---|---|---|---|
| cure-C | 3 / 34 | **4 / 34** | +1 (OSC-034) |
| door-1 | 8 / 34 | **8 / 34** | 0 |

Per ruled fixture, `detector_silent` / `progress_restored`:

| fixture | cure-C base | cure-C P1+P2 | door-1 base | door-1 P1+P2 |
|---|---|---|---|---|
| OSC-004 | False / False | **True** / False | True / False | True / False |
| OSC-013 | False / False | **True** / False | False / False | **True** / False |
| OSC-017 | False / False | **True** / False | False / False | **True** / False |
| OSC-034 | False / False | **True / True** | True / True | True / True |

**P1+P2 silences the D-1 detector on every fixture it touches and restores progress on exactly
one.** Three of four cure-C fixtures land in *detector-quiet but stalled*, which the grading rule
inherited from `local_claude_1/t1-prediction-registry-2026-08-16.md` explicitly refuses to call
FIXED. No regression: no situation moved from FIXED to NOT FIXED on either base.

## Gate 3 — the 240-game panel against a matched floor

`check_floor_match.py` compares the candidate and floor **configs field by field** and the result
files' corpus provenance, excluding by name only the fields that must differ (which bot plays,
scratch paths, process count) and writing that exclusion list into the result. The cure-C floor is
**reused, not re-run** — `claude_1/chop4c/osc031-phase2-floor.json`, cure-C judged against itself
on this identical corpus — and the reuse is legitimate only because that check passes. The door-1
floor was run tonight. Both MATCHED.

| base | floor blocking | candidate blocking | change |
|---|---|---|---|
| cure-C | 53 / 240 | **33 / 240** | **−20** |
| door-1 | 43 / 240 | **35 / 240** | **−8** |

**Aggregate improves on both bases.** The aggregate is context, not the verdict: cure C taught
that lesson expensively when its aggregate improved while the per-game gate failed.

## Gate 4 — `(map_id, seat)` decomposition, both directions

| base | de-novo | healed | matched-corpus gate |
|---|---|---|---|
| cure-C | **0** | 20 | PASS (240 keyed games; floor stream byte-identical across arms) |
| door-1 | **0** | 8 | PASS (240 keyed games) |

A zero from a check never observed rejecting is worth nothing, so the direction carries its own
control: **swap the arms** and re-run the same `decompose()`. Every healed game reappears as
de-novo — 20 of 20 on cure-C, 8 of 8 on door-1, same keys. The de-novo bucket demonstrably fills
on this exact data with this exact code, so the real run's `0` is a measurement, not a silence.
It does **not** claim the candidate regresses nowhere outside these 240 keyed games.

## Every behaviour change NAMED, including the non-blocking ones

Zero de-novo games means "diagnose every de-novo game" would have produced an empty section. So
every keyed game where the candidate and its floor disagree on `block`, on which **property**
fired, or on **flags** is named instead — 24 of 240 on cure-C, 12 of 240 on door-1. Beyond the
healed blocks, four per base changed within an already-blocked game:

- **`m021` seat 1** (choke_corridor / idle), **both bases**: new property **P4** and a new
  report-tier flag **`r5-horizon`** — "full wood carrier since turn 12 never DROPs at a door
  within the bounded banking horizon of 30 turns". The game blocks under the floor as well, so it
  is not de-novo, but P1+P2 changed *how* it fails and that is on the record.
- **`m004` seat 0** (orchard_eligible / idle), **door-1 base only**: new property **P3**, first
  divergence turn 42 (`parent: MOVE 0 1 2;WAIT` vs `candidate: WAIT;CHOP 2`). This drops the
  door-1 arm's orchard-inertness count to 11 of 12.
  **P3 asserts the candidate's command stream is byte-equal to the parent's on orchard-eligible
  seat views.** P1+P2 is by design a command change, so P3 can be tripped by any real selector
  edit that happens to reach such a view; the cure-C arm passing 12 of 12 is luck, not principle.
  **Whether P3 is applicable to an intentional selector change is a ruling, and it is not mine.**
  It goes to codex_1's review and, if he judges it a design question, to the owner.
- `m003`/`m090`/`m099` (cure-C) and `m070`/`m099` (door-1): detector-count changes inside games
  that block under both arms, no new property, no new flag.

## Gates 5 and 6 — latency and parity

P1 adds a per-pair call in the hot loop; the card said measure it, not argue it. All four arms,
760 warm turns each, `latency_probe.timed_run` imported rather than restated:

| arm | median | p95 | max | budget | verdict |
|---|---|---|---|---|---|
| cure-C base | 0.0567 ms | 0.0730 ms | 0.1161 ms | 50 ms | MET |
| cure-C P1+P2 | 0.0518 ms | **0.0750 ms** (+0.0020) | 0.1449 ms | 50 ms | MET |
| door-1 base | 0.0561 ms | 0.0725 ms | 0.1240 ms | 50 ms | MET |
| door-1 P1+P2 | 0.0611 ms | **0.1341 ms** (+0.0616) | 0.2071 ms | 50 ms | MET |

The p95 cost is under two tenths of a millisecond against a 50 ms budget. **Limit, stated:** the
candidate and base arms play different games once P1 diverges, so the delta compares two
trajectories, not the same turns; and this is four situations on an unloaded host, not the corpus.

**Process-count parity**: the cure-C candidate's 240 rows at 8 processes vs 1 process —
**8160 field comparisons across 34 fields, IDENTICAL**. (`attempt` is excluded by the inherited
tool and the exclusion is printed by it.)

## What this package does NOT claim

- It does not claim either candidate CURES the benching situations. On the standing grader it
  cures **one of four** on cure-C and adds none on door-1.
- It does not claim the 235 non-deadlock benched turns from Phase 1 (OSC-002, OSC-001, OSC-029,
  OSC-031) are addressed. They are out of scope by design and remain so.
- It does not claim P3 is wrong to fire on `m004`. It claims P3 is structurally reachable by any
  intentional command change and asks for a ruling.
- It does not rank the two bases. Which base wins the title is the night tree's verdict, and the
  queue slot is the owner's D3 ruling.
- Nothing here was run against the Arena.

## Artifacts

| path | what |
|---|---|
| `make_pair_selector_candidate.py`, `p1p2.diff`, `build-manifest-2026-08-20.json` | one generator, two subjects, cross-base identity |
| `candidate-{cureC,door1}-p1p2.rs` | the two candidates |
| `make_probe.py`, `probe-*.rs`, `probe-manifest-2026-08-20.json` | one probe builder, both loop shapes |
| `gate_bench.py`, `gate1-bench-2026-08-20.json` | fail-first BENCHED gate, parity + coverage + P1 liveness |
| `gate_employment.py`, `gate1-employment-2026-08-20.json` | uninstrumented cross-check |
| `sweep34-*.json` | all-34 sweep, four arms |
| `panel-*.json` / `.md`, `claude_1/pipeline/picker2-*-config.json` | the four 240-game panels |
| `check_floor_match.py`, `floor-match-2026-08-20.json` | the reused floor is this candidate's floor |
| `decomposition-{cureC,door1}-2026-08-20.json` | `(map_id, seat)` decomposition |
| `denovo_direction_control.py`, `denovo-direction-control-2026-08-20.json` | the de-novo direction is observable |
| `named_changes.py`, `named-changes-2026-08-20.json` | every behaviour change, named |
| `parity-cureC-2026-08-20.json`, `latency-2026-08-20.json` | process parity, latency |
| `run_gates.py`, `gate-battery-run-2026-08-20.json` | the whole battery in one command |
