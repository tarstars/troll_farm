# Research queue

Current checkpoint, September 5: `BASELINE-RESTORATION-RESULTS-2026-09-05.md` supports and records
the one V439 restoration publication (submission 41245746 / agent 6704418), following 4/6 versus
2/6 wins on fresh paired real-agent blocks. Its rollout is complete, not a seventh-place result.
The separate training-timing repair in `next_bot/`
passes correctness checks but loses four points in its reused local panel, and is not bundled
into the live source. See `TRAIN-EGRESS-RESULTS-2026-09-05.md`; do not promote from timing alone.
The V439 rollout is now terminal: confirmed rank 28, rating 23.43, all 160 games, 95/0/65 and
zero deployment failures. See `V439-RESTORATION-MATURE-2026-09-05.md`. It remains the live source;
no publication is in flight. The seventh-place goal is still active.
The neighboring learned export was independently checked and is not a supported replacement;
see `NEIGHBOR-LEARNING-INVENTORY-2026-09-05.md`. Earlier queue notes below remain historical.

`PLANNING-MODEL-RESULTS-2026-09-05.md` now supplies a tested direct-endpoint forward model for
joint short-horizon planning. An independent official replay check found and locally corrected
plant-creation order; 2,889 supported transitions now match, with 560 unsupported moves retained
explicitly. A V439-based experimental planner is now integrated in `lookahead_search.rs`, with
source-size and exact-output checks. It is not selected for publication. Initial full-work timing
failed on 42/43,263 observed turns; exact top-k selection repaired the stalls without changing
commands. The eight-turn policy tied the local baseline and is not advanced. The predeclared
persistent-horizon follow-up gains three local wins and passes timing. The exact source audit
and previous 496-test suite passed, but the frozen field screen stopped on a compiler timeout
before candidate gameplay. The original failure stays recorded. A Claude-assisted packaging-only
lint-prefix repair passes 498 tests, clean default local builds, complete exact-source replay and
startup verification. Its separate one-request diagnostic still times out during compilation,
without the warning flood. No further platform games are scheduled. Claude is preparing a bounded
offline compiler-cost work; no gameplay change or publication follows automatically.
`COMPILER-COST-RESULTS-2026-09-05.md` closes no-inline and lean-legality attempts, records the
verified platform Rust1.90 toolchain and reproduces 29 real warm/cold opponent action differences.
Next bounded compiler experiment targets bulky stable-sort code for small lists, with preserved
comparison/tie semantics and a matched-toolchain control. No further platform request is scheduled.
See `LOOKAHEAD-FIELD-FAILURE-2026-09-05.md`. Do not restart the completed V439 rollout monitor.

Open items in priority order. One item per wake. Each item gets its design written in at the top
before any code, its result recorded in a dated results file and the README, and is then moved to
the closed list with the number that closed it. Add new items at the bottom of the open list with
a one-line rationale and the evidence behind it.

## Open

**Paused for reassessment, 2026-09-05.** The owner requested a from-scratch critical review of the
project and previous decisions. `CRITICAL-REVIEW-2026-09-05.md` takes priority over the experiment
order below. Item 37 is an untested hypothesis, not the next approved implementation plan. Validate
the evaluation method before constructing another candidate family; no historical result is erased.

Current work follows `EVALUATION.md`. The first bounded measurement is the frozen archived-policy
pilot in `FIELD-CALIBRATION-PROTOCOL-2026-09-05.md`, using actual adaptive platform opponents.
The historical authorization and quality-gate paragraphs below are superseded by that contract.

The pilot is complete: `FIELD-CALIBRATION-RESULTS-2026-09-05.md`. No tested policy won any of its
three real-opponent blocks; V468 had the smaller loss margin in all three. Next: executable
resource-denial/fallback fixtures and one capability-based productive continuation, with a
prospective new-map real-opponent comparison. Include an earlier archived reference (V368) before
calling V468 the champion. Do not resume item 37 by its old priority or publish V564 from the
legacy score gain. The current live source remains V543.

That continuation is now measured: `NEXT-BOT-RESULTS-2026-09-05.md`. Both productive profiles fix
the observed no-wood path but fail to outperform V368 on three fresh real-opponent blocks. V368
wins 2/3 versus 1/3 for each other policy. V439 matches all 900 commands of those V368 paths and
differs from V468 only by the removed resource-denial bonus. Next: a separately frozen single-change
V439/V468 confirmation on new maps and broader actual opponents, before more economy tuning or
publication. No automatic promotion of the new architecture or historical lucky rollout.

