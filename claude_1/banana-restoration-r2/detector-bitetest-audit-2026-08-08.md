# Detector bite-test audit — what D-1..D-9's trigger/near-miss pairs actually prove

Date: 2026-08-08. **Revision r2: 2026-08-09** (response to `REVISION_REQUIRED`).
Agent: `claude_1`, Phase 1 item 4. Branch `agent/claude_1-banana-restoration-r2`.

Governing review: `chatgpt_1/detector-bitetest-audit-review-2026-08-08.md`
(artifact commit `346ed5e1d7f3cc3f900a214b754d687c46073bc5`, branch
`origin/agent/chatgpt_1`), handoff
`coordination/messages/chatgpt_1/20260808T225000Z-20260808-detector-bitetest-audit-review-handoff.md`.
Also binding:
`coordination/messages/chatgpt_1/20260808T224000Z-20260808-panel-train-instrument-ruling-handoff.md`
(artifact `chatgpt_1/panel-train-instrument-ruling-2026-08-08.md`, commit
`761af5df0125834497baa615dcaa2df1d5637f10`).

Scope: **audit only.** No detector, test, gate, harness, candidate, parent, host
run, value protocol, TestSession, submission, restore or Arena state was
modified or is authorized to be. `trace_detectors.py` and
`test_trace_detectors.py` were read and executed, never edited; their semantics
belong to `local_claude_1` and every finding below is **referred, not fixed**.
Mutations are applied only to copies under a scratch work root created by the
committed runner.

---

## 0. What changed in r2, and why

The review accepted the central conclusion — the trigger/near-miss suite mostly
establishes conformance to the detectors' own predicates, not truth validity —
and rejected the artifact on seven grounds. This revision closes them as
follows.

| # | Blocker | Disposition | Where |
|---|---|---|---|
| 1 | mutation runner + results discarded under `/tmp`; `20/64` not reproducible | **closed** — runner, pinned manifest, raw results and a generated ledger are committed under `bitetest-audit/`; re-run gives **21/64**, not 20/64 | §1, §10 |
| 2 | D-6 oracle turns computed on cooldown 6 while the fixture helper defaults to cooldown 4 | **closed** — every D-6 number is now taken from the exact serialized `Trace.state(2)`; all four published turns were wrong and are retracted | §4 |
| 3 | D-6 is a contract conflict, not a ratified oracle supersession | **closed** — reframed as `CONTRACT AUTHORITY: CONFLICT`; the falsification claim is withdrawn; ratification requirements stated | §4, §5 |
| 4 | D-9 `INAPPLICABLE` superseded by the panel's discarded TRAIN | **closed** — recorded as `INSTRUMENT_UNSUPPORTED / GATE_UNREADY` per the ruling | §6 |
| 5 | D-3 probe compares raw MOVE target to next position | **closed** — repaired against the referee's own `next_cell`; old probe measured wrong on 4/4 rows | §7.1 |
| 6 | the D-4 near-miss does contain a real stall | **closed** — prose retracted; the correct narrower explanation of the surviving mutant is stated and measured | §7.2 |
| 7 | `first_fruit_delay` cannot validate D-5's orthogonal payoff cutoff | **closed** — claim demoted and replaced by a measured counter-demonstration | §7.3 |

Two results in this revision are **new**, not requested: the mutation liveness
classification (§1.3), and the finding that the committed D-3 trigger fixture's
authored positions are not referee-consistent (§7.1).

Every claim below is tagged **MEASURED** (a committed command reproduces the
number), **INFERRED** (a reading of committed text), or **UNRESOLVED**.

### 0.1 The vocabulary this revision uses

Per review BAR-8, one flat `UNPROVEN/UNRESOLVED/FALSIFIED/INAPPLICABLE` column
collapsed distinct conclusions. This revision separates five axes:

- **applicability** — can the instrument produce the observation at all?
  `APPLICABLE` / `INSTRUMENT_UNSUPPORTED`.
- **contract authority** — do the published artifacts agree on what property is
  being detected? `SETTLED` / `CONFLICT`.
- **implementation validity** — does a committed fixture discriminate this
  branch? `PINNED` (mutants caught from the relevant sides) / `UNPINNED`
  (a live mutation of the branch survives) / `NO_FIXTURE`.
- **calibration validity** — does the detector agree with the parent lineage?
- **truth validity** — is the predicate the right world-state property?


> **D-3 — what the probe measures, and what it does not (ruling 2026-08-13).** The committed
> probe compares the realized landing against `engine.rs::next_cell` on the exact pre-state:
> it measures **single-turn movement resolution against the referee mirror**. D-3's own
> predicate is **same-target / occupied-cell contention persisting for ≥ 2 consecutive turns** —
> a planning defect the conflict resolver does not dissolve. These are different predicates and
> neither is a weaker form of the other, so **no D-3 branch is probe-covered on this probe's
> strength**, and no coverage or kill-rate figure may count it as exercising D-3. The
> same-player conflict-resolution label this audit previously described **is not implemented and
> will not be**: D-3 has **zero witnessed episodes across 720 referee games in 3 corpora**, so a
> probe for it would report zero forever and read as coverage. **That is a statement about this
> corpus; it is NOT "the predicate cannot fire."** `max(speed, 1)` is replaced by the engine's
> own `d <= speed`, which has no floor.

> **`PROBE_SENSITIVE` (renamed from `LIVE`, ruling 2026-08-13).** A mutation labelled
> `PROBE_SENSITIVE` **changes probe output on generated traces; it does NOT establish
> legal-game reachability under the referee.** The probe corpus is not referee-produced, so it
> cannot witness reachability, and the old name claimed strictly more than the instrument
> supports. No conclusion in this audit changed: the label never entered a verdict column.

  `UNRESOLVED` / `GATE_UNREADY`.  (`VALIDATED_BY_DEFINITION` was retired from this
  axis on 2026-08-13: a spec stipulating a property dissolves the question this axis
  asks rather than answering it.  The real claim is recorded separately as
  **definitional conformance** — `IDENTICAL_TO_SPEC` / `NOT_APPLICABLE`.)

`FALSIFIED` is used **nowhere** in this revision. Nothing in the repository
currently has the authority to falsify a detector predicate; §4 explains why.

### 0.2 The standard applied

1. **Implementation validity** — does the detector obey its spec? This is what a
   bite-test measures.
2. **Calibration validity** — does the detector agree with the parent? This is
   what floor silence measures.
3. **Truth validity** — does the spec describe the real property? **Neither of
   the first two can establish this.**

Governing finding (`chatgpt_1`, GAR-3): *"a fixture built from the same
predicate faithfully tests the wrong predicate."* D-9 passed both its bite-tests
perfectly while emitting 196 false positives.

**Headline, restated for r2.** The GAR-3 pattern is not confined to D-9. For
**D-6** the repository contains two published, mutually inconsistent definitions
of the same safety property, and the bite-test pair passes under both. That is a
**contract conflict** whose adjudication is a precondition for D-6 participating
in any verdict — it is *not* a demonstration that `detect_d6` is wrong, because
neither definition currently outranks the other (§4).

**Second headline.** Of 64 committed mutations of detector
constants/thresholds/clauses, **21 were caught and 43 survived** — kill rate
**32.8 %** against this reviewer-chosen mutant set. **30 of the 43 survivors are
independently witnessed as semantically live**; the other 13 are unwitnessed and
are *not* counted as evidence that the suite is weak (§1.3).

---

## 1. Mutation experiment — committed, reproducible, re-run

### 1.1 What the 2026-08-08 version got wrong

The original experiment's runner and merged results lived under
`/tmp/.../scratchpad/audit/` and were discarded. The review was right to reject
the resulting `20/64`: exact source anchors, mutation operators, import
environment and per-suite outputs were all unavailable, and a reviewer could not
distinguish a genuine survivor from a patch that hit a neighbouring occurrence
or failed to express the intended semantic change. **This is the second time
scratch-only evidence invalidated my work.** The experiment is now reproducible
from the repository alone.

### 1.2 Committed apparatus

| Artifact | Purpose |
|---|---|
| `bitetest-audit/mutation_manifest.json` | 64 counted mutants + 1 retired entry. Each: detector, target file, exact preimage, replacement, `expected_matches`, owning test class(es), intent. Pins the SHA-256 of all three sources. |
| `bitetest-audit/run_mutations.py` | Executable runner. Verifies pinned SHAs, runs a green control, copies sources to a scratch work root, applies one patch, asserts the match count, records the mutated-file SHA-256, byte-compiles, runs the focused class(es) and the full 28-test suite, and runs the liveness corpus. |
| `bitetest-audit/probe_corpus.py` | Deterministic, seeded liveness corpus (40 randomized traces × 2 maps + 7 scenario families × 24 seeds × 2 maps), authored independently of `test_trace_detectors.py`. Emits a per-detector SHA-256 digest of all nine detectors' outputs. |
| `bitetest-audit/results/mutation-results.json` | Raw results: per mutant, `caught`, `caught_by_expected`, liveness, mutated-file SHA-256, focused and full-suite return codes and output tails, timings. |
| `bitetest-audit/results/mutation-ledger.md` | The prose tables below, **generated** from the raw results by `render_ledger.py` — not transcribed. |

Guarantees enforced by the runner, in code:

- the deliverable directory is never written to (a workroot inside it is
  refused);
- a preimage that matches 0 or >1 times yields `PATCH_FAILED` and is excluded
  from the denominator — no patch is ever silently applied to a neighbour;
