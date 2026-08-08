# Detector bite-test audit — what D-1..D-9's trigger/near-miss pairs actually prove

Date: 2026-08-08. Agent: `claude_1`, Phase 1 item 4. Branch
`agent/claude_1-banana-restoration-r2`.

Scope: **audit only.** No detector, gate, candidate, parent, `.min.rs`,
`trace_detectors.py`, `test_trace_detectors.py` or `fuzz_panel.py` was
modified. Every mutation described below was applied to a **scratch copy**
under `/tmp/.../scratchpad/audit/` and discarded; the deliverable directory
is byte-identical to `origin/agent/claude_1-banana-restoration-r2` apart
from this file.

Artifacts audited:

- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/trace_detectors.py`
- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/test_trace_detectors.py`
- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/conversion_race_oracle.py`
- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/detector-selftest-report-2026-08-04.md`
- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/invariant-spec-2026-08-04.md`
- `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/design-banana-fsm-2026-08-06.md`

Baseline confirmed before any mutation: `python3 -m unittest
test_trace_detectors` in the deliverable directory — **28 tests, OK, 0.016 s**.
Identical result from the pristine scratch copy.

---

## 0. The standard applied, and the headline

Three questions, per the task framing:

1. **Implementation validity** — does the detector obey its spec? This is
   what a bite-test measures.
2. **Calibration validity** — does the detector agree with the parent?
   This is what floor silence measures.
3. **Truth validity** — does the spec describe the real property?
   **Neither of the first two can establish this.**

Governing finding (`chatgpt_1`, GAR-3): *"a fixture built from the same
predicate faithfully tests the wrong predicate."* D-9 passed both its
bite-tests perfectly while emitting 196 false positives.

**Headline of this audit:** the GAR-3 pattern is not confined to D-9. It is
reproduced, with numbers, for **D-6**: the repo's own
`founding_safety_oracle` (review F4, `conversion_race_oracle.py:385-439`)
judges the D-6 **near-miss** — the trace asserted to be *clean* — as
**unsafe on two independent grounds**, while `detect_d6` returns
`("PASS", 0)`. D-6 is implementation-valid and, measured against the only
independent oracle in the directory, wrong. Section 4 gives the arithmetic.

Second headline: of 64 mutations of detector constants/thresholds/clauses,
**20 were caught and 44 survived** (kill rate 31 %). The survivors are not
scattered — they cluster on exactly the conjuncts the fixtures never vary.

---

## 1. Mutation experiment — method and full results

**Method.** `pristine/` = verbatim copies of `trace_detectors.py`,
`conversion_race_oracle.py`, `test_trace_detectors.py`. For each mutant: copy
`pristine/` → `work/`, apply one textual substitution (asserted to match
exactly once — three initial patches matched 0 or 2 sites and were re-anchored,
none silently applied), import-check, then run (a) the detector's own test
class and (b) the whole 28-test suite in `work/`. `CAUGHT` = the pair's own
tests fail. `SURVIVED` = the pair still passes. The whole-suite column never
differed from the focused column: **no mutation was caught by a different
detector's tests**, so every number below is attributable to the pair under
audit.

Runner: `/tmp/.../scratchpad/audit/mutate.py` (+`mutate2..4.py`); merged
results `/tmp/.../scratchpad/audit/mutation-results-merged.json`.

| Det | caught | survived | kill rate |
|---|---|---|---|
| D-1 | 2 | 6 | 25 % |
| D-2 | 2 | 4 | 33 % |
| D-3 | 2 | 2 | 50 % |
| D-4 | 2 | 4 | 33 % |
| D-5 | 2 | 6 | 25 % |
| D-6 | 2 | 7 | 22 % |
| D-7 | 1 | 7 | **12.5 %** |
| D-8 | 6 | 5 | 55 % |
| D-9 | 1 | 3 | 25 % |
| **all** | **20** | **44** | **31 %** |

Full ledger (survivors are the finding):

| id | det | result | mutation |
|---|---|---|---|
| D1-M1 | D-1 | CAUGHT | `>= 6` transitions → `>= 4` (k>=3 → k>=2) |
| D1-M2 | D-1 | SURVIVED | `>= 6` → `>= 8` (k>=3 → k>=4) |
| D1-M3 | D-1 | CAUGHT | carry-delta progress event deleted |
| D1-M4 | D-1 | SURVIVED | plant-appear/disappear progress event deleted |
| D1-M5 | D-1 | SURVIVED | inventory-delta progress event deleted |
| D1-M6 | D-1 | **SURVIVED** | **A≠B≠A period-2 shape requirement deleted** |
| D1-M7 | D-1 | SURVIVED | `>= 6` → `>= 5` |
| D1-M8 | D-1 | SURVIVED | `>= 6` → `>= 9` |
| D2-M1 | D-2 | CAUGHT | 12-turn window → 3 |
| D2-M2 | D-2 | SURVIVED | 12-turn window → 120 |
| D2-M3 | D-2 | CAUGHT | `picks < 2 or drops < 2` → `< 1` |
| D2-M4 | D-2 | SURVIVED | door-cell restriction deleted |
| D2-M5 | D-2 | SURVIVED | net-zero requirement deleted |
| D2-M6 | D-2 | SURVIVED | 12-turn window → 4 |
| D3-M1 | D-3 | CAUGHT | `len(run) >= 2` → `>= 1` |
| D3-M2 | D-3 | CAUGHT | `len(run) >= 2` → `>= 3` |
| D3-M3 | D-3 | SURVIVED | clause (b) landing-on-working-peer disabled |
| D3-M4 | D-3 | SURVIVED | shared-target proxy widened to include WAIT |
| D4-M1 | D-4 | CAUGHT | `nd_run == 2` → `== 1` |
| D4-M2 | D-4 | SURVIVED | `nd_run == 2` → `== 3` |
| D4-M3 | D-4 | SURVIVED | `d1 >= d0` → `d1 > d0` |
| D4-M4 | D-4 | CAUGHT | banned-verb set reduced to `{MINE}` |
| D4-M5 | D-4 | SURVIVED | forced (full-capacity, I-21) commitment start deleted |
| D4-M6 | D-4 | SURVIVED | DROP-at-door commitment start deleted |
| D5-M1 | D-5 | CAUGHT | `cheby != 1` → `cheby != 2` |
| D5-M2 | D-5 | SURVIVED | orth cutoff `2*CD` → `1*CD` |
| D5-M3 | D-5 | SURVIVED | orth cutoff slack `+2` → `+20` |
| D5-M4 | D-5 | SURVIVED | cumulative \|Ring\| bound disabled |
| D5-M5 | D-5 | SURVIVED | concurrent \|Ring\| bound disabled |
| D5-M6 | D-5 | CAUGHT | Ring narrowed `cheby==1` → orth-only |
| D5-M7 | D-5 | SURVIVED | global cutoff slack `+1` → `+40` |
| D5-M8 | D-5 | SURVIVED | water-boost branch collapsed to `CD_wet` |
| D6-M1 | D-6 | CAUGHT | `opp_x <= 2` → `<= 1` |
| D6-M2 | D-6 | SURVIVED | `opp_x <= 2` → `<= 6` |
| D6-M3 | D-6 | SURVIVED | `opp_h <= min_own` → `opp_h < min_own` (tie no longer conceded) |
| D6-M4 | D-6 | **SURVIVED** | **harvest-race clause (a1) deleted entirely** |
| D6-M5 | D-6 | **SURVIVED** | **clause (b) opp-harvested-ours deleted entirely** |
| D6-M6 | D-6 | SURVIVED | A7 flipped: min own ETA over harvest-capable units only |
| D6-M7 | D-6 | SURVIVED | ETA drops the speed division (`ceil(d/speed)` → `d`) |
| D6-M8 | D-6 | SURVIVED | `opp_x <= 2` → `<= 5` |
| D6-M9 | D-6 | CAUGHT | `opp_x <= 2` → `<= 7` (== the near-miss's own distance) |
| D7-M1 | D-7 | SURVIVED | carry-age `> 12` → `> 0` |
| D7-M2 | D-7 | SURVIVED | end-of-game grace `T-6` → `T-600` |
| D7-M3 | D-7 | **SURVIVED** | **DROP-at-door requirement for banking deleted** |
| D7-M4 | D-7 | **SURVIVED** | **inventory-increase confirmation of banking deleted** |
| D7-M5 | D-7 | SURVIVED | PLANT-as-legitimate-sink exemption deleted |
| D7-M6 | D-7 | SURVIVED | harvest provenance labelling deleted |
| D7-M7 | D-7 | CAUGHT | `lost_bananas` episode emission deleted |
| D7-M8 | D-7 | SURVIVED | carry-age `> 12` → `> 2` |
| D8-M1 | D-8 | CAUGHT | `c in tr.diag` → `c in tr.doors` |
| D8-M2 | D-8 | CAUGHT | I-7 tie no longer conceded (`<` → `<=`) |
| D8-M3 | D-8 | **SURVIVED** | **oracle race strictness `<` → `<=` (tie conceded flipped)** |
| D8-M4 | D-8 | CAUGHT | `race_won = oracle["feasible"]` → `= True` |
| D8-M5 | D-8 | CAUGHT | ownership-flip precondition ignored (`lost = True`) |
| D8-M6 | D-8 | CAUGHT | opponent deadline = arrival only (ripeness dropped) |
| D8-M7 | D-8 | SURVIVED | opponent deadline = ripeness only (travel dropped) |
| D8-M8 | D-8 | SURVIVED | plant-kind `== "BANANA"` restriction deleted |
| D8-M9 | D-8 | **SURVIVED** | **growth-aware chop count → static `ceil(health/chop)`** |
| D8-M10 | D-8 | CAUGHT | exemption `lost and race_won` → `lost or race_won` |
| D8-M11 | D-8 | SURVIVED | health-decrease confirmation of an executed chop deleted |
| D9-M1 | D-9 | **SURVIVED** | **`len(own_units) != 1` guard deleted** |
| D9-M2 | D-9 | SURVIVED | banana-attributable widened to any resource |
| D9-M3 | D-9 | SURVIVED | `t >= first_train` → `t > first_train` |
| D9-M4 | D-9 | CAUGHT | `len(own_units) != 1` → `!= 7` |

**Single most decisive line of the table:** D8-M9. `test_oracle_matches_review_counterexample`
(`test_trace_detectors.py:387-396`) explicitly asserts
`banana_exact_chop_turns(2, 4, 1, 1) == 5` versus `ceil_div(4, 1) == 4` — the
round-3 host review's terminal counterexample. Yet replacing the oracle's
*use* of the growth-aware count with the static `ceil(health/chop)` inside
`conversion_race_oracle.py` **survives all four D-8 scenario tests**. The
counterexample is asserted on a helper function; no fixture routes it through
`detect_d8`. The regression the review demanded is not defended at the
detector level.

---

## 2. Per-detector findings

Throughout: "the pair" = the trigger test plus its declared near-miss.

### D-1 — A→B→A movement (`trace_detectors.py:555-621`)

**What the pair asserts.** Trigger `test_trigger_period2_10_turns`
(`:120-127`): 10 turns of strict A/B alternation, no carry change ever;
asserts `verdict == "FAIL"`, `ep["k"] >= 3`. Near-miss #1
`test_near_miss_progress_event_inside` (`:129-134`): *the same* alternation
with the single discriminating change `carry_fn=lambda t: carry_of(wood=1)
if t >= 6 else [0]*6` — one carry delta injected mid-window. Near-miss #2
`test_near_miss_short_window_k2` (`:136-139`): the same alternation truncated
to 5 states.

**Property or implementation?** Implementation. The decisive evidence is
**D1-M6**: deleting the clause `and (t == s + 1 or pos[t] == pos[t - 2])`
(`:600`) — the requirement that the walk actually be A,B,A,B and not merely
"moving" — **survives the whole suite**. Under that mutant a unit walking in
a straight line for seven turns is reported as a period-2 oscillation. The
property D-1 names is *oscillation*; the fixtures only ever exhibit
oscillation, never any other motion, so the clause that separates
oscillation from motion is untested. If the spec had defined D-1 as "any
7-turn progress-free movement run", both fixtures would still pass
unchanged.

**Checked against what?** Only the detector's own spec — `UNRESOLVED`.

**Genuine near-miss?** Near-miss #1 is genuine: exactly one dimension
(carry) differs, and D1-M3 confirms it is the carry clause that is pinned.
But A2 defines *three* progress-event kinds; D1-M4 (plant appear/disappear)
and D1-M5 (inventory delta on a DROP/PICK turn) both survive — two thirds of
the progress definition has no control at all. Near-miss #2 pins the window
threshold only within `[5, 9]` transitions (D1-M7 `>=5` survives, D1-M8
`>=9` survives, D1-M1 `>=4` caught): the pair is consistent with `k>=3` and
with `k>=4` alike (D1-M2 survives). The spec's `k >= 3` is not established.

**Independent oracle?** None. `conversion_race_oracle.py` models tree
growth and travel races; it has no notion of a unit's movement history and
**cannot** label oscillation. `UNRESOLVED`.

**Falsification probe.** Take the packet-row episodes already reported in
`detector-selftest-report-2026-08-04.md` §2 (e.g. game 897832286 unit 2,
turns 160–286) and compare `detect_d1`'s episode boundaries against the
packet's own independently-computed `baseline_maximum_period2` metric,
turn-window by turn-window rather than in aggregate. That metric is
computed by the host, not by this code, and is the only period-2 label in
the system that does not reuse detector logic. Agreement on window
boundaries (not just on "both are non-zero") would be the first
non-circular evidence for D-1.

---

### D-2 — Repeated PICK/DROP churn (`trace_detectors.py:624-679`)

**What the pair asserts.** Trigger `test_trigger_two_zero_net_cycles`
(`:153-161`): `["PICK 0 BANANA", "DROP 0", "PICK 0 BANANA", "DROP 0",
"WAIT"]` at `DOOR`, carries `[0,1,0,1,0]`, inventories `[5,4,5,4,5]`.
Near-miss `test_near_miss_single_pair_is_legit_seed_abort` (`:163-167`): the
same trace with **one** PICK/DROP pair. The single discriminating condition
is `picks < 2 or drops < 2` at `:657`.

**Property or implementation?** Implementation, and of only one of four
conjuncts. D-2's predicate is a conjunction of *window length ≤ 12*, *≥2
PICKs and ≥2 DROPs*, *at door cells*, *net-zero over the window*. Both
fixtures sit at `DOOR` and both are net-zero, so **D2-M4** (delete the door
restriction) and **D2-M5** (delete the net-zero requirement) both survive.
If the spec were wrong in the same way — e.g. if churn away from doors were
the real defect, or if non-net-zero churn counted — the pair would pass
identically.

**Checked against what?** Only the spec. `UNRESOLVED`.

**Genuine near-miss?** Yes, for the multiplicity conjunct only: it differs
in exactly the discriminating dimension and D2-M3 confirms the pin. The
12-turn window is pinned only within `(4, 120]` — D2-M1 (`>3`) caught,
D2-M6 (`>4`) survives, D2-M2 (`>120`) survives — because the trigger window
is 4 turns and no fixture probes a 12–13 turn boundary.

**Independent oracle?** None. Bank churn is an inventory-ledger property;
`conversion_race_oracle.py` has no inventory model. `UNRESOLVED`.

**Falsification probe.** A *differential* ledger: recompute, from the raw
transcript alone, `sum(inventory deltas) + sum(carry deltas)` per unit per
sliding window using a second implementation written from the transcript
format (not from `trace_detectors`' `Trace` class), and assert it agrees
with `detect_d2`'s window arithmetic on all 240 floor games. Disagreement
would falsify the net-zero clause; agreement would at least be a
cross-implementation check rather than self-agreement.

---

### D-3 — Same-target / occupied-cell contention (`trace_detectors.py:682-754`)

**What the pair asserts.** Trigger `test_trigger_shared_move_target_2_turns`
(`:184-191`): two own units emit identical MOVE destinations `(6,1)` on
turns 1 and 2, divergent on turn 3; asserts `ep["units"] == [0,2]` and
`(turn_start, turn_end) == (1,2)`. Near-miss
`test_near_miss_one_turn_transient` (`:193-197`): identical destinations on
turn 1 only. The discriminating condition is `len(run) >= 2` at `:715`.

**Property or implementation?** Implementation of a **proxy**, and this is
explicit: A4 of the self-test report states *"`target(u,t)` telemetry does
not exist in recorded traces; observable proxies used: identical MOVE
destinations …"*. The property is "two units contend for one target"; the
fixtures test "two units emit the same MOVE argument". D3-M4 (widening the
proxy to include WAIT) survives, showing the pair does not pin which verbs
constitute a target claim. If the spec's proxy were the wrong proxy — the
central risk A4 itself flags — the pair would pass unchanged.

**Checked against what?** Only the spec. `UNRESOLVED`.

**Genuine near-miss?** **Yes — the best control in the suite.** It differs
from the trigger in exactly one dimension (run length 1 vs 2) and pins the
threshold from *both* sides: D3-M1 (`>=1`) and D3-M2 (`>=3`) are both
CAUGHT. D-3 is the only detector whose threshold is exactly pinned. But
clause (b) — landing on a stationary-working peer, `:723-753` — has **no
fixture at all**: D3-M3 disables it entirely and survives. Half the
detector is undefended.

**Independent oracle?** None. `UNRESOLVED`.

**Falsification probe.** The referee's own movement-conflict resolver is
the ground truth for contention: replay a floor game and, for every turn
`detect_d3` flags, check whether the referee actually displaced a unit
(observable as `commanded MOVE destination != realized next-state
position`). A flagged run in which no unit was ever displaced is a false
positive against referee ground truth; an undisplaced-but-unflagged run is
a false negative. This label comes from the referee, not from the spec.

---

### D-4 — Abandoned carried-wood return (`trace_detectors.py:757-826`)

**What the pair asserts.** Two triggers:
`test_trigger_non_bank_verb_during_commitment` (`:213-219`) — commitment via
`MOVE 0 4 2` (a door) while carrying wood, then `CHOP`; asserts
`kind == "non_bank_verb"`, `verb == "CHOP"`.
`test_trigger_two_turns_without_progress` (`:221-228`) — two consecutive
door-distance non-decreases; asserts `kind == "no_progress"`.
Near-misses: `test_near_miss_monotone_return_and_drop` (`:230-235`) and
`test_near_miss_single_stall_is_tolerated` (`:237-243`), the latter differing
from the second trigger in exactly one stall turn.

**Property or implementation?** Implementation. The property is *"a unit
that has committed to bank wood must actually bank it"*. The fixtures pin
only the banned-verb set (D4-M4 caught) and the lower edge of the stall
tolerance (D4-M1 caught). Both **commitment-start** conditions other than
`MOVE`-to-door are unexercised: D4-M5 (delete the I-21 forced
full-capacity start) and D4-M6 (delete the DROP-at-door start) both survive.
So if the spec's notion of *when commitment begins* were wrong — the exact
question A5 resolves by fiat — the pair would not notice.

**Checked against what?** Only the spec. `UNRESOLVED`.

**Genuine near-miss?** `test_near_miss_single_stall_is_tolerated` is a
genuine one-dimension control (1 stall vs 2) and pins the lower edge. It
does not pin the upper edge: D4-M2 (`nd_run == 3`) survives, because the
`no_progress` trigger walks *three* consecutive non-decreasing turns, not
two. Nor does it pin non-decrease vs strict increase: D4-M3 (`d1 >= d0` →
`d1 > d0`) survives, because in both trigger and near-miss the distance
strictly increases rather than merely stalling — so the very distinction the
near-miss is *named after* ("single stall") is not actually present in the
data.

**Independent oracle?** None. `UNRESOLVED`.

**Falsification probe.** Score-level counterfactual: for each D-4 episode in
a floor game, compute the wood that *was* banked in that game versus the
wood that was carried at the moment of the flagged abandonment. If flagged
episodes are not associated with a measurable shortfall in banked wood
relative to harvested wood, the predicate is flagging behaviour that costs
nothing. The banked-wood total is referee output, independent of D-4.

---

### D-5 — Unbounded planting (`trace_detectors.py:829-888`)

**What the pair asserts.** Trigger `test_trigger_plant_outside_ring`
(`:259-264`): PLANT at `(6,3)`, Chebyshev 2 from the tent; asserts
`kind == "outside_ring"`. Trigger `test_trigger_plant_after_cutoff`
(`:266-273`): PLANT at `DOOR` on turn 299; asserts `"orth_cutoff" in kinds`.
Near-miss `test_near_miss_early_ring_plant` (`:275-277`): PLANT at `DIAG` on
turn 1 — differs from the first trigger in cell only, and from the second in
turn only.

**Property or implementation?** **Split — this is the one clause where the
pair discriminates a definitional property.** I-12 *defines* Ring as
`cheby(c, tent) == 1`; the trigger sits at Chebyshev 2 and the near-miss at
Chebyshev 1, and mutation pins membership from **both** sides: D5-M1
(`!= 1` → `!= 2`) and D5-M6 (`cheby==1` → orth-only) are both CAUGHT. For
the geometry clause the fixture and the property coincide because the
property *is* a geometric definition, so there is no gap for a wrong spec
to hide in.

Everything else about D-5 is untested. **D5-M4** (cumulative |Ring| bound
disabled) and **D5-M5** (concurrent |Ring| bound disabled) survive — the
I-13 capacity clauses have no fixture whatsoever. The I-5 cutoff arithmetic
survives arbitrary corruption: D5-M2 (`2*CD` → `1*CD`), D5-M3 (slack `+2` →
`+20`), D5-M7 (global slack `+1` → `+40`), D5-M8 (water branch collapsed to
`CD_wet`) all survive, because the trigger plants at turn 299 out of 300 —
so far past any plausible cutoff that the cutoff's *value* is irrelevant.
The near-miss plants at turn 1, equally far the other way. The pair
establishes only that a cutoff exists somewhere in `(1, 299)`.

**Checked against what?** Ring geometry: against a definition, which is as
good as it gets without an oracle — `VALIDATED` for that clause only.
Cutoffs and capacity: only the spec — `UNRESOLVED`.

**Genuine near-miss?** For geometry, yes. For the cutoff, no: it differs
from the trigger in the turn index by 298 turns, the opposite of a boundary
control.

**Independent oracle?** Partially — and this is the second place where
`conversion_race_oracle.py` is relevant. The I-5 cutoff asks "is there
enough time left for this plant to repay its cost?".
`first_fruit_delay` (`conversion_race_oracle.py:144-158`) computes exactly
when a fresh sapling first bears fruit, growth-aware; for the fixtures'
dry map it returns **24** turns. A cutoff derived from `first_fruit_delay`
would be an oracle-grounded label. D-5's `t_glob` at `:868-870` instead uses
`ceil_div(3, chop) + 1` = 4 turns of slack — an arithmetic proxy that never
consults ripeness at all. Whether the two agree is **UNRESOLVED**; the
comparison is cheap and is the obvious next probe.

**Falsification probe.** For every own PLANT in the 240 floor games,
compute `first_fruit_delay` on the referee's actual post-PLANT sapling and
check whether the plant in fact yielded any fruit or wood before turn 300.
Plants that D-5 permitted but that provably could never repay (fruit turn >
300 and never chopped) are false negatives of the cutoff; plants D-5
flagged that did repay are false positives. The realized yield is referee
output.

---

### D-6 — Opponent-favored fruit creation (`trace_detectors.py:891-942`)

**This is the most defective pair in the suite. See §4 for the arithmetic.**

**What the pair asserts.** Trigger `test_trigger_opponent_chopper_within_2`
(`:294-300`): PLANT at `DIAG` with an opponent (hp 1, cp 1) at `(3,0)`, BFS
distance 2; asserts `kind == "opp_chop_eta"`, i.e. clause `opp_x <= 2` at
`:924`. Near-miss `test_near_miss_opponent_far_away` (`:302-304`): the same
plant with the opponent at `(0,6)`, BFS distance **7**. The discriminating
condition is the opponent's distance, 2 vs 7.

**Property or implementation?** Neither, in the useful sense: the pair
tests **one bound of one of three clauses**, and the clause it tests is
*already known to be the wrong predicate*. D-6 clause (a1) is
`eta_opp_h(c,t) <= min_u eta_u(c,t)` — pure arrival order. The design
document
`design-banana-fsm-2026-08-06.md:1170` records review item **F4 — founding
not exact. New `founding_safety_oracle` replaces arrival-order with exact
[executable-harvest safety]**, and `design-banana-fsm-2026-08-06.md:580`
records that the candidate's A-17 plant-time guard now calls
`founding_safety_oracle.feasible_found`. `conversion_race_oracle.py:405-421`
states it plainly: *"EXACT SAFETY (replaces the old `eta_res < eta_opp_h`
arrival-order test) … arriving first does NOT reserve/body-block the cell,
so an opponent that reaches the cell by first ripeness harvests the first
fruit even though we arrived earlier."*

**`detect_d6` still implements the superseded arrival-order test.** The
candidate and the detector now disagree about what "opponent-favored" means,
and both D-6 bite-tests pass regardless. This is the GAR-3 pattern verbatim.

Mutation corroborates that the pair is blind to it: **D6-M4** deletes clause
(a1) *entirely* and survives; **D6-M3** flips its tie handling (`<=` → `<`)
and survives; **D6-M5** deletes clause (b) — the replay ground-truth clause
that the spec itself calls *"ground truth from the replay"* — entirely, and
survives; **D6-M6** flips A7's contested "min over ALL own units" to "min
over harvest-capable own units" and survives; **D6-M7** removes the speed
division from the ETA and survives.

**Checked against what?** An independent oracle **exists** and
**contradicts the near-miss** (§4). Truth validity: **FALSIFIED for the
near-miss**, not merely unresolved.

**Genuine near-miss?** No, on two counts. (i) It differs in exactly one
dimension but by the wrong magnitude — 2 vs 7, where the threshold is 2:
D6-M2 (`<=6`) and D6-M8 (`<=5`) survive, and only D6-M9 (`<=7`, i.e. the
near-miss's own distance) is caught. The pair bounds the threshold to
`[2, 6]`, a five-wide interval. (ii) It is not a negative at all: the
founding oracle calls it unsafe.

**Independent oracle?** **Yes — `founding_safety_oracle`
(`conversion_race_oracle.py:385-439`), and it is not used by any detector.**
This is the only detector in the suite for which a genuine independent
truth label already exists in the directory, and applying it (§4) falsifies
the near-miss.

**Falsification probe.** Already run, §4. The full version: for every own
PLANT event in the 240 floor games, evaluate `founding_safety_oracle` on the
referee's post-PLANT sapling and compare `feasible_found == False` against
`detect_d6`'s verdict. Every plant where D-6 is silent and the oracle says
unsafe is a D-6 false negative with a named, non-circular label.

---

### D-7 — Lost harvested fruit (`trace_detectors.py:945-1017`)

**Weakest discrimination in the suite: 1 of 8 mutants caught.**

**What the pair asserts.** Trigger `test_trigger_dropped_outside_door_is_lost`
(`:323-327`): `harvest_trace((2,2), drop_bank=False)` — HARVEST then DROP at
`(2,2)`, inventories `[0,0,0]`; asserts `kind == "lost_bananas"`. Near-miss
`test_near_miss_banked_at_door` (`:329-331`): `harvest_trace(DOOR,
drop_bank=True)` — inventories `[0,0,1]`.

**Property or implementation?** Implementation, and barely that. The
banking test at `:998-1001` is a **conjunction**: `cmd.verb == "DROP"` AND
`u.cell in tr.doors` AND `inv[BANANA]` increased. The near-miss changes
**both** the cell (non-door → door) **and** the inventory (no increase →
increase) **simultaneously**. Consequently neither conjunct is individually
controlled, and mutation confirms it exactly: **D7-M3** (delete the
door-cell requirement) survives *and* **D7-M4** (delete the
inventory-increase confirmation) survives. Under D7-M3 a banana dropped in
open field next to a tent counts as banked; under D7-M4 a DROP at a door
that the referee refused counts as banked. Both mutants ship green.

This is the textbook multi-dimensional-control defect: the control differs
from the trigger in two dimensions, so it proves neither.

Everything else survives too: D7-M1 (`age > 12` → `> 0`), D7-M8 (`> 2`),
D7-M2 (end grace `T-6` → `T-600`), D7-M5 (delete the PLANT sink exemption),
D7-M6 (delete harvest provenance labelling). The reason is structural: both
fixtures are **3 turns long**, so the 12-turn age clause and the 6-turn
end-of-game grace are unreachable by construction, and the FIFO ledger never
holds more than one entry.

**Checked against what?** Only the spec. `UNRESOLVED`.

**Genuine near-miss?** **No.** Two dimensions vary at once. The minimal
repair is two additional near-misses, each varying one: DROP at a door with
*no* inventory increase (the refused-DROP case), and DROP off-door *with* an
inventory increase (impossible under the referee — its impossibility is
itself an assertion worth making).

**Independent oracle?** None. Fruit accounting is an inventory ledger;
`conversion_race_oracle.py` models growth and travel and has no inventory or
carry concept. `UNRESOLVED`, and there is no cheap path to one from existing
code.

**Falsification probe.** Conservation, checked against the referee: over a
whole floor game, `bananas that ever existed on our plants (sum of fruit
decrements on own-planted cells) == bananas banked (own inventory
increments) + bananas planted + bananas held at end + bananas taken by the
opponent (opponent carry increments on our cells)`. Every term is read
directly from the transcript; none uses `detect_d7`'s ledger. A non-zero
residual localises a real loss; `detect_d7` flagging where the residual is
zero is a false positive.

---

### D-8 — Diagonal-mother chop (`trace_detectors.py:1067-1169`)

**What the pair asserts.** Base pair: `test_trigger_chop_diagonal_mother`
(`:347-354`) CHOPs an own-planted live banana standing on `DIAG`; near-miss
`test_near_miss_orthogonal_wood_slot_chop_is_legal` (`:356-359`) does the
identical thing on `DOOR`. The single discriminating condition is
`c in tr.diag` vs `c in tr.doors` (`:1113`). Amended pair (four tests,
`:362-478`) exercises the two-part exemption `lost and race_won` (`:1135`).

**Property or implementation?** Mixed, and it is the strongest detector in
the suite (6 of 11 mutants caught). Genuinely property-level:
`test_exempt_arrival_is_not_loss` (`:464-478`) — opponent adjacent at
chop-start, mother young and unripe — is a real control on the *concept*
"arrival alone is not loss", and **D8-M6** (dropping ripeness from the
opponent deadline) is CAUGHT by it. That is the one place in the whole suite
where a fixture discriminates a conceptual revision rather than a constant.
D8-M1, D8-M2, D8-M4, D8-M5, D8-M10 are also caught: diag membership, the I-7
tie convention, and both halves of the exemption conjunction are pinned.

But: **the oracle the exemption consults is the oracle the detector's own
spec defines**, so the D8Amended tests are agreement-with-self by
construction. And five mutants survive. Two matter.

- **D8-M9** — replacing growth-aware `exact_chop_turns` with static
  `ceil(health/chop)` inside the oracle survives, even though the suite
  contains an explicit unit assertion that these differ
  (`:391-392`). No scenario fixture has a mother whose growth changes the
  chop count; every fixture's tree is either at cooldown ≥ the chop
  sequence length or size 4. The round-3 terminal-failure regression is
  asserted on the helper, not on the detector.
- **D8-M3** — flipping the oracle's race strictness `<` → `<=` survives.
  `conversion_race_oracle.py:46-50` states the strict inequality is
  load-bearing (*"the equal-turn race … is contested and conceded to the
  opponent"*), and D8-M2 shows the *I-7* tie convention **is** pinned — but
  the *oracle's* tie convention is not. No fixture puts
  `completion_turn == opponent_harvest_turn`.

Also unexercised: **D8-M7** (opponent deadline = ripeness only, dropping
travel) survives — the mirror image of the caught D8-M6, so only one of the
two `max()` arguments is defended. **D8-M8** (delete the `kind == "BANANA"`
restriction) and **D8-M11** (delete the health-decrease confirmation)
survive.

**Checked against what?** Its own oracle — circular. `UNRESOLVED`.

**Genuine near-miss?** The base near-miss is genuine and single-dimensional
(diag vs orth, everything else byte-identical). `test_exempt_arrival_is_not_loss`
is a genuine conceptual control. `test_flagged_flip_but_infeasible_chop`
(`:433-462`) differs from the feasible case in *several* dimensions at once
(size 1→4, health/cooldown schedule, opponent trajectory), which is why the
oracle-internal constants survive.

**Independent oracle?** `conversion_race_oracle` is **not** independent —
`detect_d8` calls it at `:1121`. `asset_survival_oracle`
(`conversion_race_oracle.py:282-382`) *is* unused by any detector and
strictly generalises it (it adds `opp_destroy_turn`), so it is a partial
independent label. However, **all four D8Amended fixtures give their
opponents `cp=0`** (`test_trace_detectors.py:377, 382`), and the module
docstring states that with zero opponent chop power `asset_survival_oracle`
reproduces `conversion_race_oracle` exactly. On these fixtures the two
oracles are *identical by construction* and cannot disagree. Measured: for
`test_exempt_flip_then_feasible_conversion`'s chop-start state, giving the
opponent `chop_power = 1` moves `asset_lost_turn` from 25 to 11 — a 14-turn
swing — without changing the verdict (`completion_turn = 6`). The
destruction dimension is present, large, and untested.

**Falsification probe.** Re-evaluate every D-8 exemption decision in the 240
floor games under `asset_survival_oracle` with the opponents' **real**
chop powers, and report every cell where `feasible` (CRO) and
`feasible_convert` (ASO) disagree. Those are conversions D-8 exempted that
the generalised oracle says lose the asset to a chopper. This is a genuine
cross-oracle check because `asset_survival_oracle` is not on `detect_d8`'s
call path.

---

### D-9 — Second-worker TRAIN displacement (`trace_detectors.py:1172-1224`)

**Status: `INAPPLICABLE` for the paired clauses, per the established
finding — not re-litigated here.** `train_late` / `train_missing` /
`train_stats_differ` (`:1204-1223`) are guarded by `if p_train is not None`,
`fuzz_panel.py:486-495` injects a second worker at `second_worker_bias` 0.5
so `can_train` is false at `yamo_orchard_live.rs:836`, and PLUM is granted at
value 1 (`_inventory:390-397`) against a `training_cost` of PLUM ≥ 2. Both
D-9 tests call `detect_d9(tr)` with one argument. No fixture for those
clauses can exist without changing the harness; none is proposed.

**What the pair asserts, for the single-trace clause.** Trigger
`test_trigger_banana_command_before_train_single_worker` (`:484-495`):
`PICK 0 BANANA` on turn 1 with one own unit and no TRAIN anywhere; asserts
`kind == "banana_before_train"`. Near-miss `test_near_miss_train_issued_first`
(`:497-508`): `TRAIN 1 1 1 1;WAIT` on turn 1, a second own unit appears on
turn 2, `PICK 0 BANANA` on turn 3.

**Property or implementation?** Neither. The near-miss differs from the
trigger in **three** dimensions simultaneously: a TRAIN is present, the
banana command moves from turn 1 to turn 3, and the own-unit count goes from
1 to 2. Because the TRAIN is on turn 1, `first_train = 1` and the scan loop
`break`s immediately at `:1190` — so the near-miss exercises *no* clause at
all; it terminates before the guard, the verb test and the unit-count test
are ever reached.

Mutation proves this exactly: **D9-M1** deletes the `len(own_units) != 1`
guard (`:1193`) entirely and **survives**; **D9-M2** widens the
banana-attributable verb set to any resource and **survives**; **D9-M3**
loosens `t >= first_train` to `t > first_train` and **survives**. Only
D9-M4 (guard → `!= 7`, which kills the *trigger*) is caught. The pair
therefore establishes only that "some episode is emitted when a PICK BANANA
happens and no TRAIN has occurred" — none of the three qualifying conditions
in the clause's name is discriminated. This is precisely how D-9 could pass
both bite-tests perfectly and emit 196 false positives.

**Checked against what?** Only the spec. `UNRESOLVED` for the single-trace
clause, `INAPPLICABLE` for the paired clauses.

**Genuine near-miss?** **No — the worst-constructed control in the suite.**
A genuine near-miss would place the TRAIN at turn 2 with the banana command
still at turn 1 (isolating the ordering), or keep a single unit but issue a
non-banana PICK (isolating the verb clause), or keep two units with no TRAIN
(isolating the unit-count guard).

**Independent oracle?** None; `conversion_race_oracle.py` has no notion of
training, workers or costs. `UNRESOLVED`.

**Falsification probe.** The 196 false positives are themselves the truth
label. Take the floor games where D-9 fired, and for each flagged turn check
against the harness whether TRAIN was *executable* at that turn (`can_train`
at `yamo_orchard_live.rs:836` and `training_cost` against actual PLUM). A
flag raised on a turn where TRAIN was impossible is a false positive by
construction — which is exactly what A10 admits when it says D-9 flags "even
if training is infeasible". Running that comparison converts a documented
admission into a measured false-positive rate.

---

## 3. Summary table

Cells: `VALIDATED` / `UNPROVEN` / `INAPPLICABLE` / `UNRESOLVED`.

| Det | Implementation validity | Calibration validity | Truth validity |
|---|---|---|---|
| **D-1** | UNPROVEN — 2/8 mutants caught; the A≠B≠A shape clause (`:600`) can be deleted outright (D1-M6) and both fixtures still pass; 2 of A2's 3 progress-event kinds have no control | UNPROVEN — D-1 *fires* on the parent lineage by design (4/4 packet games), so floor agreement is not evidence either way | UNRESOLVED — no oracle in the repo can label oscillation; the packet's host-computed `baseline_maximum_period2` is the only non-circular label and has never been compared window-by-window |
| **D-2** | UNPROVEN — 2/6 caught; the door-cell and net-zero conjuncts are both deletable (D2-M4, D2-M5); window pinned only to `(4,120]` | UNPROVEN — zero episodes over 240 floor games is consistent with a correct silent detector and with a detector that cannot fire | UNRESOLVED — spec-only; no independent ledger exists |
| **D-3** | UNPROVEN — clause (a)'s 2-turn threshold is exactly pinned (D3-M1 and D3-M2 both caught, the only two-sided pin in the suite), but clause (b) is deletable (D3-M3) and the MOVE-only proxy is not pinned (D3-M4) | UNPROVEN — zero floor episodes; A4 states the true `target(u,t)` telemetry does not exist in traces | UNRESOLVED — the referee's displacement record is an available non-circular label and has not been used |
| **D-4** | UNPROVEN — 2/6 caught; both non-`MOVE` commitment-start conditions deletable (D4-M5, D4-M6); the "single stall" the near-miss is named for is not actually present in the data (D4-M3 survives) | UNPROVEN — zero floor episodes | UNRESOLVED — spec-only |
| **D-5** | **VALIDATED for the I-12 Ring-geometry clause only** — membership pinned from both sides (D5-M1, D5-M6). UNPROVEN elsewhere: I-13 capacity bounds have no fixture (D5-M4, D5-M5 deletable); all four I-5 cutoff constants survive corruption (D5-M2/M3/M7/M8) | UNPROVEN — fires on the parent lineage by design (2/4 packet games) | UNRESOLVED for cutoffs — `first_fruit_delay` (24 turns on the fixture map) is an available oracle-grounded alternative to D-5's `ceil(3/chop)+1` proxy and has never been compared. VALIDATED-by-definition for Ring geometry: I-12 *is* a geometric definition, so fixture and property coincide |
| **D-6** | UNPROVEN — 2/9 caught; clause (a1) and clause (b) are each deletable in full (D6-M4, D6-M5); the ETA bound is pinned only to `[2,6]`; the ETA formula itself is not pinned (D6-M7) | UNPROVEN — fires on the parent lineage by design (1/4 packet games) | **FALSIFIED (for the near-miss)** — `founding_safety_oracle`, the repo's own F4 replacement for arrival-order safety, judges the D-6 near-miss unsafe on two grounds while `detect_d6` returns PASS (§4). D-6 implements a predicate the design document records as superseded |
| **D-7** | UNPROVEN — **1/8 caught**, the weakest in the suite; both conjuncts of the banking test are independently deletable (D7-M3, D7-M4) because the near-miss varies both at once; the 12-turn and 6-turn constants are unreachable in 3-turn fixtures | UNPROVEN — zero floor episodes | UNRESOLVED — spec-only; no oracle exists and none is cheaply derivable. The transcript-level conservation identity in §2 is the missing label |
| **D-8** | UNPROVEN (best of the suite) — 6/11 caught, incl. the arrival-vs-ripeness concept (D8-M6); but the growth-aware chop arithmetic (D8-M9) and the oracle's strict-tie convention (D8-M3) both survive, as does the travel half of the deadline (D8-M7) | UNPROVEN — zero floor episodes | UNRESOLVED — circular: `detect_d8` calls the very oracle its spec names (`:1121`). `asset_survival_oracle` is an available non-circular generalisation, but all four fixtures give opponents `cp=0`, which makes the two oracles provably identical on those inputs |
| **D-9** | UNPROVEN for the single-trace clause — 1/4 caught; the unit-count guard, verb set and ordering boundary are all deletable (D9-M1/M2/M3) because the near-miss `break`s out at `:1190` before any of them runs. **INAPPLICABLE** for the paired TRAIN clauses | **INAPPLICABLE** — the panel is built so the parent can never TRAIN (three independent mechanisms) | **INAPPLICABLE** for the paired clauses. For the single-trace clause: FALSIFIED in practice — 196 false positives on the floor, with A10 conceding the detector fires "even if training is infeasible" |

Totals across the 27 cells: 1 VALIDATED (partial, D-5 geometry), 3
INAPPLICABLE, 2 FALSIFIED, 21 UNPROVEN/UNRESOLVED.

---

## 4. The D-6 falsification, in numbers

Run read-only against pristine copies (`/tmp/.../scratchpad/audit/pristine/d6_cross.py`).
Fixture map is the 9×7 map of `test_trace_detectors.py:21-30`: no water, tent
at `(4,3)`, `DIAG = (3,2)`. The referee's post-PLANT banana sapling is
`(size 1, health 3, fruits 0, cooldown CD_dry = 6)`.

```
first_fruit_delay(1, 3, 0, 6) = 24        # a fresh sapling ripens 24 turns later