The isolated confirmation is closed in `DENIAL-CONFIRMATION-RESULTS-2026-09-05.md`: both V439 and
V468 went 1/0/5; denial improved several losing margins but did not add a win. Opposite-seat
collection/auditing now works and passed a two-game A/A check. `RENEWAL-CYCLE-RESULTS-2026-09-05.md`
records a repaired self-occupancy/shack planting selector and full-cycle renewal value. The new
parallel export still went 1/0/2 on the reused real-agent development maps and is not selected.
Next hypothesis: joint allocation of capital funding, timely denial and productive work. Both
current workers fund expansion before considering production, so adding another lower-priority
chop bonus would not test early denial. Preserve exact archived controls and freeze the next
behavioral/competitive experiment before running it. The historical numbered queue stays paused.

The scheduling-only ablation is now closed: `CAPITAL-RELEASE-RESULTS-2026-09-05.md`. A two-worker
ceiling, proposed as a bounded Claude-assisted patch and independently verified, releases work on
turn 3 and chops on turn 5 but adds no real-agent win (still 1/0/2) and loses eight local points.
It is not advanced to fresh confirmation or publication. Default-four behavior is preserved.
Next investigate useful first-hire capacity and early scarce-fruit denial together with productive
continuation; keep the exact V439 reference and distinguish actual resource denial from ordinary
early chopping. This remains a hypothesis requiring a new frozen design, not a quota sweep.

That denial test is now closed: `SCARCE-DENIAL-RESULTS-2026-09-05.md`. The released two-worker
policy gains the putibuzu development win, but both it and V439 win only 1/6 in a prospectively
frozen fresh comparison, with 0/4 target-rank wins. No publication or weakening of the decision
rule. Stop tuning that fixed coefficient on the newly consumed maps. The independent verified
TRAIN/MOVE timing issue is documented in `TRAIN-EGRESS-FINDING-2026-09-05.md`. Next assess direct
production-baseline restoration evidence and more integrated decision-making, including a
bounded read-only check of reusable neighboring learning artifacts. Do not launch training or
promote any learned artifact merely because a winning public strategy used neural networks.

**Overnight authorization, 2026-09-02 evening.** The owner said: "It's night time. I'm going to be
AFK. I want you to put all items into queue and execute all of them." Every item below is therefore
approved to start, in the order listed, one per wake. What stays forbidden: submitting to the
platform (the V468 gate walk in item 0 stops before any `platform_run*.py`), touching the team
repository, and replacing the 12-family gate. Closed item 3 measured V425 separately without
changing that selector.

On 2026-09-04 the owner later said that programs may be published on the platform. The charter's
quality restriction still applies: only a candidate that passes every gate step may use that
authorization.

Base and baseline since 2026-09-02 11:25 (owner-approved): candidates derive from
`candidate_v468_no_denial_bonus_module.rs` and are compared with
`candidate_v468_full_baseline_bridge_module.rs` (identity panel: 24 of 24 game rows equal). V468's
own gain is inside the baseline, so every panel now measures the new change alone.

### 37. Producer-first opening with a conserved-stock axe

V630's repaired producer averaged ten harvests and seven plants when present, but trained in only
8/24 rows at median turn 163 and left every fourth-worker row fruit-short at turn 220. Reverse the
acquisition order: replace V468's expensive harvest-zero second hire with an early cheap producer,
then use conserved opening stock and parallel fruit to buy the first carry/chop axe before turn 100.

## Closed

- Stock-light producer bridge before a mature-wood worker, V628--V630 (2026-09-05, queue item 36):
  a reciprocal three-worker swap repair reduced waits and made the independent producer lifecycle
  execute, but the `1/1/1/0` worker still trained in only 8/24 rows at turns 153--176. V628--V630
  scored `+0.00/-9.83/+7.00`, `+0.00/-13.42/+7.38`, and `+0.00/-13.42/+7.83` at turn
  100/200/final. No staged fourth worker trained: every producer-complete row remained short in
  plum, lemon, and apple at turn 220. No full panel or publication.
  `V628-V630-STOCK-LIGHT-PRODUCER-BRIDGE-RESULTS-2026-09-05.md`.

- Capitalized scarce-fruit mothers, V625--V627 (2026-09-05, queue item 35): plum, lemon, and dual
  source arms established their selected mothers by turn 220 in 17/24, 19/24, and 16/24 rows, but
  the minimum `1/2/1/2` worker trained in only two V626 and two V627 rows at turns 210--219. All
  audited untrained rows had sufficient apple and iron; capitalization merely shifted the shortage
  between plum and lemon. Final gates were `+0.00/-8.46/+0.33`, `+0.00/-14.71/+1.17`, and
  `+0.00/-14.13/-0.08`. No full panel or publication.
  `V625-V627-CAPITALIZED-SCARCE-FRUIT-MOTHERS-RESULTS-2026-09-05.md`.