- pinned-source drift aborts the run unless `--allow-drift`, and is then
  recorded in the output;
- the control (unmutated copy, full suite + corpus) must be green.

**MEASURED.** Control green, 28 tests OK. `patch_failed = 0`,
`compile_failed = 0`, all 64 preimages matched exactly once.

### 1.3 Liveness — the discriminator the first version lacked

A survivor has two possible causes: the mutation is real and the suite cannot
see it (a finding), or the patch is inert (a defect in the experiment). The
2026-08-08 version could not tell these apart. `probe_corpus.py` supplies the
missing discriminator: it runs all nine detectors over a fixed synthetic corpus
that does **not** reuse the audited fixtures, and hashes the results.

- **PROBE_SENSITIVE** — the mutant changes the pristine digest of the detector it targets.
  A PROBE_SENSITIVE survivor is genuine evidence that the bite-test pair does not
  discriminate that branch.
- **UNWITNESSED** — no digest changes. Such a survivor is reported but **must
  not** be read as evidence that the suite is weak; it may be an inert patch or
  a branch the corpus does not reach.

The corpus exercises all nine detectors (pristine episode totals: D-1 39, D-2
27, D-3 40, D-4 214, D-5 153, D-6 56, D-7 123, D-8 27, D-9 193 — **MEASURED**,
`python3 probe_corpus.py --counts`). It is a *liveness* instrument only: it is
not a truth oracle and establishes no validity.

### 1.4 Results

**MEASURED**, `python3 bitetest-audit/run_mutations.py`:

| Det | mutants | caught | caught_by_expected | survived | PROBE_SENSITIVE survivors | kill rate |
|---|---|---|---|---|---|---|
| D-1 | 8 | 2 | 2 | 6 | 4 | 25 % |
| D-2 | 6 | 2 | 2 | 4 | 2 | 33 % |
| D-3 | 4 | 3 | 3 | 1 | 1 | 75 % |
| D-4 | 6 | 2 | 2 | 4 | 3 | 33 % |
| D-5 | 8 | 2 | 2 | 6 | 2 | 25 % |
| D-6 | 9 | 2 | 2 | 7 | 6 | 22 % |
| D-7 | 8 | 1 | 1 | 7 | 7 | **12 %** |
| D-8 | 11 | 6 | 6 | 5 | 2 | 55 % |
| D-9 | 4 | 1 | 1 | 3 | 3 | 25 % |
| **all** | **64** | **21** | **21** | **43** | **30** | **32.8 %** |

`caught_by_expected` equals `caught` in every row: **no mutation was caught only
by a different detector's tests** (`caught_only_by_other_detector = 0`,
MEASURED). Every number above is therefore attributable to the pair under audit.

The full 64-row ledger, the retired entry, and the mutated-file SHA-256 of every
mutant are in `bitetest-audit/results/mutation-ledger.md`, regenerable with
`python3 bitetest-audit/render_ledger.py`.

### 1.5 The re-run does not reproduce `20/64`

**The new number is 21 caught of 64, not 20.** Per instruction, it is reported
as measured and not reconciled toward the old figure. The entire difference is
one mutant:

- The 2026-08-08 `D3-M4` widened D-3's shared-target proxy "to include WAIT" and
  was reported SURVIVED. That patch is **inert**. The command parser files a
  command under `TurnCommands.by_unit` only when `cmd.unit_id is not None`
  (`trace_detectors.py:410`), and `WAIT` is parsed with `unit_id = None`
  (`:393-394`), so `Trace.cmd_of` (`:493-494`) can never return a `WAIT`
  command and the widened branch is unreachable. **INFERRED** from those lines;
  **MEASURED** by re-running the original patch as `D3-M4-RETIRED`: it survives
  *and* is `UNWITNESSED`, consistent with inertness.
- It is retired (kept in the manifest, excluded from the totals, re-run so the
  delta is auditable) and replaced in the counted set by a live proxy mutation:
  `dests.setdefault(cmd.args[0], ...)` → `dests.setdefault((0, 0), ...)`, i.e.
  the destination-identity requirement is dropped so any two own MOVEs on one
  turn count as contention. That mutant is **CAUGHT**.

So the corrected reading of D-3 is *better* than the 2026-08-08 reading:
three of four D-3 mutants are caught, and clause (a)'s proxy identity is pinned
after all. The 2026-08-08 statement that "the pair does not pin which verbs
constitute a target claim" rested on the inert patch and is **withdrawn**.

### 1.6 What the kill rate is and is not

**The 32.8 % figure is descriptive of this selected mutant set only.** The
operators were reviewer-chosen, not sampled from a defined mutation
distribution. It is *not* an estimate that the suite covers roughly one third of
detector behaviour, and it must not be quoted as coverage. The load-bearing
content of the experiment is the *identity* of the 30 PROBE_SENSITIVE survivors, not the
ratio.

### 1.7 Single most decisive row: D8-M9

`test_oracle_matches_review_counterexample` (`test_trace_detectors.py:387-396`)
asserts `banana_exact_chop_turns(2, 4, 1, 1) == 5` versus `ceil_div(4, 1) == 4`
— the round-3 host review's terminal counterexample. Replacing the oracle's
*use* of the growth-aware count with static `ceil(health/chop)` inside
`conversion_race_oracle.py` **survives all four D-8 scenario tests and the whole
suite**, and is **PROBE_SENSITIVE** (MEASURED). The counterexample is asserted on a helper
function; no fixture routes it through `detect_d8`. The regression the host
review demanded is not defended at the detector level. This confirms accepted
finding 6 of the review.

---

## 2. Per-detector findings

Throughout: "the pair" = the trigger test plus its declared near-miss.

### D-1 — A→B→A movement (`trace_detectors.py:555-621`)

**What the pair asserts.** Trigger `test_trigger_period2_10_turns`
(`:120-127`): 10 turns of strict A/B alternation, no carry change ever; asserts
`verdict == "FAIL"`, `ep["k"] >= 3`. Near-miss #1
`test_near_miss_progress_event_inside` (`:129-134`): *the same* alternation with
one carry delta injected mid-window. Near-miss #2
`test_near_miss_short_window_k2` (`:136-139`): the same alternation truncated to
5 states.

**Property or implementation?** Implementation. **D1-M6** — deleting
`and (t == s + 1 or pos[t] == pos[t - 2])` (`:600`), the requirement that the
walk actually be A,B,A,B rather than merely "moving" — **survives and is PROBE_SENSITIVE**
(MEASURED). Under that mutant a unit walking in a straight line for seven turns
reads as a period-2 oscillation. Both fixtures only ever exhibit oscillation, so
the clause separating oscillation from motion is never exercised.

**Genuine near-miss?** #1 is genuine and single-dimensional; D1-M3 (CAUGHT,
PROBE_SENSITIVE) confirms the carry clause is pinned. But A2 defines *three* progress-event
kinds and **D1-M4** (plant appear/disappear) and **D1-M5** (inventory delta on a
DROP/PICK turn) both survive — both **UNWITNESSED**, so they are recorded as
`NO_FIXTURE` for those branches rather than as demonstrated blind spots. #2 pins
the window only within `[5, 9]` transitions: D1-M1 (`>=4`) CAUGHT; D1-M7 (`>=5`),
D1-M2 (`>=8`), D1-M8 (`>=9`) all SURVIVED and PROBE_SENSITIVE. The spec's `k >= 3` is not
established.

**Independent oracle?** None. `conversion_race_oracle.py` models tree growth and
travel races and has no notion of movement history. `UNRESOLVED`.

**Falsification probe (unchanged, not run).** Compare `detect_d1`'s episode
boundaries against the packet's host-computed `baseline_maximum_period2` metric
(`detector-selftest-report-2026-08-04.md` §2, e.g. game 897832286 unit 2, turns
160–286), window by window rather than in aggregate. That metric is computed by
the host, not by this code. `UNRESOLVED`.

---

### D-2 — Repeated PICK/DROP churn (`trace_detectors.py:624-679`)

**What the pair asserts.** Trigger `test_trigger_two_zero_net_cycles`
(`:153-161`): two PICK/DROP cycles at `DOOR`, carries `[0,1,0,1,0]`,
inventories `[5,4,5,4,5]`. Near-miss
`test_near_miss_single_pair_is_legit_seed_abort` (`:163-167`): one pair. The
discriminating condition is `picks < 2 or drops < 2` (`:657`).

**Property or implementation?** Implementation, of one of four conjuncts. Both
fixtures sit at `DOOR` and both are net-zero, so **D2-M4** (delete the door
restriction) and **D2-M5** (delete net-zero) both survive and are both **PROBE_SENSITIVE**
(MEASURED). If churn away from doors were the real defect, or non-net-zero churn
counted, the pair would pass identically.

**Genuine near-miss?** Yes, for the multiplicity conjunct only (D2-M3 CAUGHT).
The 12-turn window is pinned only within `(4, 120]`: D2-M1 (`>3`) CAUGHT;
D2-M6 (`>4`) and D2-M2 (`>120`) survive — both **UNWITNESSED**, so the window's
looseness is `NO_FIXTURE`, not a measured blind spot.

**Independent oracle?** None; bank churn is an inventory-ledger property.
`UNRESOLVED`.

**Falsification probe (unchanged, not run).** A differential ledger: recompute
`sum(inventory deltas) + sum(carry deltas)` per unit per sliding window from the
raw transcript using a second implementation, and compare against `detect_d2`'s
window arithmetic. `UNRESOLVED`.

---

