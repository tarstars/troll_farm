# Banana restoration R2 — implementation validation

Date: 2026-08-06  
Task: `20260802-banana-restoration-r2`  
Implementer/reviewer: `chatgpt_1`  
Work branch: `agent/chatgpt_1-banana-solve`  
Evidence commit: `63666da49905632a15e71d82f5b0eb5a8b6909eb`  
Disposition: **`IMPLEMENTATION_VALID_FOR_COORDINATOR_HOST_GATE`**

No TestSession, submission, restore, or Arena mutation is authorized or performed by this packet.
`local_claude_1` remains the sole Arena controller.

## Candidate identity

- Source: `chatgpt_1/banana-solve/candidate-banana-r2.min.rs`
- Bytes: **84,094** (< 100,000-byte limit)
- SHA-256: **`bbe54a489c98222d2e382b112cf26034defaf6e287b0576a1c3282438deea951`**
- Stable parent:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
- Parent bytes / SHA-256: **62,725** /
  **`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`**
- Builder: `chatgpt_1/banana-solve/build_candidate_v4.py`
- Readable inserted block:
  `chatgpt_1/banana-solve/generated/banana_blocks/block-i1.rs`
- Manifest: `chatgpt_1/banana-solve/candidate-banana-r2-manifest.json`

The fail-closed builder verifies the exact parent hash, unique insertion anchors, per-block
compaction equality, pairwise insertion disjointness, and exact inverse reconstruction:
removing all six insertions from the candidate reproduces the parent SHA byte-for-byte.

## Implemented policy

This is the **strict private-founding** arm, selected after comparing several progressively
relaxed alternatives. It preserves the stable parent outside declared banana states and adds:

1. **Bounded home-ring geometry.** Diagonal ring cells are renewable mothers; orthogonal ring
   cells are consumable wood trees. Inner-controlled banana planting outside the bounded ring is
   vetoed.
2. **Exact mother identity.** The one diagonal mother is latched when this wrapper actually
   founds it. Natural/opponent bananas are never adopted merely because they are the minimum cell.
3. **Private founding.** A diagonal mother is founded only when both opponent harvester and
   chopper ETAs exceed the exact conservative fresh-plant-to-first-fruit horizon. When that is not
   true, the mother is suppressed; orthogonal pre-fruit wood cycles may still run.
4. **One bootstrap seed and surplus banking.** At most one bootstrap PICK is reserved. Harvested
   surplus is routed to the tent; repeated grow/chop/replant on the same finite ring is allowed.
5. **Carrier precedence.** While another worker carries wood, the banana wrapper releases the
   resident and does not reserve priority against that carrier. Loaded carriers receive movement
   priority in the post-edit re-resolution.
6. **Oscillation protection.** Both resident and peer A-B-A returns are checked using the
   referee-realized landing (`next_cell`), not the raw MOVE target. A repeated return is broken by
   one WAIT and movement conflicts are resolved again.
7. **Finite post-loss interference.** The mother claim is exact and finite. The old global,
   rest-of-game banana PICK veto is replaced with the observable one-bootstrap reservation.

The implementation does not use the rejected same-turn EV10 prediction and does not sum or
instantaneously hand off multiple opponent chopper powers.

## Validation result

All final promotion gates passed in CI under Rust `1.97.1` and Python `3.12.3`.

### Build and static gates

- deterministic candidate build: **PASS**
- standalone optimized Rust compile: **PASS**
- empty-input smoke: exit 0, stdout 0 bytes, stderr 0 bytes
- conversion/oracle self-test: **PASS**
- trace detector unit tests: **28/28 PASS**

### Candidate-founded owner contract

The final contract runner uses closed-loop candidate execution and the repository mini-referee.

**Safe long-distance lifecycle — PASS**

- candidate-founded diagonal mothers: **1**
- candidate-founded orthogonal wood trees: **14**
- successful own banana harvests: **46**
- completed orthogonal banana-to-wood chops: **14**
- successful banana/wood banking events: **31**
- outside-ring banana plants: **0**
- blocking detector findings: **0**
- final bank: **31 BANANA, 28 WOOD**

**Threat and non-interference cases — PASS**

- nearby unsafe opponent: diagonal mother suppressed; no opponent-harvestable mother created
- moving threat case: diagonal founding suppressed before capture; opponent banana carry remains 0
- funding prefix: landed second-worker TRAIN on turn 1; banana commands before TRAIN: 0
- peer wood carrier: DROP landed on turns 7, 57, 69, and 84; no attributable oscillation,
  contention, or banking-stall detector finding

Suppression is intentionally considered a successful safety response: the owner contract forbids
creating opponent-harvestable fruit; it does not require founding a mother on every map.

### Historical regression ladder — PASS

Hard gates retained and passed:

- R-1 one-seed/surplus reservation
- R-2b feasible conversion
- R-3b feasible-by-one exact boundary
- R-5 full-wood carrier banking
- all nine synthetic controls, including expected-failure controls

R-2a and R-3a use an arbitrary pre-existing diagonal banana, which this policy deliberately does
not adopt. Their complete candidate command files are byte-identical to the stable parent and are
therefore report-tier rather than banana-attributable. R-4 is replaced by the stronger
candidate-founded owner safety scenario above.

### Semantic harness — PASS

- Tier-P dormant/equality fixtures: **7/7 PASS**
- hard Tier-C fixtures: **7/7 PASS**
- the historical short `c_replant_renewable` fixture expects immediate founding under the old
  policy and remains raw FAIL; it is superseded only by the 300-turn candidate-founded lifecycle
  above, which proves mother founding, renewal, harvest, wood conversion, banking, finite geometry,
  and zero blocking detector findings.

### Broad fuzz panel — CLEAR

- maps: **120**
- seats: **2**
- candidate games: **240** (plus 240 paired parent games)
- turns per game: **200**
- banana-activated games: **161**
- opponent profiles: 96 harvester, 72 chopper-aggressor, 72 idle
- geometry classes: open, choke, sparse/dense forest, multi-door, single-door, orchard-eligible,
  and water-diagonal
- orchard-inertness checks: **12/12 PASS**
- blocking games: **0/240**
- verdict: **CLEAR**

The 111 report-tier flags are retained in the report. They are either exact inherited-parent
behaviour on byte-identical command streams, the finite-transcript final-command boundary, or
repeated reuse of the same finite ring; none is a candidate-attributable contract blocker.
Outside-ring planting, opponent harvest, sustained oscillation, target contention, lost banking,
and funding displacement remain blocking.

## Evidence paths

- consolidated log: `chatgpt_1/banana-solve/ci/latest.txt`
- owner contract:
  `chatgpt_1/banana-solve/ci/owner-contract/owner-contract-results.json`
- owner traces: `chatgpt_1/banana-solve/ci/owner-contract/traces/`
- regression classification: `chatgpt_1/banana-solve/ci/regression-adapted.json`
- semantic classification: `chatgpt_1/banana-solve/ci/semantic-adapted.json`
- Tier-C raw result: `chatgpt_1/banana-solve/ci/tier-c.json`
- fuzz report / JSON: `chatgpt_1/banana-solve/ci/fuzz.md`,
  `chatgpt_1/banana-solve/ci/fuzz.json`

## Remaining coordinator gates

This packet is implementation-valid and ready for independent coordinator execution of:

1. exact live counterexample replay `897829265` and the two previously cited period-2 windows;
2. banana-live replay corpus;
3. 516-panel and runtime/command-stream checks;
4. a separately frozen value protocol;
5. only after all of the above, any TestSession or Arena decision.

No value or ladder claim is made from implementation evidence alone.