- Reachable staged rank-one orchard workforce, V622--V624 (2026-09-05, queue item 34): banana-first
  quotas raised V623 to 9.79 banana plants and wood efficiency to 0.355 per chop, but none of the
  minimum `1/2/1/2`, `2/2/1/2`, or `2/3/1/2` third workers trained in 72 smoke rows. At turn 220
  the cheapest V622 had all apple and iron in every surviving row, while 21 of 23 rows lacked
  lemon and 10 lacked plum. Source reservation and source-tree protection could not overcome the
  exact-prefix single-harvester bottleneck; the final arms scored at best
  `+0.00/-11.38/+2.17`. No full panel or publication.
  `V622-V624-STAGED-ORCHARD-WORKFORCE-RESULTS-2026-09-05.md`.

- Replay-derived rank-one shack orchard reconstruction, V619--V621 (2026-09-05, queue item 33):
  exact V468 through turn 100 followed by one typed orchard allocator scored respectively
  `+0.00/-21.75/+1.42`, `+0.00/-22.00/+1.79`, and `+0.00/-26.21/+3.04` at turn
  100/200/final. V619 added 9.37 plants and 17.46 harvests but banked 1.50 less wood, planted
  11.46 apples versus only 4.62 bananas, and never trained a third worker in 24 rows. All three
  raid boundaries shared the conversion failure, so no full panel or publication ran.
  `V619-V621-RANK-ONE-SHACK-ORCHARD-RESULTS-2026-09-05.md`.

- Persistent producer seed transaction, V616--V618 (2026-09-05, queue item 32): all 107 explicit
  routed seed transactions across the three arms completed as plants with zero transaction drops,
  but the best cap-four arm scored only +0.00/-3.42/+9.88 at turn 100/200/final. Against its V595
  parent V618 planted 0.21 fewer crops, added 28.54 moves, removed 6.83 chops, and finished 0.54
  lower: explicit routes replaced native immediate plants rather than adding crop throughput. No
  full panel or publication. `V616-V618-PERSISTENT-PRODUCER-SEED-TRANSACTION-RESULTS-2026-09-05.md`.

- Own-worker chop/payout pooling feasibility, V615 measurement (2026-09-05, queue item 31): Java
  and Rust referees preserve unique same-player cell occupancy, while fatal chop damage and wood
  recipients are grouped by the plant's single cell. Two own workers can therefore never pool
  chop or carry; sequential pre-damage awards wood only to the fatal-turn worker. The distinct
  cross-player join was already rejected as V422. No candidate or panel.
  `V615-OWN-WORKER-POOLING-FEASIBILITY-RESULTS-2026-09-05.md`.

- Exact-second-train near banana reserve, V612--V614 (2026-09-05, queue item 30): every arm
  established exactly 2/4/6 early bananas in all 24 smoke rows, but full-game banana plantings
  stayed 8.00 versus V468's 7.96. The reserves displaced 0.88/1.88/2.96 native ring plants and
  diverted the axe from wild supply; score regressed monotonically by
  -4.38/-5.08/-5.96, -12.58/-11.58/-11.17, and -18.33/-17.54/-20.67 at turns
  100/200/final. No full panel or publication. `V612-V614-NEAR-BANANA-RESERVE-RESULTS-2026-09-05.md`.

- Cross-lineage frozen-panel portfolio bound (2026-09-05, queue item 29): 83 exact-length panels
  reduced to 53 exact-V468 files and 40 command-distinct behaviors. A checkpoint-safe row
  hindsight oracle gained only +25.55 final. The exact-map aggregate optimum reached
  +0.07/+5.58/+37.84; adding exact seat identity barely reached +0.02/+0.82/+44.36 with seven
  lineages, while a 69-feature leave-one-map-out stump scored -4.67/-4.71/-0.37. Existing-policy
  selectors are closed; no candidate or publication. `V612-CROSS-LINEAGE-PORTFOLIO-RESULTS-2026-09-05.md`.