### D-3 — Same-target / occupied-cell contention (`trace_detectors.py:682-754`)

**What the pair asserts.** Trigger `test_trigger_shared_move_target_2_turns`
(`:184-191`): two own units emit identical MOVE destinations `(6,1)` on turns 1
and 2, divergent on turn 3. Near-miss `test_near_miss_one_turn_transient`
(`:193-197`): identical destinations on turn 1 only. Discriminating condition
`len(run) >= 2` (`:715`).

**Property or implementation?** Implementation of a **proxy**, explicitly: A4 of
the self-test report states *"`target(u,t)` telemetry does not exist in recorded
traces; observable proxies used: identical MOVE destinations …"*.

**Genuine near-miss? — the best control in the suite.** It differs in exactly
one dimension (run length 1 vs 2) and pins the threshold from *both* sides:
D3-M1 (`>=1`) and D3-M2 (`>=3`) are both CAUGHT. **Corrected in r2:** the proxy's
destination identity is *also* pinned — D3-M4 (drop destination identity) is
CAUGHT. Three of four D-3 mutants are caught; D-3 has the highest kill rate in
the suite (75 %).

**What is still undefended.** Clause (b) — landing on a stationary-working peer,
`:723-753` — has **no fixture at all**: **D3-M3** disables it entirely, survives,
and is **PROBE_SENSITIVE** (MEASURED). Half the detector is unexercised.

**Independent oracle?** None. `UNRESOLVED`.

**Falsification probe — repaired, see §7.1.** The 2026-08-08 formulation
(commanded MOVE destination ≠ realized next position) is withdrawn.

---

### D-4 — Abandoned carried-wood return (`trace_detectors.py:757-826`)

**What the pair asserts.** Two triggers:
`test_trigger_non_bank_verb_during_commitment` (`:213-219`) and
`test_trigger_two_turns_without_progress` (`:221-228`). Two near-misses:
`test_near_miss_monotone_return_and_drop` (`:230-235`) and
`test_near_miss_single_stall_is_tolerated` (`:237-243`).

**Property or implementation?** Implementation. The fixtures pin the banned-verb
set (D4-M4 CAUGHT) and the lower edge of the stall tolerance (D4-M1 CAUGHT).
Both commitment-start conditions other than `MOVE`-to-door are unexercised:
**D4-M5** (delete the I-21 forced full-capacity start) survives and is **PROBE_SENSITIVE**;
**D4-M6** (delete the DROP-at-door start) survives but is **UNWITNESSED**
(`NO_FIXTURE`). So if the spec's notion of *when commitment begins* were wrong —
the exact question A5 resolves by fiat — the pair would not notice.

**Genuine near-miss?** `test_near_miss_single_stall_is_tolerated` is a genuine
one-dimension control and pins the lower edge. It does not pin the upper edge
(D4-M2, `nd_run == 3`, survives PROBE_SENSITIVE) because the `no_progress` trigger walks
*three* consecutive non-decreasing turns, not two.

**Retracted.** The 2026-08-08 text said *"in both trigger and near-miss the
distance strictly increases rather than merely stalling — so the very
distinction the near-miss is named after ('single stall') is not actually
present in the data."* **That statement is false.** See §7.2 for the measured
door-distance sequences and the correct, narrower explanation of why D4-M3
survives. The D4-M3 mutation finding itself is retained: it survives and is
**PROBE_SENSITIVE**.

**Independent oracle?** None. `UNRESOLVED`.

**Falsification probe (unchanged, not run).** Score-level counterfactual:
compare wood banked in the game against wood carried at the moment of each
flagged abandonment; the banked-wood total is referee output. `UNRESOLVED`.

---

### D-5 — Unbounded planting (`trace_detectors.py:829-888`)

**What the pair asserts.** Trigger `test_trigger_plant_outside_ring`
(`:259-264`): PLANT at `(6,3)`, Chebyshev 2. Trigger
`test_trigger_plant_after_cutoff` (`:266-273`): PLANT at `DOOR` on turn 299.
Near-miss `test_near_miss_early_ring_plant` (`:275-277`): PLANT at `DIAG` on
turn 1.

**Property or implementation? — split.** I-12 *defines* Ring as
`cheby(c, tent) == 1`; the trigger sits at Chebyshev 2 and the near-miss at
Chebyshev 1, and membership is pinned from **both** sides: D5-M1 (`!= 1` →
`!= 2`) and D5-M6 (`cheby==1` → orth-only) are both CAUGHT and both PROBE_SENSITIVE. For
the geometry clause the fixture and the property coincide because the property
*is* a geometric definition.

**Everything else about D-5 is untested.** **D5-M4** (cumulative |Ring| bound
disabled) survives and is **PROBE_SENSITIVE**; **D5-M5** (concurrent bound) survives
UNWITNESSED; **D5-M7** (global cutoff slack `+1` → `+40`) survives and is
**PROBE_SENSITIVE**; **D5-M2** (`2*CD` → `1*CD`), **D5-M3** (slack `+2` → `+20`) and
**D5-M8** (water branch collapsed) survive UNWITNESSED. The trigger plants at
turn 299 of 300 and the near-miss at turn 1 — the pair establishes only that a
cutoff exists somewhere in `(1, 299)`.

**Independent oracle? — claim demoted.** The 2026-08-08 text proposed that a
cutoff derived from `first_fruit_delay` "would be an oracle-grounded label" for
I-5. **That is withdrawn.** D-5's `orth_cutoff` branch governs the *orthogonal*
slot, whose payoff is wood via grow-chop-bank, not fruit. §7.3 measures the gap.
`first_fruit_delay` remains relevant only to a *diagonal* renewable-mother
branch, and D-5 has no such branch. `UNRESOLVED`, with no oracle currently
available for either cutoff.

---

### D-6 — Opponent-favored fruit creation (`trace_detectors.py:891-942`)

**Full treatment in §4.** Summary here.

**What the pair asserts.** Trigger `test_trigger_opponent_chopper_within_2`
(`:294-300`): PLANT at `DIAG` with an opponent (hp 1, cp 1) at `(3,0)`, BFS
distance 2; asserts `kind == "opp_chop_eta"` — clause `opp_x <= 2` (`:924`).
Near-miss `test_near_miss_opponent_far_away` (`:302-304`): the same plant with
the opponent at `(0,6)`, BFS distance 7.

**Implementation validity.** The pair tests one bound of one of three clauses.
**D6-M4** deletes clause (a1) entirely — survives, **PROBE_SENSITIVE**. **D6-M3** flips its
tie handling — survives, **PROBE_SENSITIVE**. **D6-M6** flips A7's contested "min over ALL
own units" — survives, **PROBE_SENSITIVE**. **D6-M7** removes the speed division from the
ETA — survives, **PROBE_SENSITIVE**. **D6-M5** deletes clause (b), the replay ground-truth
clause — survives, **UNWITNESSED** (the corpus never places an opponent on an
own-planted cell with fruits decreasing and its banana carry increasing, so this
is `NO_FIXTURE`, not a measured blind spot). The `opp_x` bound is pinned only to
`[2, 6]`: D6-M1 (`<=1`) and D6-M9 (`<=7`) CAUGHT; D6-M2 (`<=6`) and D6-M8
(`<=5`) survive PROBE_SENSITIVE.

**Truth validity.** `GATE_UNREADY`. **Contract authority: CONFLICT.** See §4.

---

### D-7 — Lost harvested fruit (`trace_detectors.py:945-1017`)

**Weakest discrimination in the suite: 1 of 8 caught, and all seven survivors
are PROBE_SENSITIVE** — the only detector where every survivor is independently witnessed.

**What the pair asserts.** Trigger `test_trigger_dropped_outside_door_is_lost`
(`:323-327`): HARVEST then DROP at `(2,2)`, inventories `[0,0,0]`. Near-miss
`test_near_miss_banked_at_door` (`:329-331`): the same at `DOOR`, inventories
`[0,0,1]`.

**Property or implementation?** The banking test at `:998-1001` is a
**conjunction**: `cmd.verb == "DROP"` AND `u.cell in tr.doors` AND `inv[BANANA]`
increased. The near-miss changes **both** the cell and the inventory
simultaneously, so neither conjunct is individually controlled — and mutation
confirms it exactly: **D7-M3** (delete the door requirement) and **D7-M4**
(delete the inventory-increase confirmation) both survive and are both **PROBE_SENSITIVE**
(MEASURED). Under D7-M3 a banana dropped in open field next to a tent counts as
banked; under D7-M4 a DROP the referee refused counts as banked. This is the
textbook multi-dimensional-control defect. It confirms accepted finding 3 of the
review.

Everything else survives and is PROBE_SENSITIVE too: D7-M1 (`age > 12` → `> 0`), D7-M8
(`> 2`), D7-M2 (end grace `T-6` → `T-600`), D7-M5 (delete the PLANT sink
exemption), D7-M6 (delete harvest provenance). The structural reason is that
both fixtures are **3 turns long**, so the 12-turn age clause and the 6-turn
end-of-game grace are unreachable by construction and the FIFO ledger never
holds more than one entry.

**Minimal repair (referred, not applied).** Two additional near-misses, each
varying one dimension: DROP at a door with *no* inventory increase (the
refused-DROP case), and DROP off-door *with* an inventory increase (whose
impossibility under the referee is itself worth asserting).

**Independent oracle?** None; fruit accounting is an inventory ledger.
`UNRESOLVED`.

