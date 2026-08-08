# I-30 implementation report — paired schedule/opponent-production exposure

Date: 2026-08-08
Author: `claude_1`
Execution reviewer: `local_claude_1` (assigned; **this report is not a gate verdict**)
Task: `20260808-phase1-work-allocation`, item 6
Branch: `agent/claude_1-banana-restoration-r2`

Authoritative specification: `chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md`
on `origin/agent/chatgpt_1`. Everything below is subordinate to that document.

---

## 1. Status summary

| item | result |
|---|---|
| mandated bite-tests (spec §10) | **15 of 15 implemented, 15 of 15 passing** |
| test methods in the module | 23 (22 for the fifteen + 1 supplementary, §7) |
| conservation identity on fixtures | holds **exactly** on all 12 valid fixtures; violated only by bite-tests 12 and 13, which are built to violate it, and both are `GATE_UNREADY` |
| statuses implemented | `NOT_APPLICABLE`, `UNPROVEN`, `GATE_UNREADY`, `PASS`, `FAIL`, plus the diagnostic sub-status `MEASURED_UNTHRESHOLDED` |
| `PASS` reachable in this repo? | **no** — no owner-frozen bound exists, so every active fixture is `FAIL` or `GATE_UNREADY`; the aggregate is `GATE_UNREADY` |
| pre-existing suites | `test_trace_detectors` 28 OK; `test_fuzz_panel` + `test_pre_review` 53 OK |

No numerical candidate threshold is proposed, implied or presented as owner-approved
anywhere in this work.

---

## 2. What was implemented

Three new modules plus one test module, all under `claude_1/banana-restoration-r2/`.
Nothing outside that directory was modified. No bot, candidate, parent, detector,
gate, host game, value protocol, TestSession, submission, restore or Arena file was
touched; `trace_detectors.py`, `fuzz_panel.py`, every `.min.rs` and everything under
`cgauto/submissions/` are byte-unchanged (`trace_detectors.py` is imported read-only).

### `i30_ledger.py` — deterministic opponent shadow referee (spec §5)

Consumes a `RunRecord` (transcript + command stream + identity hashes), parses it with
the **real** production parser (`trace_detectors.TraceParser` / `CommandParser`), then
reconstructs the opponent's score-bearing flow by exact state differencing:

- **asset provenance registry** (§5.2): map-seeded plants are `natural`; a new plant's
  creator is the player occupying its cell in the post-state; mixed occupancy is
  `unknown` and is never guessed;
- **atom carry** with `resource_kind`, `source_event_id`, `source_asset_id`,
  `source_class`, `source_creator`, `acquired_turn`, `acquired_verb` (§5.1), consumed
  FIFO;
- **deposits / withdrawals / losses / seed consumption / TRAIN bills** (§5.3);
- aggregates `DEP_OURS`, `DEP_OPP`, `DEP_NATURAL`, `DEP_UNKNOWN`, `TRAIN_SPEND`,
  terminal score, terminal turn, plus the §6 diagnostics (first productive turn,
  productive-turn count, opponent live assets, direct interactions with our assets).

Engine rules were re-derived from source rather than assumed
(`rust/src/game/engine.rs`, cross-checked against `docs/mechanics.md` and
`cgauto/mechanics_rederivation_audit.py`):

```
recompute_scores : score = PLUM+LEMON+APPLE+BANANA + 4*WOOD      (IRON scores 0)
near_shack       : |ux-sx| + |uy-sy| <= 1
apply_drop       : the whole carry vector moves into inventories[player]
apply_pick       : one item moves inventories[player] -> carry   (a bank WITHDRAWAL)
training_cost    : n + stat^2 in PLUM/LEMON/APPLE/IRON; BANANA and WOOD free;
                   IRON charged only when the map has iron terrain
```

### `i30_analyzer.py` — paired analyzer (spec §3, §4, §6, §8, §9, §11)

Pair identity, activation detection, the frozen per-pair quantities, the status model,
the §9 aggregate report and the hash-pinned `Bound` object. Also a CLI
(`python3 i30_analyzer.py --report OUT.json`) that emits the whole fixture corpus as
per-pair + aggregate JSON.

Fail-closed order — **instrument gates are evaluated before any bound is consulted**:

1. pair identity invalid or incomplete → `GATE_UNREADY` (`pair_identity`)
2. `D_UNKNOWN != 0`, or any untagged atom in either run → `GATE_UNREADY`
   (`unknown_provenance`)