- Carry-aligned mature second worker, V609--V611 (2026-09-05, queue item 28): V609's mandatory
  carry-three control scored +12.00/+20.38/+39.83 on the 24-game smoke; V610's isolated lane
  passed at +12.00/+29.83/+40.00. The frozen 192-game V610 panel reversed to
  -34.72/-49.37/-42.01 with 46 added losses. Carry three trained at turn 14 on the smoke map but
  mean 54.3 in the field, removing 29.21 harvests and 35.39 deposits. Carry four trained at turn
  98 even on the smoke. A checkpoint-safe row hindsight selector gains only +4.82 final, ruling
  out a narrow ETA cutoff as the +40 solution. No fresh panel, packaging, or publication.
  `V609-V611-CARRY-ALIGNED-MATURE-WORKER-RESULTS-2026-09-05.md`.

- Starter-isolated delayed mature orchard, V606--V608 (2026-09-05, queue item 27): all arms were
  exact V468 through turn 100. Unmasked cap six scored +0.00/-5.38/-4.88; isolated cap six and
  eight were gameplay-identical at +0.00/-6.04/-5.79. Isolation removed the starter's extra crop
  servicing and every movement issue, but V607 made 8.88 more chops, ran 9.67 turns longer, and
  banked 1.04 less wood. A lone carry-two axe collects only two of four wood when a mature tree
  dies; the remaining payout is discarded. No full panel, packaging, or publication.
  `V606-V608-STARTER-ISOLATED-DELAYED-ORCHARD-RESULTS-2026-09-05.md`.

- Explicit dual-capability second-worker lifecycle, V603--V605 (2026-09-05, queue item 26): after
  repairing a worker-self-occupancy selector defect, caps two/four/six scored
  -24.00/-23.13/-8.21, -39.63/-35.34/-8.63, and -36.75/-27.25/+5.96 at turn
  100/200/final on the 24-game smoke. V605 added 11.58 plants and 19.71 harvests but removed 36.34
  chops by turn 100; the worker-owned crops also pulled the inherited starter off 15.05 chops.
  Games ran 28.5 turns longer and opponents gained 84.33 score while own wood gained only 0.21.
  No full panel, packaging, or publication. `V603-V605-DUAL-WORKER-LIFECYCLE-RESULTS-2026-09-05.md`.

- Low-power producer-chop orchard conversion, V600--V602 (2026-09-05, queue item 25): caps
  one/two/three scored +0.00/-1.21/+10.58, +0.00/+0.92/+12.75, and
  +0.00/+0.92/+12.75 at turn 100/200/final on the 24-game smoke. V601 added 3.83 producer picks
  but only 0.54 plants; 72 of 207 picks were followed by `DROP`, total plants fell 1.92, and
  harvests stayed exactly flat. Caps two and three were gameplay-identical. No full panel,
  packaging, or publication. `V600-V602-LOW-POWER-PRODUCER-ORCHARD-RESULTS-2026-09-05.md`.

- Axe-seeded secondary orchard, V597--V599 (2026-09-05, queue item 24): live caps one/two/three
  scored +0.00/+3.46/+14.13, +0.00/+2.79/+13.54, and +0.00/+0.46/+13.00 at turn
  100/200/final on the 24-game smoke. Cap one retained all producer harvests and gained 3.25 wood,
  but added only 0.29 plants over V595. V468's axe already planted 8.58 crops; serial seeding and
  felling reduced that to 6.00, and larger caps added traffic rather than throughput. No full
  panel, packaging, or publication. `V597-V599-AXE-SEEDED-SECONDARY-ORCHARD-RESULTS-2026-09-05.md`.

- Producer-preserving owned-crop axe, V594--V596 (2026-09-04, queue item 23): protection-only
  scored +0.00/+1.79/+9.75 and size-two priority scored +0.00/+1.50/+10.46 at turn
  100/200/final on the 24-game smoke. V595 retained all harvests and gained 2.25 wood, but median
  first divergence was turn 234, waits rose 8.46 and plants fell 1.42. Any-fruit and empty-fruit
  mature priority were gameplay-identical. The boundary is safe but existing crop supply limits
  it to 26% of the required final gain. No full panel, packaging, or publication.
  `V594-V596-PRODUCER-PRESERVING-AXE-RESULTS-2026-09-04.md`.

- Maturity-owned two-worker lifecycle, V591--V593 (2026-09-04, queue item 22): typed ownership,
  refill and targets 2/3/4 scored +0.00/+15.83/+33.54, +0.00/+5.96/+33.21, and
  +0.00/+3.38/+31.17 at turn 100/200/final on the 24-game smoke. Target-two V591 entered the
  frozen 192-game panel and reversed to +0.00/-15.66/-22.20 with 15 added losses. It added 8.68
  plants, 20.37 chops and 4.42 wood, but replacing the producer removed 30.97 harvests and 39.18
  deposits. No fresh panel, packaging, or publication.
  `V591-V593-MATURITY-OWNED-LIFECYCLE-RESULTS-2026-09-04.md`.