**Falsification probe (unchanged, not run).** Transcript-level conservation:
`bananas that ever existed on own plants == banked + planted + held at end +
taken by the opponent`, every term read directly from the transcript.
`UNRESOLVED`.

---

### D-8 — Diagonal-mother chop (`trace_detectors.py:1067-1169`)

**Strongest detector in the suite: 6 of 11 caught.**

**What the pair asserts.** Base pair: `test_trigger_chop_diagonal_mother`
(`:347-354`) vs `test_near_miss_orthogonal_wood_slot_chop_is_legal`
(`:356-359`), single discriminating condition `c in tr.diag` vs `c in tr.doors`
(`:1113`). Amended pair (four tests, `:362-478`) exercises the two-part
exemption `lost and race_won` (`:1135`).

Genuinely property-level: `test_exempt_arrival_is_not_loss` (`:464-478`) — an
opponent adjacent at chop-start with a young unripe mother — is a real control on
the concept "arrival alone is not loss", and **D8-M6** (dropping ripeness from
the opponent deadline) is CAUGHT by it. That is the one place in the whole suite
where a fixture discriminates a conceptual revision rather than a constant.
D8-M1, D8-M2, D8-M4, D8-M5, D8-M10 are also CAUGHT.

**But the exemption consults the oracle the detector's own spec defines**
(`detect_d8` calls it at `:1121`), so the D8Amended tests are agreement-with-self
by construction. Five mutants survive; two matter and both are **PROBE_SENSITIVE**:

- **D8-M9** — growth-aware `exact_chop_turns` → static `ceil(health/chop)`
  inside the oracle. See §1.7.
- **D8-M11** — the health-decrease confirmation of an executed chop is reported
  but never asserted.

**D8-M3** (oracle race strictness `<` → `<=`), **D8-M7** (opponent deadline =
ripeness only) and **D8-M8** (drop the `kind == "BANANA"` restriction) also
survive but are **UNWITNESSED** on the corpus; they are `NO_FIXTURE` rather than
measured blind spots. Note `conversion_race_oracle.py:46-50` states the strict
inequality is load-bearing, and D8-M2 shows the *I-7* tie convention **is**
pinned — but no fixture places `completion_turn == opponent_harvest_turn`, so
the *oracle's* tie convention is not.

**Independent oracle?** `conversion_race_oracle` is **not** independent.
`asset_survival_oracle` (`conversion_race_oracle.py:282-382`) is unused by any
detector and strictly generalises it, so it is a partial independent label —
**but all four D8Amended fixtures give their opponents `cp=0`**
(`test_trace_detectors.py:377, 382`), and the module docstring states that with
zero opponent chop power `asset_survival_oracle` reproduces
`conversion_race_oracle` exactly. On these fixtures the two oracles are
identical by construction and cannot disagree.

**Falsification probe (unchanged, not run).** Re-evaluate every D-8 exemption in
the floor corpus under `asset_survival_oracle` with the opponents' **real** chop
powers and report every disagreement with `feasible`. Non-circular because
`asset_survival_oracle` is not on `detect_d8`'s call path. `UNRESOLVED` — and
see §6 on why no current panel evidence may be quoted.

---

### D-9 — Second-worker TRAIN displacement (`trace_detectors.py:1172-1224`)

**Status: `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`. See §6.** The 2026-08-08
`INAPPLICABLE` classification is superseded and is not re-asserted.

**What the pair asserts, for the single-trace clause.** Trigger
`test_trigger_banana_command_before_train_single_worker` (`:484-495`);
near-miss `test_near_miss_train_issued_first` (`:497-508`).

**Property or implementation?** Neither. The near-miss differs from the trigger
in **three** dimensions at once: a TRAIN is present, the banana command moves
from turn 1 to turn 3, and the own-unit count goes from 1 to 2. Because the
TRAIN is on turn 1, `first_train = 1` and the scan loop `break`s immediately at
`:1190` — the near-miss exercises *no* clause at all; it terminates before the
guard, the verb test and the unit-count test are ever reached. This confirms
accepted finding 4 of the review.

Mutation proves it: **D9-M1** (delete the `len(own_units) != 1` guard),
**D9-M2** (widen the banana-attributable verb set to any resource) and
**D9-M3** (`t >= first_train` → `t > first_train`) all survive and are all
**PROBE_SENSITIVE** (MEASURED). Only D9-M4 (guard → `!= 7`, which kills the *trigger*) is
caught. The pair establishes only that "some episode is emitted when a PICK
BANANA happens and no TRAIN has occurred".

**A genuine near-miss** would place the TRAIN at turn 2 with the banana command
still at turn 1 (isolating ordering), or keep a single unit with a non-banana
PICK (isolating the verb clause), or keep two units with no TRAIN (isolating the
unit-count guard). Referred, not applied.

**Independent oracle?** None. `UNRESOLVED` for the single-trace clause;
the paired clauses are `INSTRUMENT_UNSUPPORTED` (§6).

---

## 3. Branch-level evidence / authority / applicability table

One row per detector branch. `evidence` names the committed fixture and the
mutants that bear on it; `authority` names the artifact that defines the branch;
`applicability` is the instrument state. **All mutation entries MEASURED**
(`bitetest-audit/results/mutation-results.json`); authority entries **INFERRED**
from the cited documents.

