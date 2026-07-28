# D175a bounded early planting — execution report

Date: 2026-07-29. Verdict: **CLOSED-AT-MECHANISM**. Trigger fidelity 100% (153/153
attributable instances). The fix is verified *correct* against its own frozen five-condition
conjunction and dramatically clears its own headline mechanism target (median first-plant
turn 13.0 vs the required ≤60, control ≈199.0) — but the own-crop reap rate mechanism gate
fails decisively (0.45% vs the required ≥5%, barely different from control's own 0.68% on
this panel), and — downstream of that — both the safety ratio and every value gate fail
badly. Per protocol, mechanism failure alone determines the verdict; safety and value are
reported for completeness and because they independently corroborate the same story.

## What was built

`YamoBot::bounded_early_plant_candidate(&self, view, unit) -> Option<Candidate>` — a scored
candidate, appended (when eligible) to the `Vec<Candidate>` the ordinary mid-game branch of
`commands()` already builds via `Self::main_candidates(...)`, scored 9,600–9,800 to
outrank ordinary CHOP (`1000×wood/turns`, rarely > a few thousand) and this file's own
`bank_candidates` (max 8,000) through the existing `select()` argmax + cross-unit conflict
resolution, while staying below the file's unconditional-override tier (`forced_move`
20,000). A new field `YamoBot.own_crops: BTreeSet<Cell>` (read-only bookkeeping mirroring
the pre-existing `opponent_crops` reconciliation, needed because `GameState::Plant` carries
no owner field) supports condition (b). Full design rationale, including why this uses
scored-candidate injection rather than D174a's post-selection-rewrite pattern, and the exact
operationalization of "bill-critical," is recorded in
`.superpowers/sdd/d175a-phase-markers.md` (written before any results were seen).

**9 new unit tests** covering every scenario the protocol's "Unit tests" paragraph lists
(full conjunction; 6+ live crops; after turn 120; no seed; no cell within distance 2;
bill-critical; endgame — using two independent, non-redundant routes to "not endgame":
turn>120 vs. the fuller `Self::endgame()` board-stripped-and-losing case; a positive
PICK-when-not-carrying case; and a full two-turn `commands()` integration test proving CHOP
resumes automatically the turn after a seed is consumed). `cargo test --bin
yamo_orchard_live`: 32/32 pass (23 pre-existing + 9 new). `cargo check` / `cargo check --lib`
/ `cargo test --lib resident_policy`: clean, 32/32 (confirms the `troll_farm::resident_policy`
re-export is intact). `cargo fmt -- --check`: clean.

## Compile-then-restore