- Bill-free two-worker parallel orchard, V588--V590 (2026-09-04, queue item 21): exact V468
  through turn 100 followed by capability roles and crop caps 6/8/10 scored respectively
  +0.00/-2.38/+13.04, +0.00/-4.33/+11.67, and +0.00/-5.42/+10.17 at turn 100/200/final on the
  24-game smoke. Cap six added 26.58 harvests and 59.21 moves but removed 3.63 plants, 31.71 chops,
  and 4.13 wood. The inherited allocator harvests globally before seed work and does not protect
  owned crops to maturity, so more capacity added plants without wood. No full panel, packaging,
  or publication. `V588-V590-TWO-WORKER-PARALLEL-ORCHARD-RESULTS-2026-09-04.md`.

- Fresh rank-seven replay gap re-baseline, V587 (2026-09-04, queue item 20): captured 1,735 unique
  current top-15 games with zero failures. The unchanged putibuzu agent/submission moved from
  24.92/rank 13 to 26.99/rank 7 as its public evaluation window changed; only one opponent overlaps
  V543's schedule. Rank seven and eight are almost entirely two-worker policies, while rank one's
  58 two-worker games average 34.72 plants, 47.53 own-crop wood, 60.71 final wood, and 43/1/14.
  Opened a scratch parallel-orchard controller; no candidate or publication in this evidence item.
  `V587-RANK7-GAP-RESULTS-2026-09-04.md`.

- Minimum third-worker bill escrow under V468, V584--V586 (2026-09-04, queue item 19): immediate,
  living-source, and ripe-source activation were gameplay-identical on the 24-game smoke. Each
  scored +0.00/-3.38/-13.17 at turn 100/200/final, went 17/0/7 versus V468's 19/1/4, removed 4.50
  picks/plants and 25.79 chops, and added 17.75 waits. None completed the full fruit bill or
  trained worker three. No full panel, packaging, or publication.
  `V584-V586-BILL-ESCROW-RESULTS-2026-09-04.md`.

- Surplus-funded cheap third worker with axe-only iron, V581--V583 (2026-09-04, queue item 18):
  all three arms were byte-identical to V468 across the standard seed and a fruit-heavy
  115.5-harvest seed, 48 games per arm. Even the `1/1/1/1` bill was never simultaneously banked
  after seed-pick reservation with 96 turns left, so no axe mining or extra train occurred. No
  full panel, packaging, or publication. `V581-V583-SURPLUS-AXE-HIRE-RESULTS-2026-09-04.md`.

- Continuous single-owner third-worker bill, V578--V580 (2026-09-04, queue item 17): V579's
  192-turn arm gained +7.25/+21.04/+34.46 on the 24-game smoke and was positive against all 12
  families, but scored -14.24/-26.83/-31.20 on the frozen 192-game panel and added 20 losses. It
  trained only three third workers, removed 55.53 harvests and 59.84 deposits, and added 113.70
  moves per game. No gate pass, fresh panel, packaging, or publication.
  `V578-V580-CONTINUOUS-STARTER-BILL-RESULTS-2026-09-04.md`.

- Per-role champion continuation with an opportunistic third-worker bill, V575--V577 (2026-09-04,
  queue item 16): explicit-ID action routing and a V468-priority cross-controller collision guard
  repaired the composition to zero movement issues. Cooldowns 48/32/16 then scored
  +0.67/+2.21/+0.17, +0.79/+3.75/-2.04, and +1.00/+2.54/+1.38 at turn 100/200/final on the
  24-game smoke. No arm issued a mine or third-worker train, and the best final gain was only
  1.38 versus the required 40. No full panel, packaging, or publication.
  `V575-V577-PER-ROLE-BILL-SPLICE-RESULTS-2026-09-04.md`.

- Observed-second-train champion prefix to dense scaling, V572--V574 (2026-09-04, queue item 15):
  exact V468 first-train command/turn pairs matched in all 192 rows and the capability repair
  handled all five harvest-zero second-worker specifications. V573 nevertheless scored
  -24.20/-49.43/-25.69 at turn 100/200/final, added 202.46 moves, removed 39.59 chops and 12.75
  harvests, and added 26 losses despite 159 third- and 93 fourth-worker completions. Crediting
  live fruit in V574 recovered 2.16 at turn 100 but lost another 16.08 final. Both failed every
  gate; no fresh panel, packaging, or publication. `V572-V574-OBSERVED-SECOND-DENSE-HANDOFF-RESULTS-2026-09-04.md`.

