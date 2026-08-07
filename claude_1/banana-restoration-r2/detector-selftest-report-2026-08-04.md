# Detector self-test report — banana restoration r2 trace detectors

Date: 2026-08-04. Deliverables under
`/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/`:
`trace_detectors.py` (library + CLI) and `test_trace_detectors.py`
(synthetic self-tests). Spec: `invariant-spec-2026-08-04.md`, sections
"0. Definitions and notation" and "Detector catalog (acceptance check 5)".
Protocol mirrored from `protocol-module-extract.rs` (completed from the
frozen parent `parent-a8eb3b2b.min.rs`, whose `read_turn` the extract
truncates mid-function); command grammar cross-checked against the parent's
emission sites and the harness `VALID_ARITIES`. Pure Python 3 stdlib,
deterministic (byte-identical report verified on rerun).

## 1. Unit-test suite

`python3 -m unittest test_trace_detectors -v` from the deliverable
directory: **23 tests, 23 passed, 0 failed, 0 errors** (~0.02 s).

Per detector, at least one synthetic TRIGGER and one NEAR-MISS trace, built
programmatically in the real stdin protocol format:

| Detector | Trigger | Near-miss (must NOT trigger) |
|---|---|---|
| D-1 | 10-turn a/b alternation, zero progress events (k=4) | same window WITH a carry-delta progress event inside (exempted); also a k=2 window (below k>=3) |
| D-2 | 2 PICK + 2 DROP at a door in 4 turns, net inv+carry zero | single PICK-then-DROP pair (legitimate seed abort) |
| D-3 | two own units share a MOVE destination 2 consecutive turns | shared destination for 1 turn only (resolver transient) |
| D-4 | CHOP during wood-committed interval; also 2 consecutive door-dist non-decreases | monotone door approach + DROP; also a single 1-turn stall (tolerated) |
| D-5 | PLANT BANANA at cheby 2 from tent; also plant at turn 299 > T_late=282 | early plant on a ring (diagonal) cell |
| D-6 | plant with opponent chopper at ETA 2 (<= 2) | same plant with opponent at ETA 7 |
| D-7 | harvested banana DROPped off-door (lost, inv unchanged) | harvested banana banked by DROP at a door |
| D-8 | CHOP standing on live own-planted diagonal mother | CHOP of own banana on an orthogonal wood slot (I-4 channel) |
| D-9 | PICK BANANA while \|own units\| = 1 before any TRAIN | TRAIN issued turn 1, banana command afterwards |

## 2. Real-game runs (packet.json.gz, current-lineage baseline traces)

`python3 trace_detectors.py --packet packet.json.gz --game-id N --report ...`
over 4 of the 25 packet rows (JSON reports saved next to this file as
`detector-report-<game>.json`):

| Game | Turns | D-1 | D-2 | D-3 | D-4 | D-5 | D-6 | D-7 | D-8 | D-9 | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 897833045 | 300 | FAIL (1 ep) | PASS | PASS | PASS | FAIL (2 ep) | PASS | PASS | PASS | PASS | FAIL |
| 897829892 | 262 | FAIL (1 ep) | PASS | PASS | PASS | PASS | FAIL (3 ep) | PASS | PASS | PASS | FAIL |
| 897832286 | 286 | FAIL (2 ep) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL |
| 897830203 | 300 | FAIL (1 ep) | PASS | PASS | PASS | FAIL (3 ep) | PASS | PASS | PASS | PASS | FAIL |

**These FAILs are EXPECTED and are evidence the detectors work.** The packet
rows are traces of the CURRENT bot, literally selected as liveness
counterexamples of the parent lineage (every row carries a
`baseline_maximum_period2` metric); period-2 oscillation is the known
inherited defect the restoration must fix. The detectors were NOT tuned to
make these games pass — the spec predicates are the truth.

Sample episodes (unit ids and turn ranges from the reports):