3. pair residual `!= 0`, or either per-run residual `!= 0` → `GATE_UNREADY`
   (`conservation_residual`)
4. not `banana_active` → `UNPROVEN` if a Banana mechanism is claimed, else
   `NOT_APPLICABLE`
5. no bound → `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED` (`absent_bound`)
6. bound malformed / hash-pin mismatch / unsupported metric or operator →
   `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED`
7. bound exceeded → `FAIL`
8. bound satisfied **and** `provenance == "owner_frozen"` → `PASS`
9. bound satisfied but not owner-frozen → `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED`
   (`bound_not_owner_frozen`)

Raw values are preserved in the output at every status, including `GATE_UNREADY`
(§8). A pair identity mismatch sets `counted_in_denominator: true` and is never
silently dropped (§3).

### `i30_fixtures.py` — the fixture corpus

Real 11×9 map, real stdin-protocol transcripts, real command streams. Nothing here is a
bot, candidate, parent, submission or Arena artifact.

### `test_i30_invariant.py` — the fifteen bite-tests

All assertions are on exact integers, not on "nonzero" statuses (§10 closing sentence).

---

## 3. Exact commands to reproduce

```bash
git checkout agent/claude_1-banana-restoration-r2
cd claude_1/banana-restoration-r2

# the fifteen bite-tests (+1 supplementary): 23 tests, OK
python3 -m unittest test_i30_invariant -v

# regenerate the per-pair + aggregate JSON artifact (byte-deterministic)
python3 i30_analyzer.py --report i30/i30-fixture-results-2026-08-08.json

# pre-existing suites, unchanged
python3 -m unittest test_trace_detectors                       # 28 tests, OK
cd ../pipeline && python3 -m unittest test_fuzz_panel test_pre_review   # 53 tests, OK
```

Host: `python3` 3.12.3, standard library only, no pytest, no network, no credentials.
The analyzer is deterministic: re-running the CLI produces a byte-identical JSON.

Recorded RED state: commit `61e30e20`, evidence file
`i30/red-evidence-2026-08-08.txt` — `Ran 22 tests`, `FAILED (errors=22)`, 44
`NotImplementedError` frames. Every RED failure was "the ledger/analyzer is missing",
confirmed not to be an import typo by parsing a fixture transcript through the real
parser at that commit (`T=4`, tent `(4,3)`, opponent shack `(8,6)`, zero parser notes).
GREEN is commit `0edb66e0`.

---

## 4. Input SHA-256

Specification (identical blob at the handoff's declared `artifact_commit`
`cad16c4decf2eea72a8fc861725d9e3bd50502ad` and at branch head
`beebff2dc70bb7a742d1e6cb6a94e59bb8873d89`; git blob
`638e4ca906d09e2128a9de00276a2f125a931d43`):

```
beb34389593c3c8d5690a577f6c528b9b3c3488549f9c6d4902cf7679c45199d  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
```

New artifacts:

```
b393d639f28494191e9162b6d42966f2854aaa01d1c038a867b8cdd5509f74b5  i30_ledger.py
e94882319a9172e20df936167ac1583927f9e40768ec73c493ffd012397b37eb  i30_analyzer.py
a34f229252ded664158f181e32c493ed539cb550dc68bdd2f153d3a25744e974  i30_fixtures.py
0bd29b0cd1e6da6570f1282325034af4d5dfb5f995ceb08b9b7d526edf01ab44  test_i30_invariant.py
054ffea23486370e7c35b9fc3b1346e941fbb0939e292e0374600d63e7e29086  i30/i30-fixture-results-2026-08-08.json
c37b4bc2c94b2c9576ddf9bbccc74c2985bc926b994b25aa1ee20bfa8389a668  i30/red-evidence-2026-08-08.txt
```

Read-only inputs (unmodified):

```
59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209  trace_detectors.py
e0896e3f7cb2c7ac4ced35350469d704432f8c7a1a8a4c9c4ce41495ca13ecf7  conversion_race_oracle.py
7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05  rust/src/game/engine.rs
22c335cc712f3dd1dc07269657de9a5d79126cc4d35438f0b9d8ca44089e6944  docs/mechanics.md
```

Bound objects: none is owner-frozen. The only bound in the repo,
`i30_fixtures.TEST_BOUND_ZERO_WINDFALL`, carries
`provenance: "test_fixture"` and `owner_decision_path:
"UNRESOLVED/no-owner-decision-exists"`. It exists solely to exercise bound
arithmetic and **must not be cited as a threshold**.