- Champion-prefix early banana wood reserve, V569--V571 (2026-09-04, queue item 14): after masking
  protected reserves out of V468's target view, limiting each tree to one harvested fruit, and
  delaying starts to turn 45, caps one/two/three scored -2.75/-5.21/-6.08,
  -5.38/-2.00/+6.88, and -5.75/-2.38/+5.38 at turn 100/200/final on the 24-game behavior smoke.
  All failed both checkpoint gates and the +40 requirement. The carry-one planter's trips and
  carry-two feller's partial four-wood pickup removed 36.5--54.6 chops and left every arm near
  47.5 wood versus V468's 53.2 while opponents gained 21.5--25.6. No full panel, packaging, or
  publication. `V569-V571-EARLY-BANANA-RESERVE-RESULTS-2026-09-04.md`.

- Capacity-two producer and ripe-first source collection, V567--V568 (2026-09-04, queue item 13):
  moving production to the carry-two worker increased third/fourth completions from 165/134 to
  173/159 and gained 27.87 final points over V566. Against V468, however, V567 scored
  -52.37/-91.06/+43.18 and went 147/2/43; it met only the final requirement. Ripe-first collection
  recovered 11.10 at turn 200 but lost 6.07 final versus V567, went 135/0/57, and failed every
  gate. Both failures persist outside noncritical blockage rows. No fresh panel, packaging, or
  publication. `V567-V568-CAPACITY-TWO-PRODUCER-RESULTS-2026-09-04.md`.

- One-axe dense opening, V566 (2026-09-04, queue item 12): reserving the higher-id second worker
  for immediate chopping recovered 44.14 turn-100 points versus V564, but the carry-one sole
  producer delayed worker three by about 69 command turns. Fourth-worker completions fell from 175
  to 134 and final score fell 156.16 versus V564. Against V468 it scored -24.61/-59.94/+15.31,
  went 158/2/32 versus 177/3/12, and failed all gate conditions. Seven noncritical move blockages,
  no critical issues; no fresh panel, packaging, or publication.
  `V566-ONE-AXE-DENSE-OPENING-RESULTS-2026-09-04.md`.

- High-capacity third worker, V564--V565 (2026-09-04, queue item 11): changing only V546's third
  worker to `2/3/1/2` added 40.24 final own score, 10.21 wood, 32.31 margin, eight wins, and nine
  fourth-worker completions versus V546; all 12 family deltas improved. It still trailed V468 by
  68.75 at turn 100 and 27.80 at turn 200. The elite `3/4/2/3` bill delayed worker three to turn
  158.25 and finished 32.85 behind V546. A hindsight selector can preserve both early checkpoints
  but gains at most 0.44 final points, so the dense opening cannot meet the gate. FAIL; no fresh
  panel, packaging, or publication. `V564-V565-HIGH-CAPACITY-THIRD-RESULTS-2026-09-04.md`.

- Rating-18+ worker-funding provenance audit, V563 (2026-09-04, queue item 10): the three active
  games contained seven hires, all matching commands, next-state births, exact debits, and
  tooltips. Every hire occurred at first affordability or one turn later; between hires the bots
  harvested 130 bill fruits and deposited 39 iron but issued zero chops. The two four-worker bots
  and V543 reached worker three at the same mean turn 61, but their capacity-three/four thirds
  reached four at 101 versus 145.5. At rating 14+, `2/3/1/2` converted 6/6 thirds to four workers;
  eleven other thirds converted 0/11. Evidence-only; no gameplay or platform change.
  `V563-WORKER-FUNDING-PROVENANCE-RESULTS-2026-09-04.md`.

- Harvest-free champion-prefix banana wood batteries, V560--V562 (2026-09-04, queue item 9): all
  caps were exact V468 through turn 100 and kept two workers, but cap one scored only +0.03 final
  after a -0.58 turn-200 dip; caps two/three were behaviorally identical and scored +0.05 after a
  -0.63 dip. Even without reserve harvesting, the chopper lost 2.26 chops, added 3.97 moves and
  2.38 waits, banked 0.13 less wood, and displaced 38 apple cycles across the panel. Opponents
  gained 1.22 per game and cap two/three added a loss. FAIL; no promotion or publication.
  `V560-V562-HARVEST-FREE-BATTERIES-RESULTS-2026-09-04.md`.

