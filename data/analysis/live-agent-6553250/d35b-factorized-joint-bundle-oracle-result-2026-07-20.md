# D35b factorized joint persistent-bundle oracle — result (2026-07-20)

## Verdict

**Reject the frozen one-bundle grammar and leave confirmation sealed.**

The factorized representation is substantially more valuable than the earlier
resident-local job grammar: a terminal hindsight oracle selects a non-control
bundle at 238/316 eligible roots (75.32%) and adds **+34.989 seed-clustered
margin** over the productive farm.  It nevertheless fails the two suppression
requirements.  The oracle reduces opponent score only **8.712** points versus
the required 20, and its opponent remains **+96.525** above the independent
resident reference versus the required maximum of +65.

This is an upper-bound rejection, not a candidate.  No confirmation seed was
opened, no policy was trained, no source was integrated, and no TestSession,
submission, or Arena action occurred.

## Integrity

- Two final one-seed runs contain 1,392 rows each and are byte-identical at
  `dde9f0b36e558f22219a4400e4a22e88be8eb5e2e20257914c9473884722138c`.
- The development run covers all 160 seed/seat/opponent tasks.  Its scenario
  manifest records 316 eligible roots out of 320 nominal roots.  On seed
  9,200,004 against the resident, both seats finish with one farm worker and
  never reach the required two-worker root; these are evidenced ineligible
  scenarios, not dropped tasks.
- The matrix contains 316 controls and 19,904 non-control bundles.  Every root
  reproduces the uninterrupted farm terminal tuple exactly.
- There are zero duplicate options or keys, target collisions, malformed plan
  keys, crossing errors, inconsistent deltas, illegal direct commands, or
  branches above three workers.
- Role support passes the outcome-blind D35b.1 amendment: 166 roots expose
  `RENEW`, 244 expose `FELL_BANK`, and 244 expose `MINE_BANK`.
- The runner's nine Rust tests and the analyzer's six Python tests pass.

The first integrity sample exposed that the original 95%-of-all-roots role gate
contradicted the grammar whenever a fixed root had no ripe tree, qualified free
worker, or iron access.  D35b.1 replaced it with explicit opportunity fidelity
and absolute support before any oracle choice or aggregate outcome was
inspected.  No value threshold changed.

## Frozen development outcome

| Measure | Result | Requirement | Gate |
|---|---:|---:|:---:|
| Non-control selection | 75.32% | >=25% | pass |
| Seed-clustered margin gain | +34.989 | >=+20 | pass |
| Selected-root mean / median gain | +46.777 / +33 | >=+35 / >=+15 | pass |
| Own-score delta from farm | +26.277 | >=-20 | pass |
| Opponent-score delta from farm | **-8.712** | **<=-20** | **fail** |
| Own-score advantage over resident | +160.225 | >=+68 | pass |
| Opponent-score excess over resident | **+96.525** | **<=+65** | **fail** |
| Opponent-family breadth | 8/8 nonnegative; 8/8 >=+10 | 8/8; >=6/8 | pass |
| Repeated selected role tuples | 10 tuples with >=10 roots | >=2 | pass |
| Catastrophe frequency | 0.95% vs 1.90% farm | no increase | pass |
| Negative-margin mass | 1,553 vs 2,788 farm | no increase | pass |

All ten independent seed means are positive; the normal seed interval for the
margin gain is [+22.301, +47.678].  Opponent-family gains range from +28.000
against resident and ScriptBoss to +53.175 against the native three-worker
proxy.  This is broad joint-scheduling value, not one proxy exploit.

No train goal succeeds and every selected bundle uses `train=none`.  The result
therefore comes entirely from coordinating the existing two workers.  It adds
another independent confirmation that extra headcount is not an isolated
action: the bounded jobs cannot fund worker three before their assignment epoch
ends.

## Analysis at several abstraction levels

### Representation

Factorization solves the combinatorial-class problem found in D35a.  The oracle
uses 22 exact role tuples and selects ten of them at least ten times; no single
flat team signature is required.  Persistent unit jobs, collision-aware targets,
deterministic completion, and a separate global action are a viable controller
interface.

### Optimization