- D-1, game 897833045: unit 1 oscillates (6,1)<->(5,1), turns 36–45, k=4,
  zero progress events.
- D-1, game 897832286: unit 2 oscillates (6,4)<->(6,3) turns 160–286
  (k=63) — the packet's own `baseline_maximum_period2 = 128` for this row;
  D-1 reports the progress-event-free core of the same defect. Also unit 0,
  (8,0)<->(9,0), turns 45–56.
- D-1, game 897830203: unit 1, (10,9)<->(9,9), turns 262–300 (k=19), an
  endgame oscillator like the cited 269–280 counterexample window of game
  897829265 (that game is not in this packet).
- D-5, games 897833045/897830203: the current bot replants bananas on ring
  cells past the I-5 orthogonal cutoff (plants at turns 283–295 > T_late =
  282) — the baseline has no late-cutoff logic, exactly what B2/I-5 adds.
- D-6, game 897829892: unit 2/0 replant bananas with an opponent chopper at
  ETA 0–1 (turns 164–170) — the baseline has no plant-time enemy-ETA guard,
  exactly the factory failure mode I-10 closes.

D-2/D-3/D-4/D-7/D-8/D-9 pass on all four games: the baseline does not churn
the bank, contend targets across full turns, abandon wood returns, lose
harvested bananas, chop diagonal mothers relative to its own plants, or act
on bananas before TRAIN — consistent with those defects being specific to
the rejected factory wrapper, not the parent.

## 3. Strictest-reading ambiguity resolutions (A1–A11, also in docstrings)

1. **A1** D-1 evaluated for own units only (progress-event attribution
   needs our command stream; opponents have none).
2. **A2** D-1 progress events are exactly the spec list — carry delta,
   own-inventory delta on u's DROP/PICK turn, plant created/removed at u's
   cell — counted on transitions with both endpoints inside the window.
3. **A3** D-2 net-zero = element-wise equality of (own inventory + u's
   carry) between S_start and S_end+1; windows ending on the final turn
   (no post-state) are skipped.
4. **A4** D-3: `target(u,t)` telemetry does not exist in recorded traces;
   observable proxies used: identical MOVE destinations of two own units
   (doors included, per I-22 door-cell distinctness) >= 2 consecutive
   turns, and realized landing (next-state position) on a
   stationary-working peer >= 2 consecutive turns; a unit with no command
   counts as WAIT.
5. **A5** D-4 commitment starts on carry[WOOD] > 0 with MOVE destination in
   doors, DROP at a door, or forced free_capacity = 0 (I-21); death
   terminates as cargo loss, not violation.
6. **A6** D-5 "own banana" = cell whose banana plant has been continuously
   present since our PLANT command; cutoff chop_power = max own chop power
   at plant turn; global late cutoff t > 300 − (ceil(3/chop) + 1).
7. **A7** D-6(a) min own ETA over ALL own units (D-6/I-10 wording), not the
   I-7 wood-committed exclusion.
8. **A8** D-7 FIFO ledger; bank-PICKed bananas tracked with provenance and
   subject to the same age-12/loss rules; death while carrying = lost;
   end-carry excused only for harvest provenance in the final 6 turns.
9. **A9** D-8 chop target = plant on the chopping unit's own cell (the
   parent emits CHOP only when plant.cell == unit.cell).
10. **A10** D-9 literal: banana-attributable command (PLANT/PICK … BANANA)
    while |own units| = 1 before the first TRAIN is flagged even if training
    is infeasible (I-16's exemption is not in D-9's text); paired
    TRAIN-parity clauses run only with `--parent-commands-file`.
11. **A11** State/command turn-count mismatch truncates to the common
    prefix and is noted in the report (none occurred in the packet games).

All spec thresholds (k>=3; 12-turn D-2 window; 2-consecutive-turn D-3/D-4
bounds; |Ring| caps; I-5 cutoffs; ETA<=2 chopper bound; 6/12-turn D-7
bounds) are cited by detector/invariant id in comments at their use sites.