detect_d6, trigger   (opponent at (3,0), BFS 2) -> FAIL, 1 episode
detect_d6, near-miss (opponent at (0,6), BFS 7) -> PASS, 0 episodes

founding_safety_oracle on the SAME two geometries
  trigger   geometry: feasible_found=False  our_h=26  opp_h=26  opp_destroy=6
  near-miss geometry: feasible_found=False  our_h=26  opp_h=26  opp_destroy=12
```

Read the near-miss row. The oracle calls the plant **unsafe** twice over:

1. `opp_harvest_turn == our_harvest_turn == 26`. Ripeness (24) dominates
   travel (7), so both players stand on the cell long before the first
   fruit exists; the race is a tie and
   `conversion_race_oracle.py:413-418` states a tie is conceded, because a
   simultaneous last-fruit HARVEST duplicates the banana to *both* players.
   D-6's arrival-order clause (a1) compares `7 <= 0` and passes the plant.
2. `opp_destroy_turn = 12 < our_harvest_turn = 26`. The opponent's chopper
   (chop power 1, BFS 7) fells the sapling on turn 12 — fourteen turns
   before it could ever bear fruit. D-6's clause (a2) compares
   `eta_opp_x = 7 <= 2` and passes the plant.

So the trace that `test_near_miss_opponent_far_away` asserts is clean is,
by the repo's own named founding oracle, a plant that the opponent either
farms or destroys. **The D-6 near-miss is a false negative measured against
an independent label.**

Two constructed cases confirm the divergence is general, not an artifact of
that one geometry:

```
harvest-only opponent at BFS 5 (loses the arrival race outright):
    feasible_found=False  our_h=26  opp_h=26   opp_destroy=unreachable