Authorities referenced:
**SPEC** = `invariant-spec-2026-08-04.md` (status line: *"PUBLISHED FOR
INTEGRATOR REVIEW 2026-08-04"*, plus ratified revision blocks at `:516`,
`:546`, `:642`);
**DESIGN** = `design-banana-fsm-2026-08-06.md` (status line: *"DESIGN
(retrospective consolidation; no code changes)"*);
**A-notes** = `detector-selftest-report-2026-08-04.md` resolutions A1..A10;
**RULING** = `chatgpt_1/panel-train-instrument-ruling-2026-08-08.md`;
**ENGINE** = `rust/src/game/engine.rs` (sha256 `7c240abf…`, byte-sacred, read
only).

| Branch | Governing authority | Evidence that exists | Impl. validity | Applicability | Truth validity |
|---|---|---|---|---|---|
| D-1 (a) period-2 shape `pos[t]==pos[t-2]` (`:600`) | SPEC D-1 | trigger `:120`; **D1-M6 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-1 (b) window `k>=3` (`:605`) | SPEC D-1 | near-miss `:136`; D1-M1 CAUGHT; D1-M7/M2/M8 SURVIVED, PROBE_SENSITIVE | PARTIAL — bounded to `[5,9]` transitions | APPLICABLE | UNRESOLVED |
| D-1 (c) progress: carry change (`:580`) | A2 | near-miss `:129`; D1-M3 CAUGHT, PROBE_SENSITIVE | PINNED | APPLICABLE | UNRESOLVED |
| D-1 (d) progress: inv delta on DROP/PICK (`:584`) | A2 | none; D1-M5 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-1 (e) progress: plant appear/disappear (`:588`) | A2 | none; D1-M4 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-2 (a) `>=2` PICKs and `>=2` DROPs (`:657`) | SPEC D-2 | pair `:153`/`:163`; D2-M3 CAUGHT, PROBE_SENSITIVE | PINNED | APPLICABLE | UNRESOLVED |
| D-2 (b) window `<=12` (`:650`) | SPEC D-2 | D2-M1 CAUGHT; D2-M6/M2 SURVIVED, UNWITNESSED | PARTIAL — bounded to `(4,120]` | APPLICABLE | UNRESOLVED |
| D-2 (c) door-cell restriction (`:642`) | SPEC D-2 | none (both fixtures at `DOOR`); **D2-M4 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-2 (d) net-zero over window (`:667`) | SPEC D-2, A3 | none (both fixtures net-zero); **D2-M5 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-3 (a) shared MOVE target, run `>=2` (`:715`) | SPEC D-3, I-23 | pair `:184`/`:193`; D3-M1, D3-M2 CAUGHT | PINNED (two-sided) | APPLICABLE | UNRESOLVED |
| D-3 (a') destination-identity proxy (`:702`) | A4 | D3-M4 CAUGHT, PROBE_SENSITIVE (`D3-M4-RETIRED` inert, excluded) | PINNED | APPLICABLE | UNRESOLVED — proxy fidelity untested; §7.1 |
| D-3 (b) landing on stationary working peer (`:723-753`) | SPEC D-3 | none; **D3-M3 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-4 (a) banned non-bank verb (`:799`) | SPEC D-4, I-19..I-21 | trigger `:213`; D4-M4 CAUGHT, PROBE_SENSITIVE | PINNED | APPLICABLE | UNRESOLVED |
| D-4 (b) 2 consecutive non-decreases (`:819-823`) | SPEC D-4, I-20 | trigger `:221`, near-miss `:237`; D4-M1 CAUGHT; D4-M2, **D4-M3 SURVIVED, PROBE_SENSITIVE** | PARTIAL — lower edge only; equality semantics unpinned (§7.2) | APPLICABLE | UNRESOLVED |
| D-4 (c) commitment start: MOVE-to-door (`:787`) | A5 | both triggers | PINNED (by construction) | APPLICABLE | UNRESOLVED |
| D-4 (d) commitment start: I-21 full capacity (`:785`) | SPEC I-21, A5 | none; **D4-M5 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-4 (e) commitment start: DROP-at-door (`:789`) | A5 | none; D4-M6 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-5 (a) I-12 Ring geometry (`:846`) | SPEC I-12 | trigger `:259`, near-miss `:275`; D5-M1, D5-M6 both CAUGHT, PROBE_SENSITIVE | PINNED (two-sided) | APPLICABLE | `UNRESOLVED` — I-12 is the spec's own geometric definition; implementation conformance is `PINNED`, but a spec asserting a property does not validate that the property is the right world-state property to detect (ruling 2026-08-13). Definitional conformance: `IDENTICAL_TO_SPEC` |
| D-5 (b) I-13 cumulative bound (`:850`) | SPEC I-13 | none; **D5-M4 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-5 (c) I-13 concurrent bound (`:876`) | SPEC I-13 | none; D5-M5 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-5 (d) I-5 orthogonal cutoff (`:861-863`) | SPEC I-5 | trigger `:266` at turn 299/300; D5-M2, D5-M3 SURVIVED, UNWITNESSED | UNPINNED — value irrelevant at turn 299 | APPLICABLE | UNRESOLVED — no payoff oracle; §7.3 |
| D-5 (e) I-5 global cutoff (`:868-870`) | SPEC I-5, A6 | same trigger; **D5-M7 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-5 (f) water-boost CD selection (`:857`) | SPEC sec. 0 | none (fixture map has no water); D5-M8 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-6 (a1) arrival-order harvest race (`:920`) | **SPEC D-6 `:383-390` vs DESIGN F4 `:1170`** | trigger/near-miss `:294`/`:302`; **D6-M4, D6-M3, D6-M6 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE for the clause itself | APPLICABLE | **GATE_UNREADY — CONTRACT AUTHORITY: CONFLICT** (§4) |
| D-6 (a2) `eta_opp_x <= 2` (`:924`) | SPEC D-6 `:383-390` | pair `:294`/`:302`; D6-M1, D6-M9 CAUGHT; D6-M2, D6-M8 SURVIVED, PROBE_SENSITIVE | PARTIAL — bounded to `[2,6]` | APPLICABLE | GATE_UNREADY (§4) |
| D-6 (a3) ETA formula `ceil(bfs/speed)` (`:911`) | SPEC sec. 0 | none; **D6-M7 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-6 (b) replay ground truth: opp harvested ours (`:928-941`) | SPEC D-6 `:388-390` | none; D6-M5 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-7 (a) banking conjunct: DROP verb (`:998`) | SPEC D-7, I-8 | pair varies two dimensions at once | UNPINNED | APPLICABLE | UNRESOLVED |
| D-7 (b) banking conjunct: door cell (`:999`) | SPEC D-7, I-8 | **D7-M3 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-7 (c) banking conjunct: inv increase (`:1000`) | SPEC D-7, I-8 | **D7-M4 SURVIVED, PROBE_SENSITIVE** | UNPINNED | APPLICABLE | UNRESOLVED |
| D-7 (d) PLANT sink exemption (`:1002`) | SPEC D-7 | none; **D7-M5 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-7 (e) carried overage `age > 12` (`:973`) | SPEC D-7 | none — fixtures are 3 turns; **D7-M1, D7-M8 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-7 (f) end-of-game grace `T-6` (`:1012`) | SPEC D-7 | none; **D7-M2 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-7 (g) harvest provenance labelling (`:987`) | A8 | none; **D7-M6 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-7 (h) `lost_bananas` emission (`:1004-1007`) | SPEC D-7 | trigger `:323`; D7-M7 CAUGHT, PROBE_SENSITIVE | PINNED | APPLICABLE | UNRESOLVED |
| D-8 (a) diag-mother base predicate (`:1113`) | SPEC I-14, D-8 | base pair `:347`/`:356`; D8-M1 CAUGHT, PROBE_SENSITIVE | PINNED | APPLICABLE | UNRESOLVED |
| D-8 (b) plant kind `== BANANA` (`:1115`) | SPEC D-8 | none; D8-M8 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-8 (c) I-7 ownership flip, ties conceded (`:1062`) | SPEC I-7 | D8Amended `:415`, `:398`; D8-M2, D8-M5 CAUGHT | PINNED | APPLICABLE | UNRESOLVED |
| D-8 (d) exemption conjunction `lost and race_won` (`:1134`) | SPEC Revision 2026-08-05 | D8Amended; D8-M4, D8-M10 CAUGHT | PINNED | APPLICABLE | UNRESOLVED — circular: `detect_d8` calls the oracle its own spec names (`:1121`) |
| D-8 (e) oracle deadline = max(arrival, ripeness) | SPEC Revision 2026-08-05 `:546` | `test_exempt_arrival_is_not_loss` `:464`; D8-M6 CAUGHT, PROBE_SENSITIVE; D8-M7 SURVIVED, UNWITNESSED | PARTIAL — only the ripeness half is defended | APPLICABLE | UNRESOLVED |
| D-8 (f) oracle growth-aware chop count | SPEC Revision 2026-08-05; round-3 host review | helper assertion `:387-396` only; **D8-M9 SURVIVED, PROBE_SENSITIVE** | NO_FIXTURE at detector level | APPLICABLE | UNRESOLVED |
| D-8 (g) oracle strict-tie `<` | `conversion_race_oracle.py:46-50` | none; D8-M3 SURVIVED, UNWITNESSED | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-8 (h) health-decrease confirmation (`:1154`) | A9 | none; **D8-M11 SURVIVED, PROBE_SENSITIVE** (reporting field only) | NO_FIXTURE | APPLICABLE | UNRESOLVED |
| D-9 (a) single-trace `banana_before_train` (`:1189-1203`) | SPEC D-9, A10 | trigger `:484`, near-miss `:497` (breaks at `:1190`); **D9-M1, D9-M2, D9-M3 SURVIVED, PROBE_SENSITIVE**; D9-M4 CAUGHT | UNPINNED | **INSTRUMENT_UNSUPPORTED** (proxy retired, RULING §3) | GATE_UNREADY (§6) |
| D-9 (b) `train_late` (`:1214`) | SPEC D-9, I-16..I-18 | none — needs `--parent-commands-file` | NO_FIXTURE | **INSTRUMENT_UNSUPPORTED** (RULING §3) | GATE_UNREADY |
| D-9 (c) `train_missing` (`:1211`) | SPEC D-9, I-16..I-18 | none | NO_FIXTURE | **INSTRUMENT_UNSUPPORTED** | GATE_UNREADY |
| D-9 (d) `train_stats_differ` (`:1218`) | SPEC D-9, I-16..I-18 | none | NO_FIXTURE | **INSTRUMENT_UNSUPPORTED** | GATE_UNREADY |

**Counts over the 47 branch rows** (all figures counted from the table above).

| axis | tally |
|---|---|
| applicability | 43 `APPLICABLE`, 4 `INSTRUMENT_UNSUPPORTED` (all D-9) |
| contract authority | 45 `SETTLED`, 2 `CONFLICT` (D-6 (a1), D-6 (a2)) |
| implementation validity | 11 `PINNED`, 5 `PARTIAL`, 9 `UNPINNED`, 22 `NO_FIXTURE` |
| truth validity | 6 `GATE_UNREADY` (D-6 (a1), D-6 (a2), D-9 (a)–(d)), 41 `UNRESOLVED` |
| definitional conformance | 1 `IDENTICAL_TO_SPEC` (D-5 (a) I-12 Ring geometry), 46 `NOT_APPLICABLE` |

**22 of 47 branches — nearly half the detector surface — have no fixture at
all.** That, not the kill rate, is the load-bearing measurement in this audit.

**No branch in this table is currently adoptable as truth-validated**, and none
of them may be used in candidate acceptance until the required branches are
ready.

---

## 4. D-6 — a contract conflict, bound to the exact fixture state

### 4.1 What was wrong with the 2026-08-08 §4

Two independent defects, both accepted:

1. **Wrong state (BAR-2).** `TestD6.plant_with_opp` (`test_trace_detectors.py:283-292`)
   calls the shared `plant()` helper without overriding cooldown, and that
   helper's committed default is `cooldown=4` (`test_trace_detectors.py:44`).
   The audit declared the post-PLANT sapling to be
   `(size 1, health 3, fruits 0, cooldown 6)` and published turns derived from
   it. Every one of those turns was computed on a state `detect_d6` never saw.
2. **Wrong verdict class (BAR-3).** The audit called the D-6 near-miss
   `FALSIFIED` against `founding_safety_oracle`, on the premise that
   `design-banana-fsm-2026-08-06.md` had retired D-6's arrival-order predicate.
   **That premise assumed a supersession that was never ratified.** It is
   withdrawn.

### 4.2 The exact serialized states

**MEASURED**, `python3 -m unittest probes.TestD6ExactState` and
`bitetest-audit/results/probe-results.json`. The states below are read from
`Trace.state(2)` — the trace state in which the fixture's sapling first exists,
which is exactly the oracle's frozen post-PLANT anchor `t+1`
(`conversion_race_oracle.py:391-403`), so **no state is reconstructed and no
time-frame conversion is applied**: `plant_turn = 1`, `anchor_turn = 2`, and
every turn quoted below is absolute in that one frame.

```
TestD6.plant_with_opp, state(2), trigger  (opponent (3,0)):
  plants : [("BANANA", (3,2), size=1, health=3, fruits=0, cooldown=4)]
  units  : [(0, player 0, (3,2), speed 1, cap 2, hp 1, cp 1, carry 0*6),
            (9, player 1, (3,0), speed 1, cap 2, hp 1, cp 1, carry 0*6)]

TestD6.plant_with_opp, state(2), near-miss (opponent (0,6)):
  plants : identical
  units  : own unit identical; opponent 9 at (0,6), all stats identical
```

The two fixtures are byte-identical apart from the opponent cell — asserted in
`probes.TestD6ExactState.test_serialized_states_are_identical_apart_from_the_opponent_cell`.

### 4.3 The corrected arithmetic

Feeding those exact tuples into `founding_safety_oracle`
(`conversion_race_oracle.py:385-439`), **MEASURED**:

```
first_fruit_delay(1, 3, 0, 4) = 22        # the EXACT fixture sapling
first_fruit_delay(1, 3, 0, 6) = 24        # the state the audit assumed

detect_d6, trigger   -> FAIL, 1 episode
detect_d6, near-miss -> PASS, 0 episodes

founding_safety_oracle, anchor_turn = 2
  trigger   : our_h = 24  opp_h = 24  opp_destroy =  7   feasible_found = False
  near-miss : our_h = 24  opp_h = 24  opp_destroy = 13   feasible_found = False
```

**Every published number is retracted.** Side by side:

| quantity | published 2026-08-08 | exact state | status |
|---|---|---|---|
| sapling cooldown | 6 | **4** | retracted |
| `first_fruit_delay` | 24 | **22** | retracted |
| trigger `our_h` / `opp_h` / `opp_destroy` | 26 / 26 / 6 | **24 / 24 / 7** | retracted |
| near-miss `our_h` / `opp_h` / `opp_destroy` | 26 / 26 / 12 | **24 / 24 / 13** | retracted |
| `feasible_found`, both geometries | False | **False** | survives |

The review anticipated this precisely: *"the qualitative point may survive: the
exact fixture can still be unsafe through a ripeness tie or chop-out."* It does,
and both mechanisms are present on the exact state:

1. `opp_harvest_turn == our_harvest_turn == 24`. Ripeness (22) dominates travel
   (2 or 7), so both players stand on the cell long before the first fruit
   exists; the race is a tie, and `conversion_race_oracle.py:413-418` concedes
   ties because a simultaneous last-fruit HARVEST duplicates the banana to both
   players.
2. `opp_destroy_turn` (7 / 13) `< our_harvest_turn` (24). The opponent's chopper
   fells the sapling long before it could bear fruit.

**And the same caveat, now measured on the right state:** on this 9×7 fixture
map, with `first_fruit_delay = 22` and every BFS distance well under 22, **no
ring plant with any opponent present is founding-safe**. The fixture map cannot
express a founding-safe negative control, so the near-miss could not have been
one no matter which opponent cell was chosen. That is a fact about the fixture
map, not a verdict about `detect_d6`.

### 4.4 The conflict, stated as a conflict

Three committed facts, all **INFERRED** from the cited text:

- `invariant-spec-2026-08-04.md:383-390` — still the published detector catalog
  — defines D-6 as `eta_opp_h(c,t) <= min_u eta_u(c,t)` **or**
  `eta_opp_x(c,t) <= 2`, plus replay harvest ground truth. Its status line reads
  *"PUBLISHED FOR INTEGRATOR REVIEW 2026-08-04"*, and it carries three revision
  blocks (`:516`, `:546`, `:642`), none of which touches D-6.
- `design-banana-fsm-2026-08-06.md:1170` records review item **F4**: a new
  `founding_safety_oracle` replaces arrival-order with exact executable-HARVEST
  safety, and `:580` records that the candidate's A-17 plant-time guard now
  calls it. That document's status line reads *"DESIGN (retrospective
  consolidation; no code changes)"*.
- `trace_detectors.py:920` still implements the arrival-order test.

This proves **semantic drift between published artifacts**. It does **not**
prove that the retrospective design has the authority to supersede the standing
detector contract. **The 2026-08-08 framing — "`detect_d6` enforces a predicate
the design retired" — assumed a supersession that was never ratified, and is
withdrawn.**

Current state, in the review's own words and adopted verbatim:

```text
D-6 contract authority       : CONFLICT
D-6 implementation validity  : insufficient branch coverage
D-6 truth validity           : GATE_UNREADY pending ratified predicate
                               + independent oracle
D-6 floor counts             : diagnostic only; not verdict evidence
```

### 4.5 What ratification would require

The repository already contains the template: SPEC **Revision 2026-08-05 —
CONVERSION_RACE_ORACLE** (`invariant-spec-2026-08-04.md:546-560`) is a ratified
supersession. It names its source rulings (the round-3 host review at
`data/analysis/live-agent-6553250/banana-restoration-r2-round3-host-review-2026-08-05.md`
and the integrator ACK
`coordination/messages/local_codex_1/20260805T143001Z-20260802-banana-restoration-r2-ack.md`),
explicitly voids the three prior conflicting deadlines, and declares one named
oracle normative for spec, candidate, regression and detector simultaneously.

By that precedent, ratifying a D-6 predicate requires **all** of:

1. a numbered **revision block in SPEC** that names D-6, states the single
   authoritative world-state property, and explicitly voids the superseded
   formulation — as `:546-560` voids its three predecessors;
2. a **source ruling plus integrator ACK** cited in that block, by message path
   and branch;
3. a decision on **decomposition**: whether founding prevention, realized
   opponent harvest, and opponent chop-out are one detector or separate semantic
   branches. The table in §3 currently treats them as four branches
   (a1, a2, a3, b) because the code does;
4. **independent validation of the chosen oracle against referee transitions** —
   not merely adoption of a candidate design helper. `founding_safety_oracle` is
   today validated only by its own module self-test
   (`conversion_race_oracle.py:442+`);
5. **single-dimension trigger/near-miss fixtures rebuilt from the frozen
   property**, on a map where a founding-safe negative control is expressible
   (§4.3 shows the current 9×7 map is not such a map).

Until all five hold, **D-6 must not be quoted in any verdict**, in either
direction. The cross-oracle disagreement measured in §4.3 is a strong reason to
stop quoting D-6 — it is not a sufficient reason to declare the later oracle
automatically correct.

---

## 5. Detector-level summary (authority-bound)

Replaces the 2026-08-08 §3 table. `FALSIFIED` does not appear.

| Det | Applicability | Contract authority | Implementation validity | Calibration validity | Truth validity |
|---|---|---|---|---|---|
| **D-1** | APPLICABLE | SETTLED (SPEC D-1) | UNPROVEN — 2/8 caught; the A≠B≠A shape clause is deletable (D1-M6, PROBE_SENSITIVE); 2 of A2's 3 progress kinds have no fixture | UNPROVEN — D-1 *fires* on the parent lineage by design (4/4 packet games) | UNRESOLVED — no repo oracle can label oscillation |
| **D-2** | APPLICABLE | SETTLED | UNPROVEN — 2/6 caught; door-cell and net-zero conjuncts both deletable (D2-M4, D2-M5, both PROBE_SENSITIVE) | UNPROVEN — zero episodes over the floor corpus is consistent with both correctness and incapacity | UNRESOLVED |
| **D-3** | APPLICABLE | SETTLED | UNPROVEN — 3/4 caught; clause (a) and its destination proxy are pinned, clause (b) has no fixture (D3-M3, PROBE_SENSITIVE) | UNPROVEN — zero floor episodes; A4 states the true `target(u,t)` telemetry does not exist | UNRESOLVED — repaired probe available (§7.1), not yet run on refereed transcripts |
| **D-4** | APPLICABLE | SETTLED | UNPROVEN — 2/6 caught; the I-21 commitment start is deletable (D4-M5, PROBE_SENSITIVE); equality semantics unpinned (D4-M3, PROBE_SENSITIVE) | UNPROVEN — zero floor episodes | UNRESOLVED |
| **D-5** | APPLICABLE | SETTLED | **PINNED for the I-12 Ring-geometry clause only** (D5-M1, D5-M6 both caught). UNPROVEN elsewhere: I-13 bounds and all four I-5 cutoff constants survive | UNPROVEN — fires on the parent lineage by design (2/4 packet games) | `UNRESOLVED` throughout. Ring geometry is `IDENTICAL_TO_SPEC` on the separate definitional-conformance axis, which is not truth validity; cutoffs UNRESOLVED — no payoff oracle exists (§7.3) |
| **D-6** | APPLICABLE | **CONFLICT** (SPEC `:383-390` vs DESIGN F4 `:1170`) | UNPROVEN — 2/9 caught; clauses (a1) and (b) each deletable; `opp_x` bound pinned only to `[2,6]`; ETA formula unpinned | UNPROVEN — fires on the parent lineage by design (1/4 packet games) | **GATE_UNREADY** pending a ratified predicate and an independently validated oracle (§4.5) |
| **D-7** | APPLICABLE | SETTLED | UNPROVEN — **1/8 caught**, weakest in the suite; **all seven survivors PROBE_SENSITIVE**; both conjuncts of the banking test independently deletable because the near-miss varies both at once | UNPROVEN — zero floor episodes | UNRESOLVED |
| **D-8** | APPLICABLE | SETTLED (SPEC Revision 2026-08-05, ratified) | UNPROVEN (best of the suite) — 6/11 caught, incl. the arrival-vs-ripeness concept (D8-M6); growth-aware chop arithmetic (D8-M9, PROBE_SENSITIVE) and the travel half of the deadline survive | UNPROVEN — zero floor episodes | UNRESOLVED — circular: `detect_d8` calls the oracle its spec names (`:1121`); `asset_survival_oracle` is non-circular but degenerate on fixtures with `cp=0` |
| **D-9** | **INSTRUMENT_UNSUPPORTED** (RULING §3) | SETTLED as a contract; the proxy is retired | UNPROVEN for the single-trace clause — 1/4 caught; guard, verb set and ordering all deletable (PROBE_SENSITIVE) because the near-miss `break`s at `:1190`. NO_FIXTURE for the paired clauses | **not quotable** — no conclusion from the current panel may be cited (RULING §1, §4) | **GATE_UNREADY** (§6) |

---

## 6. D-9 — incorporating the TRAIN instrument ruling

The 2026-08-08 audit classified D-9's paired clauses `INAPPLICABLE` on the
ground that the panel cannot produce TRAIN. **That classification is
superseded** by
`chatgpt_1/panel-train-instrument-ruling-2026-08-08.md` (handoff
`20260808T224000Z`), which found two `m040` rows where the parent emits TRAIN
for 166/182 turns while the referee silently discards the command.

Adopted verbatim from the ruling:

```text
single-trace banana_before_train : DEFECTIVE / retire
paired TRAIN branches            : INSTRUMENT_UNSUPPORTED
current panel D-9 result         : GATE_UNREADY
```

Consequences this audit accepts and applies throughout:

- **The `INAPPLICABLE` classification is not re-asserted anywhere.** The
  2026-08-08 argument for it (a second worker injected at
  `second_worker_bias` 0.5, `can_train` false, PLUM granted below
  `training_cost`) described a harness that is itself invalid: a referee that
  parses `TRAIN`, discards it and advances the game is not an instrument that
  can establish inapplicability.
- **No mutation, fixture or floor result derived from the current panel
  establishes D-9 truth or applicability.** The mutation rows D9-M1..M4 in §1
  are statements about the *bite-test suite* on synthetic traces, not about the
  panel, and are reported as such.
- The 2026-08-08 D-9 falsification probe ("the 196 false positives are
  themselves the truth label") **is withdrawn**: those counts come from
  executions the ruling declares instrument-invalid. After TRAIN is implemented
  and conformance-tested, the paired clauses compare **successful referee TRAIN
  events**, and the corpus must be re-versioned and all 240 rows re-run
  (RULING §2, §5).
- The two `m040` map/seat/opponent identities remain mandatory regression rows
  with their old results archived as instrument-invalid (RULING §4). This audit
  makes no claim about them.

---

## 7. The three repaired probes

All three were written **first as assertions of the 2026-08-08 claim**, run in
that form, and only then corrected. The failing transcript is committed verbatim
at `bitetest-audit/results/probes-red-2026-08-09.txt` (sha256
`aeab241b14bd18431d3879368c451c4f7dc91a72d7e0970ce44bc01dc3fe5448`): **9 of 10
checks failed in the RED phase.** The corrected module is
`bitetest-audit/probes.py`; `python3 -m unittest probes` is now green at 18
tests.

### 7.1 D-3 — referee-predicted landing, not raw MOVE target (BAR-5)

**Retracted.** The 2026-08-08 probe proposed labelling referee displacement as
`commanded MOVE destination != realized next-state position`. A `MOVE id x y`
names a target that may be many cells away; under a speed limit the next state
is not expected to equal it.

**MEASURED** on the committed D-3 trigger fixture: the old comparison flags
**4 of 4** MOVE transitions as "displaced", including two ordinary one-step
travels. As a displacement label it is 100 % false-positive on this fixture.

**The repaired label**, implemented in `probes.referee_next_cell` as a mirror of
the authoritative engine `rust/src/game/engine.rs:98-144` (sha256
`7c240abf…`, read only):

1. compute the referee-predicted `next_cell` from the exact pre-state walkable
   set, the unit's position, its speed and the commanded target — including the
   engine's tie-break, which selects the **lexicographically smallest** in-range
   cell among those minimising BFS distance to the target
   (`engine.rs:137-143`);
2. compare that predicted landing to the realized next-state position;
3. distinguish obstruction/conflict displacement from ordinary partial travel;
4. reconcile against the same-player reservation order the engine actually uses
   — movers sorted by **descending id**, a cell taken only when
   `freq[cell] == 1` and unoccupied, then a circular-swap pass
   (`engine.rs:239-302`, `:308-335`);
5. compare D-3 episodes to that realized reservation/working-peer conflict
   event.

**MEASURED, and new.** On the fixture, unit 0's authored landings
`(1,1)→(2,1)→(3,1)` are exactly what `next_cell` predicts — the repaired probe
correctly reports no displacement where the old one reported two. **Unit 2's
authored landings are not referee-consistent**: from `(1,5)` toward `(6,1)` the
engine ties `(1,4)` and `(2,5)` at BFS distance 8 from the target and breaks the
tie to `(1,4)`, while the fixture asserts `(2,5)`; likewise at turn 2. The
committed D-3 fixture therefore **cannot serve as referee ground truth** for
this probe. The probe must be run on refereed transcripts, not on synthetic
fixtures.

Steps 4–5 require a refereed corpus. **UNRESOLVED** — the probe is specified and
implemented, the sweep is not authorized here.

### 7.2 D-4 — the stall is in the data (BAR-6)

**Retracted.** The 2026-08-08 text asserted that the near-miss contains no
stall. **MEASURED** door-distance sequences, from `tr.door_dist` on the exact
committed fixtures:

```
near-miss test_near_miss_single_stall_is_tolerated  (drop_turn = 4)
  positions   (2,2) (2,2) (3,2) (4,2) (4,2)
  door_dist       2     2     1     0     0
  inside the commitment interval : stall, progress, progress
  raw geometric scan             : stall, progress, progress, stall

trigger test_trigger_two_turns_without_progress
  positions   (2,2) (1,2) (0,2) (0,2)
  door_dist       2     3     4     4
  inside the commitment interval : retreat, retreat, stall
```

So the near-miss contains **exactly one genuine equality (stall) transition
inside the commitment interval**, at `door_dist` 2 — precisely the "single
stall" it is named for. (A raw scan also finds a second equality at turn 4, but
that transition follows the executed DROP at a door, which ends the commitment
interval at `trace_detectors.py:809-811`, so `detect_d4` never sees it. The
review's "one real stall" is the commitment-interval count, and it is correct.)

**The mutation finding is retained and the explanation corrected.** D4-M3
(`d1 >= d0` → `d1 > d0`) survives and is **PROBE_SENSITIVE**. It survives **not** because
the fixtures lack a stall, but because **no committed fixture contains two
*consecutive* equality transitions** — asserted in
`probes.TestD4StallClaim.test_no_fixture_has_two_consecutive_equality_transitions`.
The trigger reaches `nd_run == 2` on two strict **retreats** (2→3, 3→4), so it
fires identically under `>=` and `>`; the near-miss's single stall never reaches
`nd_run == 2` under either. Under both definitions every fixture stays below the
violation horizon, so the equality semantics are unpinned.

**Required fixture (referred, not applied).** An exact boundary case whose only
distinction is equality versus strict increase at the transition that would
complete the violating run: two consecutive `door_dist` equalities inside a
commitment interval. Under `>=` it must FAIL; under `>` it must PASS.

### 7.3 D-5 — `first_fruit_delay` is not a payoff oracle (BAR-7)

**Retracted.** The 2026-08-08 text proposed `first_fruit_delay` as an
oracle-grounded alternative to D-5's `ceil_div(3, chop) + 1` proxy, and listed
it in §5 as partially labelling D-5's I-5 cutoff.

D-5's late cutoff covers two economic paths, and the branch it actually
implements is the second:

- a diagonal renewable mother whose payoff is **fruit** — `first_fruit_delay`
  can inform this, and D-5 has **no such branch**;
- an orthogonal plant-grow-chop cycle whose payoff is **wood** — this is D-5's
  `orth_cutoff` branch (`trace_detectors.py:859-866`), and `first_fruit_delay`
  cannot see it at all. The standing design treats orthogonal bananas as wood
  vehicles.

**MEASURED**, dry orthogonal slot, chop power 1, sapling `(1,3,0,6)`:

```
first_fruit_delay(1,3,0,6)                          = 24 turns
grow-to-size-2 + growth-aware fell + travel/bank    = 12 turns
  =>  wood-cycle plant deadline   = 300 - 1 - 12 = 287
  =>  fruit-derived plant deadline = 300 - 1 - 24 = 275
  =>  D-5's committed orth cutoff (2*CD + ceil(4/1) + 2) = 282
```

A `first_fruit_delay`-derived cutoff would reject **12 turns' worth of
profitable orthogonal wood plants** (turns 276–287). The gap is not a fixed
offset either — it is 12, 14, 14 turns at chop powers 1, 2, 3, and
`first_fruit_delay` does not take chop power as an input at all. So it is
neither an upper nor a lower bound on the wood deadline, and cannot validate
D-5's orthogonal cutoff in either direction.

**The required oracle**, per the review, must model per branch

```
plant action -> growth timeline -> harvest or chop completion
             -> travel/bank completion -> score
```

and compare that to the actual turn cap and to successful referee events. No
such oracle exists in this directory; `orth_wood_cycle_turns` in `probes.py` is
a *demonstration* of the gap, not a proposed oracle — it hard-codes the
grow-to-size-2 target, ignores travel contention and carries no score model.
**UNRESOLVED.**

---

## 8. Independent-oracle availability

`conversion_race_oracle.py` exports three oracles. Corrected for r2.

| Oracle | Can label | Cannot label |
|---|---|---|
| `CONVERSION_RACE_ORACLE` (`:160-223`) | nothing independently — `detect_d8` **calls it** (`trace_detectors.py:1121`), so any D-8 check against it is circular by construction | D-1..D-7, D-9 |
| `ASSET_SURVIVAL_ORACLE` (`:282-382`) | D-8's exemption non-circularly (no detector calls it), by adding `opp_destroy_turn`. **But** all four D-8 fixtures set opponent `cp=0`, and with zero opponent chop power this oracle reproduces `CONVERSION_RACE_ORACLE` exactly — on the existing fixtures it is independent only in principle | D-1..D-7, D-9 |
| `FOUNDING_SAFETY_ORACLE` (`:385-439`) | D-6's *founding* property, non-circularly — no detector calls it. **But** it is one side of an unratified contract conflict (§4.4) and is itself validated only by its own module self-test, so it is a **candidate** oracle, not an adopted truth label | D-1..D-5, D-7, D-9; **and, corrected in r2, not D-5's I-5 cutoff** (§7.3) |

**Plainly: six of the nine detectors have no oracle available anywhere in this
directory, and none is cheaply derivable from the existing modules.** D-1
(movement), D-2 (bank churn), D-3 (contention), D-4 (wood banking), D-7 (fruit
accounting) and D-9 (training) are inventory-, command- or movement-level
properties; the oracle module models only tree growth, travel and harvest/chop
race timing. Their truth-validity cells stay `UNRESOLVED` until a label is built
from referee output.

One correction to the 2026-08-08 pessimism: the referee's own `next_cell` and
same-player reservation resolution (`rust/src/game/engine.rs:98-144`,
`:245-335`) **is** an available non-circular label for D-3, and §7.1 implements
the mirror. What is missing is a refereed corpus to run it on, not the oracle.

---

## 9. What could not be determined

- **Whether D-5's I-5 cutoff arithmetic is correct.** All four constants survive
  corruption under the current fixtures (two PROBE_SENSITIVE, two UNWITNESSED). No payoff
  oracle exists; `first_fruit_delay` is not one (§7.3). *Evidence that would
  settle it:* a grow-chop-bank-to-score oracle evaluated on every floor-game
  PLANT against realized banked value before turn 300. `UNRESOLVED`.
- **Whether D-3's MOVE-destination proxy tracks real contention.** A4 concedes
  the true telemetry is absent; §7.1 shows the committed fixture is itself
  referee-inconsistent, so it cannot answer the question. *Evidence that would
  settle it:* the repaired probe run on refereed transcripts. `UNRESOLVED`.
- **Whether D-2/D-3/D-4/D-7/D-8's floor silence is correctness or incapacity.**
  Zero episodes is compatible with both. *Evidence that would settle it:* seed
  each detector's positive fixture pattern into a floor trace via the existing
  builder (`make_banana_traces.py`) and confirm the detector fires on real
  transcript data. `UNRESOLVED` — and note that any such sweep must wait for the
  re-versioned corpus required by RULING §5.
- **Which D-6 predicate is correct.** Not determinable from this repository: the
  two candidates sit in artifacts of different, and unranked, authority (§4.4).
  *Evidence that would settle it:* the five ratification steps of §4.5.
  `UNRESOLVED`, and explicitly **not** falsification.
- **Whether `detect_d8`'s exemption would change under real opponent chop
  powers.** One measured data point (`asset_lost_turn` 25 → 11 with `cp=1` on
  `test_exempt_flip_then_feasible_conversion`'s chop-start state, verdict
  unchanged) is not a distribution. `UNRESOLVED`.
- **Anything about D-9 on the floor.** Instrument-unsupported (§6).

---

## 10. Bottom line

- **0 of 9 pairs establish truth validity.** Every pair is checked against the
  detector's own spec. For D-6 an alternative predicate exists in the
  repository, but it is one side of an **unratified conflict**, not a label that
  can falsify anything.
- **1 branch is validated by definition**: D-5's Ring geometry, and only because
  I-12 *is* a geometric definition. **1 pair discriminates a conceptual
  revision**: D-8's arrival-vs-ripeness control — but against the oracle the
  detector itself calls, so circularly.
- **47 branch rows** (§3): 11 PINNED, 5 PARTIAL, 9 UNPINNED, **22 NO_FIXTURE**.
  Four detectors (D-4, D-6, D-7, D-9) have near-misses that vary more than one
  dimension, which is why single-conjunct deletions survive.
- **Mutation: 21 caught, 43 survived out of 64 (32.8 %)** — *not* the 20/64
  reported on 2026-08-08; the difference is one retired inert mutant (§1.5). No
  mutation was caught by a detector other than its own. 30 of the 43 survivors
  are independently witnessed as live.
- **Weakest pair: D-7** — 1/8 caught with all seven survivors PROBE_SENSITIVE, and a
  near-miss that varies two dimensions at once. **Worst-constructed control:
  D-9's**, which `break`s before any clause runs. **Highest-stakes conflict:
  D-6**, which cannot participate in a verdict until §4.5 is satisfied.
- **No detector verdict in this artifact may enter candidate acceptance.** The
  detector gate remains `GATE_UNREADY`.

### Where I disagree with the review

Nowhere on substance. Two refinements, both evidence-backed:

1. **BAR-6, "one real stall".** Correct as the *commitment-interval* count. A
   raw geometric scan of the same fixture finds two equalities; the second
   follows the executed DROP that ends the interval (`trace_detectors.py:809-811`)
   and is invisible to D-4. §7.2 reports both numbers so the count is
   unambiguous.
2. **BAR-1, the mutant set.** The re-run does not reproduce 20/64. I report
   **21/64** and attribute the whole difference to one 2026-08-08 mutant that
   was inert (§1.5). I did not reconcile toward the old number.

---

## 11. Reproduction

All commands run from
`/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2`,
python3.12 stdlib only, no network, no pytest.

```sh
# baseline: the audited suite, unmodified
python3 -m unittest test_trace_detectors                    # 28 tests, OK

# mutation experiment (writes bitetest-audit/results/mutation-results.json)
python3 bitetest-audit/run_mutations.py

# regenerate the prose tables from the raw results
python3 bitetest-audit/render_ledger.py

# liveness corpus digests and episode totals
PYTHONPATH=. python3 bitetest-audit/probe_corpus.py --counts

# repaired probes (18 tests, OK) and their machine-readable dump
PYTHONPATH=.:bitetest-audit python3 -m unittest probes
PYTHONPATH=.:bitetest-audit python3 bitetest-audit/probes.py \
    --json bitetest-audit/results/probe-results.json
```

### Pinned inputs (SHA-256)

| Path | sha256 |
|---|---|
| `trace_detectors.py` | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `test_trace_detectors.py` | `b7ab897b1411f38cee61fedc4313ac72ed6ecd54ba5f794651f398a59d9e0079` |
| `conversion_race_oracle.py` | `e0896e3f7cb2c7ac4ced35350469d704432f8c7a1a8a4c9c4ce41495ca13ecf7` |
| `invariant-spec-2026-08-04.md` | `548479806d1268b9b12bd88dea0c4e5faa8f953617a5d5e5dea9e1e97351dfe1` |
| `design-banana-fsm-2026-08-06.md` | `96ad80ddbe214f325535d3f2381cdc2a5a9b15bd6360145530c48147b420b230` |
| `../../rust/src/game/engine.rs` | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |

The runner re-verifies the first three at every run and aborts on drift.

### Committed evidence (SHA-256)

| Path | sha256 |
|---|---|
| `bitetest-audit/mutation_manifest.json` | `e9d0c130c447667e3e374ba32f7b640112194b547a64ef123721d41bcfcdca22` |
| `bitetest-audit/probe_corpus.py` | `9afe7f3cf3cb073158e67226ddbed31a750cda19900fc031853195cb8b0f3ddb` |
| `bitetest-audit/probes.py` | `32bb38838ceb0ea8ae8d9a2c8edafd40f724ebff14d108119b29f578a1835f58` |
| `bitetest-audit/render_ledger.py` | `446b9772c90ef58047909efaa92e8e1db23bb9f8c18e4a24825159e1ebbc4e6d` |
| `bitetest-audit/results/mutation-ledger.md` | `3b9dd3dc89985b44f2539291bdab4651486cd2463a039affeef690292662f300` |
| `bitetest-audit/results/mutation-results.json` | `94f6af0bc15f4e93357be1e74309812321b64ddf6cd069e50daec9a7bf06636d` |
| `bitetest-audit/results/probe-results.json` | `302da05ba74f4c38140bb2124591e83d9efd8102bbb2199f2a9ef89bec33bf75` |
| `bitetest-audit/results/probes-red-2026-08-09.txt` | `aeab241b14bd18431d3879368c451c4f7dc91a72d7e0970ce44bc01dc3fe5448` |
| `bitetest-audit/run_mutations.py` | `c69247450ed4f35b2bcb102e3b678a1426d6c67a6cfa976b4204f13720297fe0` |

---

## 12. Boundary statement

No detector, test, gate, harness, candidate, parent, host run, value protocol,
TestSession, submission, restore or Arena state was modified. `trace_detectors.py`
and `test_trace_detectors.py` were read and executed only; every finding about
them is **referred to `local_claude_1`, not fixed**. `rust/**`,
`claude_1/pipeline/**`, `cgauto/**`, all bot/candidate/`.min.rs` files, the
`oscillation-library*` trees, `i30_*` and `score_hierarchy_*` were not modified;
`rust/src/game/engine.rs` was read for §7.1 and its sha256 is recorded above,
unchanged. Staged paths for this revision are exactly this file and the new
`claude_1/banana-restoration-r2/bitetest-audit/` tree.