- Champion-prefix near-reserve banana orchard, V557--V559 (2026-09-04, queue item 8): all caps
  were exact V468 through turn 100 and kept two workers, but cap one scored +0.02 final after a
  -0.65 turn-200 dip, while caps two/three scored -0.01 after a -0.63 dip. Caps two and three were
  behaviorally identical. Ten added banana plants displaced 35 apple cycles; harvest routing added
  3.79 moves and 2.23 waits and protection removed 1.63 chops per game. In 52 changed games own
  score was flat while opponents gained 4.46. FAIL; no promotion or submission.
  `V557-V559-CHAMPION-PREFIX-BANANA-RESERVE-RESULTS-2026-09-04.md`.

- Planting-cadence constraint audit, V556 (2026-09-04, queue item 7): the three rating-18+ losses
  had banana supply and usable geometry on all 276 post-fourth-worker states, and reachable ripe
  bananas on 273, but V543 harvested and planted zero. Its 21 post-training births were 19 lemons
  and two apples; maintenance saturation blocked 188 states and established-crop refill occupied
  the other 88. Opponents produced 183 generations, 163 banana, against V543's 53. This is a
  six-tree/species policy lock, not seed or geometry scarcity; no candidate was built.
  `V556-PLANTING-CONSTRAINTS-RESULTS-2026-09-04.md`.

- Same-state chopper target audit, V555 (2026-09-04, queue item 6): among 1,593 comparable mature
  chop turns against rating-14+ opponents, V543 selected the best current cycle 1,554 times
  (97.6%). The 13 losses had ten actionable miss episodes and only six material episodes; their
  alternatives were natural or own-planted, never opponent-planted. The sole opponent alternative
  was a non-material turn in a +4 win. The target-choice branch is too small to explain the public
  wood gap; no candidate was built. `V555-CHOPPER-TARGET-AUDIT-RESULTS-2026-09-04.md`.

- V468-to-dense-economy handoff, V552--V554 (2026-09-04, queue item 5): exact V468 ran through
  turns 80, 100, or 120 before a lazy dense-controller start. Boundaries and legality were clean,
  but none of 192 turn-101 states could afford even the cheapest harvest-and-chop third worker.
  R1FA redirected both established roles for 80--130 turns; ring chops fell by about 40, moves
  nearly doubled, and final deltas were -52.7/-60.1/-59.9. A V546 recheck found only one
  nonnegative turn-100 row and no row meeting all gates, ruling out a selector workaround. FAIL;
  V543 retained. `V552-V554-DENSE-HANDOFF-RESULTS-2026-09-04.md`.

- Third troll funded by farm surplus, V551 prerequisite audit (2026-09-04, queue item 4): item 1
  failed its hard precondition. V548 moved third-worker completion from 77 to 134 of 192 games and
  median arrival from turn 140 to 105, proving the funding path engaged, but lost 40.70 points at
  turn 100, 7.17 wood and 23.39 margin versus its V481 parent and finished only +8.11 over V468.
  V472--V481 independently show that the new troll pays when trained but gathering its bill costs
  the existing apple or wood income. Closed without another candidate.
  `V551-THIRD-TROLL-PREREQUISITE-AUDIT-RESULTS-2026-09-04.md`.

- Stronger local opponent measurement, V550 (2026-09-04, queue item 3): a separate 13-family
  runner measured V425 against V468 without changing the frozen gate. All 208 identity rows
  matched, and the original 12-family mean remained 247.25. V425's training sequence matched
  public R1FA in all 16 games, but its score, wood, chop rate and plant rate were only 49%, 42%,
  46% and 25% of the 133-game public profile; it lost 0/16. Retain it only as an optional
  training-signature/adversarial diagnostic, not a validated R1FA proxy or gate family.
  `V550-V425-OPPONENT-MEASUREMENT-RESULTS-2026-09-04.md`.

- WAIT-only farm fallback, V549 (2026-09-04, queue item 2): replacing an exact non-starter wait
  with a V481-mother trip cut waits by 5.05 and added 15.60 harvests per game. Carrying the fruit
  then forced 8.87 more drops; total chops fell 18.01, wood fell 5.19, third-worker completions
  fell from 77 to 61, and margin fell 11.06 versus V481. The first idle action is not the whole
  cost of a farm job. FAIL; V543 retained. `V549-IDLE-FARM-FALLBACK-RESULTS-2026-09-04.md`.