chop-only opponent at BFS 3 (outside D-6's hardcoded ETA<=2), power 3:
    feasible_found=False  our_h=26  opp_h=--   opp_destroy=5
```

Both are D-6-clean and oracle-unsafe. The second is the sharper one: a
chopper at ETA 3 destroys the mother on turn 5, and D-6's threshold of 2
was chosen — per the spec's rationale at `invariant-spec-2026-08-04.md:383-390`
— as a fixed constant rather than derived from destruction timing.

Note also, for completeness, that the D-6 **trigger** is oracle-unsafe too
(`feasible_found=False`). So the trigger agrees with the oracle and the
near-miss does not: the pair as a whole does not discriminate the property,
it merely happens to be right on the positive side.

A caveat stated plainly: on this particular 9×7 fixture map, with
`first_fruit_delay = 24` and a maximum BFS distance well under 24, **no ring
plant with any opponent present is founding-safe**. That is itself the
finding — the fixture map cannot express a genuine D-6 negative control, so
the near-miss could not have been a real negative no matter which opponent
cell was chosen.

---

## 5. Independent-oracle availability — the honest summary

`conversion_race_oracle.py` exports three oracles. Where each can and
cannot serve as a truth label:

| Oracle | Can label | Cannot label |
|---|---|---|
| `CONVERSION_RACE_ORACLE` (`:160-223`) | nothing independently — `detect_d8` **calls it** (`trace_detectors.py:1121`), so any D-8 check against it is circular by construction | D-1..D-7, D-9 |
| `ASSET_SURVIVAL_ORACLE` (`:282-382`) | D-8's exemption, non-circularly (no detector calls it), by adding `opp_destroy_turn`. **But** all four D-8 fixtures set opponent `cp=0`, and with zero opponent chop power this oracle reproduces `CONVERSION_RACE_ORACLE` exactly — so on the existing fixtures it is not independent in practice, only in principle | D-1, D-2, D-3, D-4, D-7, D-9 |
| `FOUNDING_SAFETY_ORACLE` (`:385-439`) | **D-6, fully and non-circularly** — it is the F4 replacement for exactly D-6's predicate, no detector calls it, and it already falsifies the near-miss (§4). Partially D-5's I-5 cutoff, via `first_fruit_delay` | D-1, D-2, D-3, D-4, D-7, D-9 |

**Plainly: six of the nine detectors have no oracle available anywhere in
this directory, and none is cheaply derivable from the existing modules.**
D-1 (movement), D-2 (bank churn), D-3 (contention), D-4 (wood banking),
D-7 (fruit accounting) and D-9 (training) are all inventory-, command- or
movement-level properties; the oracle module models only tree growth,
travel and harvest/chop race timing. Their truth-validity cells are
`UNRESOLVED` and will stay `UNRESOLVED` until a label is built from referee
output (the probes in §2 name the specific referee-derived quantity in each
case).

---

## 6. What could not be determined

- **Whether D-5's I-5 cutoff arithmetic is correct.** The four constants
  (`2*CD`, `+2`, `ceil(3/chop)`, `+1`) survive arbitrary corruption under
  the current fixtures. `first_fruit_delay` provides an oracle-grounded
  alternative. *Evidence that would settle it:* evaluate both on every
  floor-game PLANT and compare against realized yield before turn 300.
  `UNRESOLVED`.
- **Whether D-3's MOVE-destination proxy tracks real contention.** A4
  concedes the true telemetry is absent. *Evidence that would settle it:*
  the referee's realized-vs-commanded landing comparison on flagged runs
  (§2, D-3 probe). `UNRESOLVED`.
- **Whether D-2/D-3/D-4/D-7/D-8's floor silence is correctness or
  incapacity.** Zero episodes across 240 games is compatible with both.
  *Evidence that would settle it:* seed each detector's positive fixture
  pattern into a floor trace via the existing trace builder
  (`make_banana_traces.py`) and confirm the detector fires on real
  transcript data, not only on synthetic blocks. `UNRESOLVED` —
  distinguishing these is the whole content of calibration validity and no
  current artifact does it.
- **Whether D-6's disagreement with `founding_safety_oracle` produces
  false negatives on the floor specifically** (as opposed to on the
  fixtures, where it is demonstrated). *Evidence that would settle it:* the
  240-game sweep in §2's D-6 probe. `UNRESOLVED` — but the fixture-level
  falsification in §4 already stands on its own.
- **Whether `detect_d8`'s exemption would change under real opponent chop
  powers.** Measured swing on one fixture: `asset_lost_turn` 25 → 11 with
  `cp=1`, verdict unchanged. One data point is not a distribution.
  `UNRESOLVED`.

---

## 7. Bottom line

- **0 of 9 pairs establish truth validity.** Every pair is checked against
  the detector's own spec, except D-6, where the one available independent
  oracle **contradicts** it.
- **1 pair discriminates a definitional property**: D-5's Ring geometry,
  and only because I-12 *is* a definition. **1 pair discriminates a
  conceptual revision**: D-8's arrival-vs-ripeness control — but against
  the oracle the detector itself calls, so circularly.
- **The remaining 7 discriminate implementation only**, and 4 of them
  (D-4, D-6, D-7, D-9) have near-misses that vary more than one dimension,
  which is why single-conjunct deletions survive.
- **Mutation: 20 caught, 44 survived out of 64** (31 %). No mutation was
  caught by a detector other than its own.
- **Most defective pair: D-6.** It is the GAR-3 pattern instantiated a
  second time: the detector faithfully implements a predicate that
  `design-banana-fsm-2026-08-06.md:1170` records as replaced, its
  bite-tests pass perfectly, and the replacement oracle — sitting in the
  same directory, called by the candidate's own A-17 plant guard — judges
  the pair's *negative control* unsafe on two independent grounds. D-7 has
  the weakest discrimination (1/8) and D-9's near-miss is the worst
  constructed (it `break`s before any clause runs), but only D-6 is
  demonstrably testing the wrong predicate against a label that already
  exists.