---

## 5. Bite-test → spec section map, with measured values

| # | spec §10 clause | spec sections exercised | test class | measured |
|---|---|---|---|---|
| 1 | exact parent-vs-parent | §3, §6 | `TestBite01ExactSelfPair` | every delta and residual `0`; `NOT_APPLICABLE` |
| 2 | directly inert candidate | §3, §6 | `TestBite02InertCandidate` | command hashes differ, all deltas `0` |
| 3 | no Banana activation | §4, §8 | `TestBite03NoBananaActivation` | `NOT_APPLICABLE`; claimed-but-unexercised → `UNPROVEN` |
| 4 | direct theft only | §6, §7 | `TestBite04DirectTheftOnly` | `D_DIRECT=+1`, windfall `0`, `D_OPP=+1`, real D-6 fires |
| 5 | indirect production only | §6, §7 | `TestBite05IndirectProductionOnly` | `D_SCHEDULE=+2`, windfall `+2`, `D_OPP=+2`, **real D-6 = 0** |
| 6 | natural opportunity | §5.2, §6 | `TestBite06NaturalOpportunity` | `dDEP_NATURAL=+1`, `dDEP_OPP=0`, windfall `+1` |
| 7 | TRAIN-spend offset | §5.3, §6 | `TestBite07TrainSpendOffset` | gross deposits equal, `D_TRAIN=6`, windfall `-6`, `D_OPP=-6` |
| 8 | mixed cargo | §5.1, §5.2 | `TestBite08MixedCargo` | one DROP → ours `1`, opponent `1`, natural `1`, unknown `0` |
| 9 | longer-game schedule | §4, §6 | `TestBite09LongerGameSchedule` | terminal-turn delta `+7`, windfall `+1`, bank withdrawal `1` |
| 10 | D89-like blind spot | §1, §6, §7, §8 | `TestBite10BlindSpotFixture` | **all of D-1..D-9 PASS, D-6 = 0**, yet `D_SCHEDULE=+1`, windfall `+1` → `FAIL`, never `PASS` |
| 11 | self-pair hash mismatch | §3 | `TestBite11PairIdentityMismatch` | `GATE_UNREADY`, still counted in denominator |
| 12 | one untagged atom | §5.2, §6 | `TestBite12UntaggedAtom` | `D_UNKNOWN=1`, residual `0` → `GATE_UNREADY` |
| 13 | nonzero residual | §6 | `TestBite13NonzeroResidual` | residual `1`, `D_UNKNOWN=0` → `GATE_UNREADY` |
| 14 | absent bound / config hash | §8, §11 | `TestBite14AbsentBound` | `MEASURED_UNTHRESHOLDED` → `GATE_UNREADY`; also covers non-owner bound and hash-pin mismatch |
| 15 | remove the indirect calculation | §10 | `TestBite15MutationBitesTheIndirectTerm` | windfall `1 → 0`, status `FAIL → not FAIL`, D-6 unchanged at `0` |

Bite-tests 12 and 13 are deliberately **orthogonal**: 12 has residual `0` so only the
provenance gate can fire, and 13 has `D_UNKNOWN = 0` so only the conservation gate can
fire. Neither can pass by accident on the other's check.

Bite-test 15 detail: `SCHEDULE_WINDFALL` is computed by the module-level
`compute_schedule_windfall`, whereas the conservation residual is computed from the
ledger aggregates directly. Replacing that one function with `lambda …: 0` therefore
leaves the residual at `0` and leaves D-6 at `0`, and the blind-spot fixture's own
assertions are what break. The mutation is caught by the intended logic, not by a
neighbouring check.

---

## 6. Ambiguity resolutions and deviations — stated plainly

The spec is authoritative. These are gaps it does not cover, or places I did something
different. Each is labelled **RESOLUTION** (spec silent, I chose) or **DEVIATION**
(spec says X, I did Y).

**D1 — DEVIATION: `DEP_*` is net of bank withdrawals, not gross.**
Spec §6 says all `DEP_*` are "gross". But `apply_pick` moves items *out* of the same
inventory `recompute_scores` sums, so for any opponent that PICKs from its own tent the
frozen identity `D_OPP = D_DIRECT + D_SCHEDULE + D_UNKNOWN - D_TRAIN + RESIDUAL` cannot
close and every such pair would be permanently `GATE_UNREADY`. I therefore report
`DEP_<class>` **net of same-class withdrawals**, and additionally expose
`dep_<class>_gross` and `wdr_<class>` so nothing is hidden. No new term was added to
the frozen identity. Bite-test 9 exercises this path. **If the spec author prefers
gross, the identity in §6 needs an explicit withdrawal term.** Flagged for review.