Dev copy SHA-256 verified `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`
(prefix `fff6669b`) before editing, and equal to `rust/src/d171a_control_resident_snapshot.rs`
(the frozen control). Built `rust/src/bin/d175a_bounded_early_planting_panel.rs` (mechanical
adaptation of `d174a_opportunistic_mining_panel.rs`: seeds 9,856,000–9,856,255/256 maps,
`D175A_DEBUG_TASK`, output filenames; task-matrix/threading/NDJSON machinery otherwise
byte-identical) with the fix present (build-time SHA `de2db365...`). Captured the fix as
`data/analysis/live-agent-6553250/d175a-fix-as-tested.patch` (372 lines), then immediately
`git checkout -- rust/src/bin/yamo_orchard_live.rs`: SHA re-verified
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` (exact match), `git
status --porcelain`/`git diff --stat` both empty. Re-ran the built binary's debug-task path
post-restore: identical output, confirming the compiled artifact is unaffected by the source
restore (as expected).

Pre-lock precise-pattern grep (`9,?856,?(000-255)`) of `data/analysis/` and `docs/` found 3
hits, all confirmed false positives on inspection (digit substrings inside unrelated
floating-point values in D11-curriculum PPO training JSON, e.g. `6473.090089856158`). Range
is fresh and disjoint from D171a/D173a/D173b/D174a's own ranges.

## Trigger fidelity: PASS (100%, 153/153 attributable instances)

Method: for a `random.Random(175002)` sample of 150 activated tasks (of 4,087), located each
task's ground-truth first-divergence turn (state provably identical between control and
candidate up to and including that turn), identified every own unit whose selected command
differed from control's, and independently re-derived in Python — a line-for-line
reconstruction of `bounded_early_plant_candidate`, including a from-scratch turn-by-turn
replay of `own_crops` mirroring `reconcile_opponent_crops` — what that unit's command
*should* be.

202 changed-command instances total. **49 classified `collateral_reassignment`** (command
does not match the Python reconstruction, and is not itself a PLANT/PICK command) and
excluded from the denominator: `select()`'s 2-unit joint pairwise score-sum optimization can
shift a *different*, untouched unit's chosen command as a side effect of this fix adding one
high-scored candidate elsewhere in the same turn. Spot-checked one instance in full (seed
9,856,201, seat 1, opponent `legend_balanced`, turn 2): the starter, adjacent to the shack
with bank APPLE stock, correctly triggers the fix's PICK — but `endgame_candidates`'s own
*pre-existing* PICK-conversion branch (reached because this unit had no reachable chop
target that turn) already independently proposed the identical `PICK 1 APPLE` at a much
lower score, so the command is textually unchanged for that unit even though the fix fired;
the freshly-trained teammate's command still shifts purely because the now-far-more-dominant
duplicate candidate reshuffles the joint optimum. Verified this exact shape explains all 3
sample tasks with only collateral instances and no visible directly-attributable one.

**Zero** instances of the genuine failure modes (a PLANT/PICK command whose conditions the
reconstruction rejects, or a predicted firing that didn't match what was observed). The
remaining **153/153 (100.0%)** match the reconstruction exactly. GATE (≥90%): **PASS**.
Output: `artifacts/experiments/d175a-bounded-early-planting/d175a-trigger-fidelity-check.json`
(+ `.py`, the checking script, alongside it).

## Panel

`LC_ALL=C`, seeds 9,856,000–9,856,255 × 8 families × 2 seats = 4,096 tasks. jobs20 (with
trajectory dump): 99.557s, **4,087/4,096 activated (99.8%)**. jobs1 (TSV only): 851.2s;
`sha256sum` confirms jobs1/jobs20 TSVs byte-identical
(`96ed3b692668067042ed86d8aa4233242b6bdcc98fbf88f5c263d715b1423e9c`). Trajectory NDJSON:
control always (4,096 lines, 540 MB), candidate only for the 4,087 activated tasks (601 MB).
Outputs under `artifacts/experiments/d175a-bounded-early-planting/`.

## Integrity — clean

All pass: 4,096/4,096 rows, task matrix exact, all games done, 9/9 inactive tasks byte-exact
to control (0 mismatches), jobs1/jobs20 byte-identical.

## Mechanism — 3 of 4 sub-gates pass; own-reap rate fails decisively

| Gate | Control | Candidate | Threshold | Pass? |
|---|---:|---:|---:|---|
| Median first-plant turn | 199.0 (mean 184.7) | **13.0** (mean 14.3) | ≤ 60 | **pass** |
| Own-crop reap rate | 0.68% | **0.45%** | ≥ 5% | **FAIL** |
| Peak concurrent own crops (mean) | 1.92 | **1.98** (median 2.0, max 4) | ≤ 8 | **pass** |
| No waste-sweep detector worse by > 10% | — | — | — | **pass** |

Detector detail (candidate vs control, all within tolerance): `idle_with_work` **−58.7%**
(134,352→55,451 episodes — a large *improvement*, expected: units that previously had
nothing to do now have a plant/pick action available), `unbanked_carry` **−19.6%**
(214→172), `door_queue` **−5.1%** (3,754→3,564), `harvest_slack` **+5.7%** (42,829→45,288,
within the 10% tolerance), `late_train_window` 0.0% (16→16), `repeated_failed_command` 0/0.

### Root cause of the mechanism failure

The fix works exactly as designed on its own narrow terms: median first-plant turn falls
from 199 to 13 — a 15× improvement, far beyond the ≤60 bar, using the frozen five-condition
conjunction with 100% trigger fidelity and near-universal activation (99.8% of tasks). But
**this fix only ever changes when the first plant happens, not what happens to the plant
afterward.** The fate of any planted crop — self-chopped for wood, reaped for fruit, or
taken by the opponent — is governed entirely by pre-existing, untouched machinery (the same
`regeneration_commitments`/`endgame_candidates` "convert plants toward wood, not toward a
renewable orchard" grammar CONSTRAINTS.md already records from D87, and B4.5 §1's own
finding that this is "structurally a late-game condition" independent of when planting
first becomes reachable). Own-crop reap rate stayed at 0.45% (candidate) vs 0.68% (control)
on this panel — both far below B4.4's field reference (0.93% for the actual resident, itself
already 16–18× below every two-worker peer's 15–17%) — because unlocking *when* planting can
start does nothing to unlock *reaping* it: that is a structurally separate mechanism this
experiment's frozen scope never touches (no harvest-priority change was in scope; only
planting priority was). This is exactly the shortfall the protocol asked to have quantified
if mechanism failed: **a 15× tempo win with essentially zero improvement in the metric that
was meant to prove the planted crops become a renewable fruit loop rather than a relabeled
wood-conversion detour.**

## Safety — ratio technically undefined-by-sign-flip; reported as FAIL

| | Δown (activated, n=4,087) | Δopponent (activated, n=4,087) |
|---|---:|---:|
| Mean (candidate − control) | **−5.41** | **+21.09** |

Raw ratio Δopponent/Δown = −3.90, which trivially satisfies a naive `ratio ≤ 0.40` by sign
flip — reported here as a **FAIL**, not a pass, because the ratio's premise (how much of a
genuine own-score *gain* leaks to the opponent) does not apply when Δown ≤ 0. Own score
*fell* under the candidate while the opponent's *rose* — a strictly dominated outcome, worse
in kind than the leak the safety gate was built to bound, not merely a borderline case of it.
This is directionally consistent with — and now a further, execution-panel-level
confirmation of — B4.5 §5's field correlation (own planting volume correlates with the
opponent's own score, surviving a game-length confound check) and D89's own causal finding
(private production relaxes the suppression pressure that would otherwise slow the
opponent's economy): diverting early turns from chopping/suppression to planting/picking
both directly loses our own tempo (chopping is 94.7% of the resident's score channel per
B4.4) and gives the opponent more room to run, simultaneously.

## Value — fails all six sub-gates, strongly negative

| Gate | Result | Threshold | Pass? |
|---|---:|---:|---|
| Overall mean | **−26.44** | ≥ +1.0 | **FAIL** |
| Map-clustered 95% CI | **[−28.96, −23.92]** | lower ≥ 0.0 | **FAIL** |
| Activated-subset mean (n=4,087) | **−26.50** | ≥ +1.0 | **FAIL** |
| Worst family (compact_gold) | **−51.31** | ≥ −1.0 | **FAIL** |
| Catastrophes | 229 vs control 130 | not above control | **FAIL** |
| Negative-margin mass ratio | **1.97** | ≤ 1.05× | **FAIL** |

Every opponent family is negative (best: `resident` −11.97; worst: `compact_gold` −51.31,
followed by `gold_adaptive` −46.34). Worst five individual tasks range −301 to −328 margin
points, all against `gold_adaptive`/`compact_gold`/`legend_balanced` — the same
"complete-economy" opponent archetypes B4.5 §2/§3 already flagged as denser/leaner-board
families where this kind of relaxation bites hardest.

## Standing conclusions

1. The fix is verified correct and effective at its own narrow, literal job: 100% trigger
   fidelity across an independently-reconstructed conjunction, and a 15× reduction in
   median first-plant turn (199→13), comfortably clearing the mechanism gate that measures
   it, with near-universal activation (99.8%).
2. The mechanism gate fails for a precisely diagnosed, structurally-separate reason:
   own-crop reap rate is essentially unchanged (0.68%→0.45%, both far below the 5% bar and
   both far below every real two-worker peer's 15–17%) because this fix's frozen scope only
   ever touches *when* planting first becomes reachable, never what happens to a plant
   afterward — that remains the pre-existing wood-conversion grammar CONSTRAINTS.md already
   documents as a separate, previously-rejected mechanism (D87).
3. Both downstream gates independently corroborate the same failure, more severely: value
   is catastrophically negative across every opponent family (worst −51.3, 229 vs 130
   catastrophes), and the safety picture is a strictly dominated outcome (own score down,
   opponent score up) — a third independent confirmation, alongside D89's controlled result
   and B4.5's field correlation, that under this resident's current execution profile,
   diverting early-game unit-turns away from chopping toward planting/picking costs more in
   lost suppression/production tempo than it could conceivably recover even before asking
   whether the resulting plants are ever reaped.
4. Per protocol: no tuning of any threshold, condition, or scope attempted after any
   outcome was seen (the "bill-critical" operationalization and the endgame-reuse decision
   were both recorded in phase markers *before* the panel ran). Dev copy restored
   byte-exact (`fff6669b...`, re-verified twice); no candidate pair built (QUALIFIED-only
   step, not reached).
5. A successor attempt would need to pair a planting-priority fix of this kind with a
   working own-crop harvest-priority change (unlocking reaping specifically, not just
   planting) before this class of fix could plausibly clear its own mechanism bar — and,
   given the safety/value picture here, would additionally need to address the resident's
   suppression-efficiency gap (B4.4 §2/§5: 0.314 vs 0.427 wood/chop, 41.1% vs 46.6% opponent-
   crop contact coverage) before diverting further chop-turns away from it is affordable at
   all, consistent with B4.5's own explicit warning: "Copying [peers'] planting volume
   without first (or concurrently) closing that execution gap is close to exactly the
   scenario the safety gate exists to catch, for us specifically."

## Outputs

- `data/analysis/live-agent-6553250/d175a-bounded-early-planting-lock.json`
- `data/analysis/live-agent-6553250/d175a-bounded-early-planting-result.json`
- `data/analysis/live-agent-6553250/d175a-bounded-early-planting-result-2026-07-29.md` (this file)
- `data/analysis/live-agent-6553250/d175a-fix-as-tested.patch`
- `rust/src/bin/d175a_bounded_early_planting_panel.rs` (new panel runner)
- `cgauto/analyze_d175a_bounded_early_planting.py` (new analyzer)
- `artifacts/experiments/d175a-bounded-early-planting/` (2 TSVs + 2 trajectory NDJSON +
  `d175a-trigger-fidelity-check.json` + `.py`)
- `.superpowers/sdd/d175a-phase-markers.md` / `.superpowers/sdd/d175a-report.md`

No git add/commit performed. No docs/ or ledger files touched (ledger integration is the
controller's, per protocol). No arena or network access.