There is ample, predictable-looking action value for a future selector: 75% of
roots change, selected gain is positive at all 238 changed roots, and all eight
opponent means are positive.  PPO is therefore not blocked by absence of a
useful action space.  It remains blocked by an objective/action grammar whose
best terminal choice still lies outside the required suppression region.

### Economy

The oracle's +34.99 margin decomposes into +26.28 own production and only -8.71
opponent score.  Relative to the resident it has enormous own-score headroom
(+160.23) but spends too little of it on denial.  This is the same
production/suppression frontier found by D24--D34, now localized inside complete
two-worker assignments rather than whole-policy families.

### Job mechanism

Selected bundles containing `FELL_BANK` are the strongest suppressive family:
their conditional opponent delta is -16.61 and margin gain is +58.44.  Other
role-presence groups suppress only about 8--10 points.  Adaptive Gold and the
native three-worker proxy lose 23.73 and 25.70 opponent points on changed roots,
whereas ScriptBoss, SilverBoss, and the balanced proxy lose only 2.43, 4.00, and
5.97.  The current target catalog ranks trees by completion time and reward but
does not represent who created the renewable lineage.  It can choose a fell job
without being able to reserve an opponent crop as a distinct competitive
target.  That is the most specific remaining grammar gap; this interpretation
is an inference from the conditional results, not yet causal proof.

### Time

The all-root gain is +41.62 at turn 50 and +28.84 at turn 100.  Among selected
roots, the corresponding gains are +53.03 and +39.97.  Earlier coordinated jobs
have more compounding value, but both boundaries remain useful; another cutoff
sweep is not warranted.

### Transfer boundary

D35b uses authoritative official maps but fixed local mechanism opponents and
terminal hindsight.  Its positive value cannot qualify an Arena candidate, and
the two failed gates forbid fitting a policy to this teacher.  Confirmation
seeds 9,200,010--9,200,029 remain unopened.

## Next hypothesis

D35c should test a **provenance-aware competitive bundle grammar** on fresh
official development seeds.  Track exact planting claims from the prefix and
separate target ownership from the unit role:

- retain the complete D35b grammar as a paired control;
- add opponent-crop `FELL_BANK`, `HARVEST_BANK`, and `RENEW` targets as separate
  collision-safe target pools rather than increasing the generic nearest-target
  count;
- report natural, own, opponent, and ambiguous target attribution explicitly;
- keep workforce, roots, completion rules, and terminal oracle tie-breaking
  fixed; and
- require the enriched oracle to close the two measured suppression gaps while
  retaining the already-proved own-production and tail value.

If explicit competitive targets still cannot reduce the opponent sufficiently,
close one-shot bundles and advance to a repeated job-boundary controller.  Do
not tune D35b target count, thresholds, checkpoints, or train specs.

## Evidence and hashes

- protocol: `d35b-factorized-joint-bundle-oracle-protocol-2026-07-20.md`;
- integrity amendment: `d35b1-root-support-integrity-amendment-2026-07-20.md`;
- runner: `rust/src/bin/d35b_factorized_joint_bundle_oracle.rs`;
- analyzer: `cgauto/analyze_d35b_factorized_joint_bundle_oracle.py`;
- development TSV, scenario manifest, JSON result, and two repeat TSVs.

SHA-256:

- runner used for D35b rows: `6e49b2c53f4a23614db4835ea6eaf791db145c55c2721ce8eb0c123cc16e3d3a`;
- current runner: `b8e29876f77092e20487e5441c7bc154b98284377b4996ecec26763f8b17a754`
  after adding only the child-module hook that lets D35c reuse the frozen private executor; D35b
  row logic is unchanged;
- analyzer: `96c5f4c310959b80cee163c98d00d3931d16fe524a9fb68f1107f56872a4dc76`;
- development TSV: `bd18beeef2eced7e8c0e94a8b076bd9e22f62d22bf0e4aa4301e27d7ae46f551`;
- scenario manifest: `0991c9e4d017fa622a8e433057e4a6ce1af687c1e6ed7daef0718ce6b8983713`;
- result JSON: `2104a87e73f961cd44bc31a7910ece235922271b33340acaaee9b521eb825cb8`.