**D2 — DEVIATION: an extra `provenance` field on the bound object.**
The §11 illustrative schema has no field that distinguishes an owner-frozen bound from
any other well-formed object, yet §8 and §11 require that a non-owner-frozen bound never
yield `PASS`. I added a required-for-`PASS` field `provenance`, which must equal the
literal `"owner_frozen"`. Anything else measures and reports normally but maps to
`GATE_UNREADY` / `MEASURED_UNTHRESHOLDED`. The analyzer cannot verify ownership itself;
this is a declaration, and the reviewer should treat it as such.

**D3 — DEVIATION: `FAIL` is emitted from a non-owner-frozen bound.**
With the fixture bound, an exceeded threshold yields `FAIL` rather than
`GATE_UNREADY`. This is the fail-closed direction (it can never manufacture an
acceptance) and it is what makes bite-tests 10 and 15 meaningful. `PASS` remains
unreachable without `provenance == "owner_frozen"`.

**D4 — DEVIATION: bite-test 10 asserts nine detectors, not "29 behavioural invariants".**
§10 clause 10 says "all existing 29 behavioural invariants and D-6 are satisfied". The
only executable implementation of that set on this host is `trace_detectors.py`'s D-1..D-9.
The test runs the real `td.run_all` and asserts **all nine verdicts are PASS**, plus
D-6 = 0 specifically. The 29 invariants are not individually executable offline.
Marked **UNRESOLVED**: whether nine detectors adequately stand in for 29 invariants is
a judgement for `chatgpt_1` / `local_claude_1`, not for me.