- Second harvester for the opening farm, V548 (2026-09-04, queue item 1): harvest power one and
  routing the farm bill through worker two raised ring harvests by 27.2, trained the third troll in
  134 rather than 77 games and moved its median arrival from turn 140 to 105. It also diverted the
  main axe, losing 7.17 wood, 30.5 points at turn 100, 23.39 margin and 13 outcomes versus V481.
  Eight collision-jammed games were a secondary defect; zero-issue games retained the early loss.
  FAIL; V543 retained. `V548-SECOND-HARVESTER-RESULTS-2026-09-04.md`.

- Fund-before-hire checkpoint bridge, V547 (2026-09-04): holding later-worker bills through turn
  100 recovered 18.9 early points versus V546, but lost 20.3 at turn 200, 19.7 final score, 22.5
  margin, and two outcomes. It remained 54.0 behind V468 at turn 100, proving worker spending is
  only part of the opening deficit. FAIL; V543 retained.
  `V547-FUND-BEFORE-HIRE-RESULTS-2026-09-04.md`.

- Dense post-training source orchard, V546 (2026-09-04): cap 6 -> 10 added 5.66 plantings, 7.21
  wood and 18.21 margin per game versus exact V543 on the same 192 games, improving W/T/L from
  163/1/28 to 166/1/25 without changing the resident family. It still trailed V468 by 72.9 at turn
  100, so the absolute checkpoint gate failed and no holdout/submission opened.
  `V546-DENSE-SOURCE-ORCHARD-RESULTS-2026-09-04.md`.

- Platform first-output hardening, V545 (2026-09-04): removing V468 and the adaptive/rescue layers
  cut compact source from 99,825 to 70,981 units and p95 planning latency to 0.94 ms, but lost 77.0
  own points at turn 100 and doubled losses from 12 to 27 on the 192-game development panel. FAIL;
  V543 retained. `V545-FIRST-OUTPUT-HARDENING-RESULTS-2026-09-04.md`.

- V468 submission-gate steps (2026-09-02 evening, queue item 0): 59.5 % against the champion of
  record and 89.5 % against orchard 6 over 400 games each (V439: 62.2 % / 94.2 %), audit clean;
  not submitted, owner decides. `CHOP-TARGET-RESULTS-2026-09-02.md`.
- Opening farm feeding a third troll, V476 to V481 (2026-09-02, owner-approved multi-mechanism
  experiment): -5 to -10 at turn 100, +10 to +13 at 300, all FAIL; the starter is the apple income
  and cannot also fetch the bill. `OPENING-FARM-RESULTS-2026-09-02.md`.
- Neural clone of V439 (2026-09-01): a clone is bounded by its teacher; 0-1 of 20 wins. Archived
  under `/data/separate_troll_farm-working/nn/`.
- H10a spatial selector (2026-09-01): closed at selection, neither seed admitted.
- Door-factory grafts V441 to V454 (2026-09-01): none raised own score by more than 4 points.
- Single-slot grow-before-fell V457/V458 (2026-09-02): -4.0 and -3.2, the freed troll waits.
- Harvest-2 second troll without an apple reserve V455/V456 (2026-09-02): -39, starves the orchard.
- Third troll funded by mined iron V472 to V475 (2026-09-02, loop iteration 5): +25 when the
  bill completes (20 of 192 games), but the bill costs the gatherers' income; -1.7 to +4.6 overall.
  `THIRD-TROLL-RESULTS-2026-09-02.md`.
- Harvest power with an apple reserve V470/V471 (2026-09-02, loop iteration 4): -3.2/-1.5; the
  orchard survives but the second troll never harvests, so the talent only costs apples.
  `HARVEST-RESERVE-RESULTS-2026-09-02.md`.
- Chop-target bonuses removed, V468/V469 (2026-09-02, loop iteration 3): +8.8/+11.4 on the
  development panel, +3.4/+2.5 on 16 fresh maps, wood unchanged; V468 is a small safe gain, not the
  wood lever. `CHOP-TARGET-RESULTS-2026-09-02.md`.
- Mother bananas feeding the conversion loop V464 to V467 (2026-09-02, loop iteration 2): -7.8 to
  -12.1; the starter is saturated by the apple engine and the second troll cannot harvest, so the
  mothers idle a troll. `MOTHER-BANANA-RESULTS-2026-09-02.md`.
- Multi-slot door farm V459 to V463 (2026-09-02, loop iteration 1): V459-V461 never engaged the
  farm (seeds are planted by the regeneration path), V462/V463 protected the trees and lost 27
  points to idle time. `DOOR-FARM-RESULTS-2026-09-02.md`.
- Resubmitting V368 for a lucky reading (V424, 2026-09-01): 25.21 then 21.06; the reading is noise.