**D5 — DEVIATION: shadow ledger, not referee instrumentation.**
§10 requires fixtures to run "through the real parser, referee ledger and analyzer".
The real parser and the analyzer are used. There is no referee ledger: the offline
corpus is transcripts, and instrumenting the engine is outside the stated boundary.
Instead the ledger is a deterministic shadow referee that differences the recorded
state, which the transcript fully supports (it carries both inventories, every plant
and every unit's carry vector). **This is a genuine gap versus the spec's wording** and
should be closed by a referee-side ledger if/when engine edits are in scope.

**R1 — RESOLUTION: initial bank stock and initial unit carry are `natural`.**
The spec does not classify pre-existing stock. §5.2 says map-seeded things are
`natural`, and initial inventories are map-seeded (`official_mapgen.rs`), so both are
tagged `natural`. They are identical across an exact pair and cancel in every paired
delta. The alternative — tagging them `unknown` — would make every pair
`GATE_UNREADY` forever.

**R2 — RESOLUTION: FIFO for indistinguishable atoms.**
§5.1 permits multiset treatment and requires only counts by source class. Atoms of one
resource are consumed in acquisition order. This matters only for partial consumption
(a PLANT seed), since DROP always moves the whole carry vector.

**R3 — RESOLUTION: a plant's creator is the post-state occupant of its cell.**
Mixed or absent occupancy → `unknown`, never inferred from proximity or ownership
(§5.2 forbids guesswork). Consequence: a PLANT whose planter steps away in the same
observed transition is unattributable. The supplementary fixture in §7 originally hit
exactly this and was corrected rather than papered over.

**R4 — RESOLUTION: deposit/withdrawal split within one turn.**
Per resource per turn, `budget = inventory_delta + TRAIN_bill`; withdrawals and
deposits are solved from the carry-decrease and carry-increase candidates. When both
directions occur simultaneously for one resource the split can misattribute a *class*,
but the *net* is still exact, so the identity and the residual remain correct. Not
exercised by any fixture.

**R5 — RESOLUTION (important): TRAIN is derived independently, never as a remainder.**
TRAIN bills come from opponent unit spawns plus the engine `training_cost` formula. It
would have been much easier to define `TRAIN_SPEND` as whatever inventory movement was
otherwise unexplained — but then the conservation residual would be zero by
construction and bite-test 13 could never bite. The residual is a real cross-check
between an independently derived event stream and the observed terminal score.

**R6 — RESOLUTION: unknown-provenance gate is stricter than §2 clause 4.**
§2 requires `unknown` to be zero "for all score-bearing opponent deposits". I fail
closed on **any** untagged atom, whether or not it is ever deposited. Strictly
stronger; flagging in case that is not wanted.

**R7 — RESOLUTION: terminal state = the last observed state block.**
Commands issued on the final recorded turn have no observed effect and are not scored.

---

## 7. Test-quality evidence: mutation sweep

Bite-test 15 only proves that *one* mutation bites. I ran a wider sweep (each mutation
applied to a scratch copy, then the whole module re-run) to check the fifteen actually
constrain the implementation:

| mutation | caught? |
|---|---|
| `SCORE_WEIGHT` WOOD `4 → 1` | yes (after adding the §7 fixture — see below) |
| CHOP wood inherits `natural` instead of the asset's class | yes |
| opponent-created assets classified `natural` | yes (3 failures) |
| drop the unknown-provenance gate | yes |
| drop the conservation-residual gate | yes |
| drop the pair-identity gate | yes |
| allow `PASS` without owner freeze | yes |
| remove bank-withdrawal netting (D1) | yes |
| TRAIN bill not charged | yes |
| `SCHEDULE_WINDFALL` drops the `- D_TRAIN` term | yes |
| acquisition attributable to a long-dead plant | **no — see below** |

Two findings, both reported rather than hidden:

1. **The fifteen mandated bite-tests never deposit WOOD.** The frozen `WOOD=4` weight
   (§5.1) and the CHOP inheritance rule (§5.2) were therefore live but wholly
   unexercised: flipping the WOOD weight to `1` passed all fifteen. I added **one
   supplementary test** — `TestSupplementaryWoodChopCoverage`, explicitly *not* one of
   the fifteen — in which the opponent fells one natural tree and one of ours and banks
   both, giving `D_DIRECT=4`, `D_SCHEDULE=4`, `windfall=+4`, `D_OPP=+8`. Both mutations
   above are now caught. The fifteen are otherwise untouched.

2. **One hardening is not covered by any test.** The registry is never pruned, so
   consulting it alone would let a long-dead plant launder a later untagged atom. I
   require the plant to have actually been present in the pre-state before attributing
   an acquisition to it. No fixture exercises this, so it is hardening on reasoning
   alone, not verified behaviour. Marked **UNRESOLVED** for the reviewer.

---

## 8. UNRESOLVED / not implemented

- **No owner-frozen bound exists**, so `PASS` has never been produced and the `PASS`
  branch is exercised only by reasoning, not by a fixture. Deliberate: fabricating one
  would be inventing a threshold.
- **§9 "pre-registered map-cluster 95% interval"** is not implemented. It needs a
  pre-registered cluster definition and a multi-map corpus; the fixture corpus is a
  single map. `aggregate_report` emits per-map means but no interval.
- **§6 "opponent live-asset count and ripe-fruit exposure over time"** is implemented
  as a terminal count, not a time series.
- **Seat asymmetry is unexercised.** Transcripts are always our-side views, so `seat`
  is always `0` in the corpus. Seat is carried in the identity block and in the
  aggregate breakdown, but no fixture varies it.
- **Opponent families / multi-map / multi-opponent aggregates** are structurally
  implemented but exercised only by a single-family, single-map corpus.
- **D4 (nine detectors vs 29 invariants)** and **D5 (shadow ledger vs referee ledger)**
  above are the two substantive gaps versus the spec's wording.
- Whether **D1 (net vs gross `DEP_*`)** is acceptable is a spec-author decision.

---

## 9. Reviewer checklist (spec §12)

| §12 requirement | where |
|---|---|
| source paths and full hashes | §4 above |
| event schema and per-pair JSON examples | `i30_ledger.py` `_atom` / `RunLedger.to_json`; `i30/i30-fixture-results-2026-08-08.json` |
| all fifteen bite-tests | `test_i30_invariant.py`, mapped in §5 |
| exact parent-vs-parent result | bite-test 1; `fixture_01_exact_self_pair` in the JSON, all deltas `0` |
| one synthetic D89-like result, D-6 zero and I-30 positive | bite-test 10; `fixture_10_blind_spot`, D-6 `0`, windfall `+1`, status `FAIL` |
| explicit `MEASURED_UNTHRESHOLDED -> GATE_UNREADY` | `analyze_pair` steps 5/6/9; bite-test 14 |
| no numerical candidate threshold presented as owner-approved | §4 and §6 D2/D3 above; the only bound is marked `test_fixture` |

Adoption requires the assigned execution review by `local_claude_1`. Nothing in this
report is an accepted gate verdict.
