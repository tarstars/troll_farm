# Session Handoff — 2026-07-16

This document supersedes `session-handoff-2026-07-11.md`. It records the recovery of the
actual live Legend bot and the repository-stabilization work required before another arena
experiment.

> **Current continuation — 2026-07-17:** the arena-validated resident remains slim agent
> `6557204`, source `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes.
> Phases 1--5 of `docs/hierarchical-controller-roadmap-2026-07-17.md` are complete.  The locally
> qualified next candidate is `candidate-agent6553250-compact-gold-rollout30.min.rs`, 90,643
> bytes; it has not been submitted and requires explicit arena authorization.

## Verified live state

- Player: `tass`
- Arena room: Legend rank 6/104, score 26.31
- Live agent: `6553250` (submission `40997200`)
- Live announcement: `yamo-carry-regen-transit-idle-harvest-rust`
- IDE source size: 90,133 bytes
- IDE source SHA-256: `09fac1fefa24eac657dba16a75d802eee38e1269f4aa44413e1ca103df36fe7a`
- The exact live source had no matching local `.rs` file at the start of this pass.
- The original contest ended on 2026-05-25; this is now practice-ladder work, with no contest
  deadline forcing a risky submission.

## Execution checklist

- [x] Recover the exact live source into an immutable agent-identified submission artifact.
- [x] Write and verify its checksum; compile both exact and formatted copies.
- [x] Make the recovered source the safe default for the submission helper.
- [x] Retire the completed Gold-rank recurring task so it cannot revive and submit stale code.
- [x] Preserve the expanded replay corpus without adding hundreds of megabytes to ordinary Git.
- [x] Fix replay collection ignore rules and document the 1,302-game corpus.
- [x] Preserve and test the explicit-agent replay collector changes.
- [x] Repair the obsolete Python-vs-current-Rust parity check.
- [x] Run the Rust, Python, and replay-QA validation suites.
- [x] Build a fixed top-five controlled-opponent panel.
- [x] Produce one isolated idle-harvest ablation from the recovered champion.
- [x] Run a throttle-safe A/B smoke panel and record whether a larger study is justified.
- [x] Decode the repeated loss signature against delineate, wala, and norxondor.
- [x] Screen the dormant sparse-farming loop and a work-conserving repair.
- [x] Add behavior-neutral wood-conversion telemetry and run a capped field sample.
- [x] Screen the global focus-bonus ablation locally and in a 12-game promotion panel.

## Current corpus and observed matchups

The processed corpus contains 1,302 games, 323 agents, 32 boss games, and no parse failures.
It includes all 161 collected games for live agent `6553250` (84 wins, 77 losses). The weakest
repeated matchups in that sample are:

| Opponent | Agent | Record |
|---|---:|---:|
| wala | 6481141 | 4-10 |
| delineate | 6479768 | 4-9 |
| norxondor_gorgonax | 6480540 | 4-9 |
| Konstant | 6479657 | 2-9 |
| laconic_pixel | 6482055 | 1-4 |

These records are diagnostic, not causal evidence. The next candidate must be compared against
the recovered champion on a fixed opponent panel before any ladder submission.

## Safety rules for this pass

1. Do not submit either baseline or candidate to the arena.
2. Keep the exact recovered source immutable; make experiments from the formatted copy.
3. Treat the failed paired self-play gate as parked infrastructure, not an arena predictor.
4. Keep external play bursts at or below 12 games; stop on HTTP 422 or degenerate results.
5. Do not delete or reset pre-existing worktree changes.

## Execution result

- Exact recovered artifact:
  `cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs`.
- Formatted development copy: `rust/src/bin/yamo_orchard_live.rs`.
- Safe submit default: the exact recovered artifact above; it was **not** invoked in this pass.
- Corpus integrity manifest: `data/processed/corpus_manifest.json`, aggregate SHA-256
  `fc230d5ea37df3540c3d85c602da680bbc2963105bb9f8abebfa58aea9f9684b`.
- Controlled smoke result: `data/panels/top5-idle-harvest-off-smoke.json`.
- Analysis and verdict: `data/analysis/live-agent-6553250/report.md`.

The panel completed ten controlled games without an HTTP or degenerate-game stop. Baseline went
2-3 and the candidate 1-4, but maps were random and unpaired. No baseline harvest occurred after
turn 250, and replay commands cannot distinguish the inner idle-harvest fallback from the outer
orchard wrapper's forced harvest. The candidate was therefore parked pending a causal study; a
larger generic panel was not justified.

## Follow-on idle-harvest verdict

An stderr-only diagnostic probe separated inner candidates/selections from outer orchard-forced
harvests and remained stdout-identical to the exact baseline on 300 fixed views.

- Identical-state divergence: live `HARVEST 0` versus ablation `WAIT` at turn 280; rolling
  forward scored 5-0 for the live fallback.
- Paired local mechanism study: 5/40 seeds activated; all five favored the live baseline, with
  mean paired margin +6.2 when activated (+0.775 across all seeds).
- Controlled platform telemetry: 0 inner selections in 10 top-five games; one game had 140
  independent orchard-forced harvests.

Decision: **REJECT `idle-harvest-off`; KEEP the recovered live baseline.** The inner fallback is
rare in the controlled sample, but every causal activated comparison was positive and none was
negative. This is not an arena-prediction claim and no submission was made. Details are in
`data/analysis/live-agent-6553250/report.md`.

## Repeated-loss follow-on

The 40 collected games against delineate, wala, and norxondor contain 28 losses. In 23/28 the
live bot leads wood at turn 100 and trails by turn 300; the mean wood gap moves +9.6 -> -6.3 ->
-28.4. Every loss opponent runs at least 20 successful plants and 20 harvested fruit. Live lands
more chops (138.3 versus 117.1) but converts them into much less wood (53.3 versus 81.2), for mean
per-game wood/chop 0.418 versus 0.773. Reproducible analysis:
`data/analysis/live-agent-6553250/matchup-loss-analysis.json`.

Two exact sparse-farming candidates tested the dormant renewable mother/crop loop. The isolated
loop lost all 17 activated paired-local seeds (mean -47.5 margin, -11.9 wood). A work-conserving
repair removed an empty-candidate bug but still went 1-16 (-32.5, -8.1 wood); all 43 inactive
dense-map seeds remained exactly neutral. These are self-harm/mechanism checks, not arena
predictions. They directly worsened wood, so neither was escalated to controlled platform games
or submitted.

## Wood-conversion and focus follow-on

The behavior-neutral wood probe remained stdout-identical to the exact live source and recorded
1,744 chop actions in ten controlled top-five games. Live realized 428 wood (0.245/chop).
Banana was the best raw target at 0.398 wood/chop; apple was worst at 0.145. Of 429 nominal wood
not collected on partial fells, only 10 units were plausibly recoverable by banking first; 408
were capacity-bound even with an empty carry. Do not build an early-bank detour.

The largest conversion split is workforce quality: the chop-1/carry-1 starter produced 114 wood
from 845 chops (0.135/chop), while trained trolls produced 314 from 899 (0.349/chop). Extra-troll
policies remain historically dangerous, so the first target-choice experiment removed only the
global lemon/plum denial bonus. Its 60-seed local screen was neutral (-0.19 paired margin,
-0.07 wood), but its final controlled promotion panel failed:

| bot | record | mean margin | mean wood |
|---|---:|---:|---:|
| exact baseline | 3-3 | +11.5 | 51.8 |
| focus-bonus-off | 0-6 | -150.7 | 39.7 |

Decision: **REJECT `focus-bonus-off`; KEEP the exact live baseline and full denial bonus.** The
platform games are unpaired random maps, so the numbers are a conservative promotion result,
not a causal arena estimate. The contradictory 5-5 diagnostic batch is retained rather than
silently discarded; it is exactly why the standard-source confirmation panel was required.

The unit-specific isolation was completed immediately afterward. Exact candidate
`candidate-agent6553250-focus-bonus-capable-only.min.rs` retains focus denial when chop or carry
exceeds one and removes it for chop-1/carry-1 workers. Its eight-worker, 60-seed paired-local
gate was negative: -1.21 mean margin, -0.31 wood, 13W/18T/29L (approximate 95% margin interval
-2.40 to -0.02). Almost the entire score delta is four times the wood delta. **REJECT; no
platform games.**

Focus-weight edits are now closed. Next use the historical corpus read-only to measure actual
train turn/spec and subsequent work share before constructing any training-policy candidate.

## Ten training-policy ideas

The next ten isolated ideas were tested without pausing: preferred/max carry, preferred/max
chop, strict carry-2, extra ETA 8/25, hard deadline 25/45, and movement tie-breaking. All used
the same 60 paired seeds with `--jobs 8`. The two positive Stage-1 means received 200-seed
confirmation:

- `train-extra-eta8`: +1.125 at n=60 -> -0.480 at n=200, wood -0.125; reject.
- `train-cap-chop2`: +1.025 at n=200, but 35W/112T/53L, wood -0.040, approximate 95% interval
  [-1.73,+3.78], 5%-trimmed mean -0.703; two outliers create the positive mean; reject.

The other eight were negative or inert. No idea qualified for a controlled field panel; no
platform games or arena submissions occurred. Preserve the exact live `TUNED_CARRY` policy and
close isolated training-constant tuning. Full result:
`data/analysis/live-agent-6553250/training-policy-sweep.md`.

## Renewable-supply follow-on

Exact live self-play confirms the mechanism: mean shared trees fall 16.23 -> 1.55 -> 0.48 ->
0.18 at turns 1/100/150/200. Median first exhaustion is turn 81.5. Live still has fruit on
86/116 exhausted sides and already plants 12.89 trees/game, so stored-fruit timing is not the
main deficit.

Six true-renewal mother/crop variants all lost wood. Broad late loop: -11.77 margin/-2.89 wood.
Best selective version (banana-only, release after first crop, liquidate mother first): -1.27
margin/-0.32 wood, 6W/40T/14L. A one-tree overlap remained negative. The separate timing-only
pre-seed confirmed at n=200 as neutral: +0.06 margin/+0.02 wood, 21W/158T/21L, unchanged total
PICK/PLANT.

No platform games or arena submissions. Renewable supply needs an exclusive mechanism; merely
growing a mature shared mother lets action cost/opponent capture exceed private crop value. Full
result: `data/analysis/live-agent-6553250/renewable-supply-study.md`.

## Corrected terminal iteration (supersedes the fixed-300 pre-seed verdict)

The active local evaluators previously forced games through turn 300.  Rust and Python now use
the referee's persistent no-tree grace, resource-stuck, and mercy rules.  Under those rules,
58/60 exact-live self-play matches end by stall at median turn 129.

The same low-supply pre-seed branch is positive over seeds 0..999: **+0.259 paired margin**,
**+0.115 wood**, 221W/655T/124L, with normal-approximation 95% margin interval
[+0.137,+0.381].  It is byte-identical to baseline in 200/200 games through turn 99.  In the
19 historical close-game streams that reproduce all recorded baseline commands, it activates
in 14 (7 losses, 7 matched wins), and all 14 first divergences satisfy the intended condition.

Verdict: the candidate now qualifies for controlled field evidence, but no platform game or
submission was authorized or performed.  Live agent `6553250` remains exact.  Full execution
record: `docs/improvement-roadmap-2026-07-16.md`; iteration report:
`data/analysis/live-agent-6553250/terminal-iteration-2026-07-16.md`.  That iteration's proposed
completion-race follow-on has now been executed and is superseded by the completed sweep below.

Final validation is clean:

- Python: 195 tests passed.
- Rust: all tests passed (with the repository's existing ignored tests and warnings).
- Replay QA: 1,302 checked, 1,295 exact scores, 7 penalty-only outcomes, 0 unexpected
  mismatches, 0 tree invariant violations, and 1,302/1,302 point-symmetric layouts.

## Completed ten-direction execution

The full roadmap sweep is now complete.  Static completion-race filtering was inert or harmful;
dynamic training denial was one-outlier driven; a greedy assignment ablation lost -6.48 margin;
the three-worker harvest-hand sequence lost all 60 seeds; removing the live score-aware endgame
switch was negative; only two unique harvest/bank/fell episodes existed; and the motion audit
found zero target-landing, teammate-block, or door-stall failures across 34,427 moves.  These
directions are parked, rejected, or retained as valuable baseline behavior as recorded in
`data/analysis/live-agent-6553250/direction-execution-2026-07-16.md`.

Broader safe secure-orchard geometry is the second local pass.  Over seeds 0..999 it changes
commands on 27 seeds and scores +3.7625 mean margin / +0.4525 wood, 26W/973T/1L.  This is rare
and heavy-tailed (range -0.5 to +276.5), so the sign pattern and wood gain matter more than the
mean magnitude.

The final local stack is
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs` (90,547 B, SHA-256
`da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`).  Corrected-semantic
n=1,000: **+4.025 margin, +0.5715 wood, 244W/632T/124L**, SD 26.135, SE 0.826, normal 95%
interval [+2.405,+5.645], 5%-trimmed mean +0.313.  Isolated effects are exactly additive in
both margin and wood on 996/1,000 seeds; average interaction is +0.0035/+0.004.

Probe/non-probe equality is exact in 200/200 games, and the stack equals its geometry parent in
200/200 games through turn 99.  Artifacts compile, checksums pass, and the full Python and Rust
regression suites pass.  No controlled platform game or submission occurred.  The next move,
only if explicitly authorized, is a small activation-instrumented controlled panel for the
stack; live agent `6553250` remains exact.

## Arena follow-on: invalid window, stack rolled back, exact live restored

The user subsequently authorized the arena trial.  Bracket at 16:57:35 MSK: exact live agent
`6553250`, rank 6/104 Legend, score 26.3.  Candidate submit `41002151` landed as agent `6555355`.
It climbed to a transient peak of rank 11 at 25.3, then reversed; the required +20-minute read
was rank 34 at 23.3, a -3.0 delta versus the established bracket.  The standing -0.5 rule
triggered a conservative rollback.

The comparison is **ARENA INCONCLUSIVE**, not a causal rejection.  Exact source
`cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs` was restored immediately with submit
`41002271`, landing as agent `6555394`.  `api_submit.py` still defaults to that exact source.
The same checksum then reached only 16.1 at restore +20 minutes and 19.9 at +35 versus its prior
26.3, while matchmaking arrived in uneven waves and one read failed.  This failed same-code A/A
control shows the platform was not operating at enough capacity/stability for the comparison.
Keep exact live resident, pause new arena writes, and retry only after normal same-code
reconvergence.  Detailed trajectory:
`data/analysis/live-agent-6553250/arena-verdict-2026-07-16.md`.

## Alternative-architecture pivot: one research candidate, no promotion

The simulator now has turn-by-turn material conformance against 361,752 replay transitions:
333,336 exact, 28,416 position-only referee-RNG differences, and zero material mismatches.  Tree
health/growth, compact chop diffs, same-turn chop/plant ordering, and simultaneous plant
collisions were corrected before rerunning architectural comparisons.

A four-policy, six-opponent league (60 maps, both seats, eight workers) finds the composed stack
best on raw average (+2.069 seed-balanced mean / +0.276 trimmed), but its interval crosses zero,
worst decile is negative, and motion-opponent mean is -0.092.  Even-seed fitting selects stack
only when initial banana fruit is <=5 and live otherwise.  Its odd holdout is +4.350/+1.354
trimmed analytically; the deployable one-source implementation produces +3.686/+0.821 on the
fresh odd-split run.  Both intervals and worst deciles remain negative.

Candidate `candidate-agent6553250-banana5-stack-portfolio.min.rs` is 91,101 bytes with SHA-256
`96ef33e77c10281510f0f3ee5ceef912bb6cf27e3b463276b8257aa6e9a234db`.  It exactly reproduces
its selected complete-policy branch in 300/300 deterministic cells.  The historical motion bot
is not an exact repeat-run oracle because its Rust hash collections are process-randomized.  The
maximin fit selects 100% live, so the portfolio is **research-only, not promotion-ready**.

The top-player macro branch is closed.  A corrected funded three-worker sequence activates in
359/360 paired cells (fully in 356) and loses -28.349 mean / -27.364 trimmed, with negative means
against all six opponents.  Exact live stays resident; no arena write occurred.  Full synthesis:
`data/analysis/live-agent-6553250/alternative-approaches-execution-2026-07-16.md`.
Final validation: 230 Python tests and the full Rust suite pass; candidate checksums, JSON parsing,
and whitespace validation are clean.

## Portfolio prospective follow-on: no promotion candidate

The stack portfolio completed a locked 300-seed deterministic gate on seeds 10,000..10,299. It
passed every research rule (+1.934 mean / +0.492 trimmed, interval lower +0.497, 96/40/72 W/T/L,
all five opponent means positive, and 460/460 exact high-branch cells) but failed promotion with a
-4.952 worst decile. Five-repeat randomized `motion` evaluation found no support: low -0.070,
high exact-live null -0.030, adjusted -0.039 with interval [-2.343,+2.265].

The complete component matrix made the next edit causal: all 21 deterministic tail losses equal
the pre-seed component exactly, while secure orchard is 11/197/0 and +1.753 mean. The packaged
stack matched its parent in 1,040/1,040 prospective cells. Pre-seeding was removed and artifact
`candidate-agent6553250-banana5-geometry-portfolio.min.rs` was frozen at SHA-256
`781f35a07cd31f5b344381c0d7e1174f0e655e8076bb3084a4d5b115b5879afe`.

On further-new seeds 10,300..10,599 the geometry portfolio was 5/204/0, +1.474 mean, interval
[+0.103,+2.846], worst decile 0, with positive means against every opponent and 1,500/1,500 exact
branch-reference cells. It nevertheless **fails the frozen research gate**: only five seeds win,
so five-percent trimming removes every nonzero gain and gives exactly 0 instead of the required
positive value. Do not promote, run motion, or submit it. Exact live remains resident.

The evaluators now use 16 process workers because Python referee bytecode was GIL-bound under the
old thread pool. The next defensible research direction is to broaden exclusive secure-orchard
activation and validate one frozen mechanism on seeds beginning at 10,600—not to refit another
selector on the two consumed blocks. Full report:
`data/analysis/live-agent-6553250/portfolio-prospective-execution-2026-07-16.md`.

Prospective-follow-on validation is clean: 246 Python tests and the full Rust suite pass, both
portfolio checksums verify, all result JSON parses, and `git diff --check` reports no errors.

## 2026-07-17 arena retry: stack promoted

Arena capacity recovered.  Exact-source A/A submission `41004754` landed as agent `6556775`,
received 67 battles, and reconverged to the 21.1 pre-reset score with a 20.8 confirmation.
Frozen stack submission `41004799` landed as agent `6556873` and later held rank 23/104 Legend
at 24.1 on two reads after 161 listed battles.  Delta versus the fresh control is +3.0 to +3.3,
so the stack is **PROMOTED**.  It remains live; `cgauto/api_submit.py` now defaults to the exact
90,547-byte submitted artifact.  The mandatory intermediate reads were missed, so the report
uses the actual late read rather than inventing a +20/+35/+50 trajectory.  Details:
`data/analysis/live-agent-6553250/arena-retry-2026-07-17.md`.
The closing read reached rank 20/104 @24.4.

## 2026-07-17 live-source slimming and arena A/A

The recovered source was compacted but not tree-shaken.  A locked pruning tool now removes
compiler-proven dead helpers, fixed-off sparse/tree-target experiment families, and the never-
constructed standalone Moisan policy.  Exact live shrinks 90,133 -> 62,311 bytes; the promoted
stack shrinks 90,547 -> 62,725 bytes.  Both compile with `-D warnings`, have checksum sidecars,
and reproduce their parents byte-for-byte over fresh dynamic both-seat games and all 26
historical streams.  They were not submitted; the recovery default remains the exact measured
90,547-byte artifact during local validation.

The promoted-stack slim form was then submitted explicitly as `41005161`, agent `6557204`,
against a fresh full-size bracket of rank 21/104 @24.5.  It read 23.3 at both +20 and +35, then
converged to rank 24/104 @24.2 at +50 and held that score through six consecutive closing reads;
160 battles were finished by +52.  Delta -0.3 is inside the frozen noise band, so the packaging
A/A **passes** and `cgauto/api_submit.py` now defaults to the 62,725-byte slim artifact.  The
extra 37,275 bytes of headroom make a compact promoted-policy residual layer plausible, but the
existing GoldElite-based residual is not deployable as-is.

## 2026-07-17 compact workforce residual: rejected before holdout

The first slim-baseline strategy iteration isolated an untested question from the earlier failed
macro variants: can the exact promoted two-worker policy add a third worker without changing its
opening?  It cannot.  Across 400 telemetry sides, normal play never afforded even `(1,1,0,1)`;
median best PLUM/LEMON/APPLE/IRON deficit was `3/3/0/3`.  Surplus candidates were inert on 200
seeds.  Starter-funded candidates never issued a third TRAIN and measured -2.225 margin for the
unbounded 2/2/0/2 branch and -0.358 for a turn-25-bounded 1/1/0/1 kill test.

Reject workforce expansion without consuming the untouched seed block or arena slot.  Keep slim
agent `6557204` and its submit default unchanged.  The next architecture target is a TRAIN-free,
stall-bounded renewal residual around the actual promoted policy.  Details:
`data/analysis/live-agent-6553250/compact-workforce-iteration-2026-07-17.md`.

## 2026-07-17 hierarchical controller decision

The workforce conclusion above is now narrowed to its tested counterfactual: a third worker
cannot be added passively or through the two tested starter-funding detours after the promoted
opening.  It is not a global rejection of worker-rich play.  The earlier funded macro experiment
reached worker three in 356/360 paired cells and then lost decisively, proving that affordability
and profitable architecture are separate questions.

Strong-agent evidence makes the coupling visible.  The top-five cohort averages 1.915 successful
trains, first train at median turn 2, about 35 plants, and 75.1 final wood; the recovered live
cohort has exactly one train, first at median turn 8, about 11 plants, and 48.2 final wood.  The
cohort is heterogeneous, including a successful two-worker agent, so no fixed worker count is the
new target.

The active roadmap is now:

1. extend the top-player census with turn-one conditions, funding trajectories, planting/supply,
   and post-train lifetime work;
2. reconstruct at most two coherent non-control opening options;
3. evaluate complete options on paired maps and fit a conservative turn-one selector;
4. compare that selector with an offline option-level Monte Carlo oracle;
5. choose a deployment architecture by robust value per byte;
6. retain the promoted policy as exact fallback and perform no arena write without explicit
   authorization.

Full architecture, statistical protocol, phase gates, and kill rules:
`docs/hierarchical-controller-roadmap-2026-07-17.md`.

## 2026-07-17 conditional opening archaeology: Phase 1 passed

The event-aligned replay analyzer now covers 427 unique games and 618 selected top/live
occurrences.  All decoded turn counts match, with zero unknown replay updates.  It records exact
turn-one conditions, every successful train and full funding deficit trajectory, contributing
worker actions, phased planting, lifetime worker output/cargo/inactivity, observed whole-bank
recovery, and per-agent conditional summaries.

Two coherent non-control options are nominated.  Rank-2 `wala` uses a turn-one farmer rule that
matches 29/29 appearances, creates PLUM/LEMON/APPLE supply with two farming hands, adds a
`2/2/0/2`-family chopper around turn 68, and conditionally adds another around turn 108.  Rank-1
`delineate` uses a max-bank hybrid first spec in 22/26 appearances and expands mainly on fast,
near-tree openings after the starter and hybrid actively replenish complementary resources.

The strongest Monte Carlo implication is horizon length: `wala`'s foundational farmer remains
below the pre-train bank through +50 turns and recovers at median +68.  Primitive or short-horizon
search would reject the architecture mechanically.  The next step is Phase 2 on reused discovery
seeds: implement the complete farm-first option outside live first, then the adaptive hybrid
option, with explicit stage/funding/supply/handoff telemetry.  Do not fit a selector, open a new
holdout, deploy live search, or write to the arena yet.  Full report:
`data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`.

## 2026-07-17 complete macro options: Phase 2 passed narrowly

Both replay-derived architectures were implemented outside the arena resident and evaluated on
reused discovery seeds with stage, funding, supply ownership, worker-effect, handoff, and outcome
telemetry.  Farm-first orchard scale is rejected: versus the promoted stack it loses -97.57
score and -27.46 wood across deterministic cells.  Its created supply was overwhelmingly private,
so the failure is funding and displaced work rather than opponent capture.  Explicit later
funding for the adaptive option is also rejected at -56.78 score.

The surviving mechanism is much smaller than the top-bot reconstruction.  If maximum-affordable
turn-one stats are `1/2/2/*` while promoted Yamo would wait for `1/3/0/*`, train an immediate
`1/2/0/chop-max` worker and then use normal Yamo control.  On the 60-seed discovery registry it
selects two maps, wins all ten selected deterministic-opponent cells, and is command-identical on
the other 116/120 seed/seat streams.  Its 63,561-byte slim form is behavior-identical to its full
reference in 120/120 dynamic streams.  This rule was derived on the same block and is not holdout
evidence.

That Phase-2 next step is now complete and superseded by the Phase 3--5 result below.  Full
Phase-2 report:
`data/analysis/live-agent-6553250/phase2-macro-option-study-2026-07-17.md`.

## 2026-07-17 direct rollout controller: Phases 3--5 passed

The global harvest-0 max-bank option loses -9.57 mean margin on the independent block, but the
per-seat hindsight oracle is positive.  Four-continuation ensemble selection retained too many
losses, and a blocked static-tree distillation missed all four held-out direct-rollout
activations while adding two false positives.  Do not reopen the static feature tree.

The frozen surviving rule runs promoted Yamo control and the complete option to the exact
terminal/stall horizon against CompactGold, then selects the option only when its predicted
margin advantage is greater than 30.  On seeds 120--179 it selected four of 120 seat cells and
scored +2.717 seed-balanced margin, 3W/56T/1L, minimum -2.6, with worst opponent mean +1.375.
This passed the protocol frozen before the block; the interval crosses zero because selection is
sparse, so it remains a local qualification rather than an arena claim.

The standalone candidate is 90,643 bytes with SHA-256
`f5df1f760791a21ad0193469c132fea02ebaa2856b33f62213765205b3b59370`.  Two scoped first-turn
workers run control and option concurrently.  A 700 ms shared deadline or worker failure falls
back to exact control, and later turns have no rollout cost.  Release validation matched 120/120
frozen decisions and 10/10 full dynamic streams; first-turn p95 was 184.07 ms and maximum 193.96
ms locally.  The resident and `cgauto/api_submit.py` were not changed.

Next: stop tuning consumed local blocks.  Only an explicitly authorized controlled platform
capacity bracket and candidate trial can test transfer.  Full report:
`data/analysis/live-agent-6553250/phase3-phase5-rollout-study-2026-07-17.md`.

## 2026-07-18 controlled rollout arena: rejected and resident restored

The authorized live sequence is complete.  Same-source control submission `41009795`, agent
`6559490`, passed capacity: 125 games @23.6 and 142 @24.1 on reads 5:04 apart, versus 24.4 before
reset.  Frozen rollout submission `41009911`, agent `6559513`, rose to 23.1 early but decayed to
21.7 at 120 games.  The final audit fetched 123/123 results; all were valid and no timeout/runtime
marker appeared.  This is a clear reject versus the 24.1 control and 25.1 promotion bar.

The exact 62,725-byte resident was restored as submission `41009991`; agent `6559583` replaced
the candidate at 10:40:33 MSK.  `cgauto/api_submit.py` was not edited during the protocol and
still defaults to that resident.

Forensics on two preserved recent-30 windows reproduced 60/60 official first commands.  The
option activated three times and lost all three (-26, -18, -27).  Its Gold/Compact predictions
were +197, +38, and +176, yet every selected map had a negative alternative continuation; two
were negative under all three other models.  CompactGold and GoldElite were exact in 120/120
reconstructed seat cells.  This closes the exact max-bank option plus single-CompactGold selector.

Phase 7 is complete and rejected.  Exact resident plus dynamic max-bank plus all 27 fixed
harvest-0 first workers were evaluated against eight heterogeneous continuations.  The strict
expanded selector was inert; relaxed rules failed held-model checks.  A repeat audit kept
9,280/9,280 opening actions exact but found five process-sensitive models, and six independent
process realizations still yielded zero opponent-robust selections.  A pooled diagnostic's two
choices caused 48 held model-seed losses.  No holdout was opened and no candidate was packaged.

Phase 8's first discriminator is also complete.  Arena opponents train immediately in 22/60
diagnosis games with 11 specs; seven local models never train in those states, while BossReal
matches none of the actual specs.  Adaptive Gold has the best exact full opening agreement at
only 8/60.  No model matches the first target of any failed rollout activation, and all miss the
third opponent's `PICK`.  Weighting the current zoo is unsupported and a turn-one controller
cannot condition on the simultaneous opponent command, so no weighted rerun follows.

Next work is offline Phase 9: extract high-level per-worker objectives and role transitions from
top-agent replays, validate them by held game and held agent, and build a complete research
continuation only if that imitation layer generalizes.  First-move Monte Carlo for the isolated
worker library is closed.  The map holdout stays sealed and no further arena write is authorized.
Full reports:
`data/analysis/live-agent-6553250/robust-first-option-discovery-2026-07-18.md` and
`data/analysis/live-agent-6553250/arena-opponent-opening-calibration-known60-2026-07-18.md`.

Phase 9's first discriminator is complete.  A 91,427-row state-only objective model fails when
the top five are pooled (59.886% held-game accuracy, 39.132% worst held-agent), but Escdemon's
compact policy passes its own held-game gate strongly: 77.682% accuracy, 0.541 macro F1, and
74.760% worst fold.  Norxondor is the secondary target.  Escdemon uses max-affordable harvest-0
at its actual train turn in 26/26 games, while the resident planner already predicts 14/26 exact
eventual specs.  This rules out another worker-stat iteration.

Immediate next work: learn Escdemon's TRAIN trigger, exact target coordinates, and multi-worker
assignment under held-game validation; only then consider a complete research policy.  The
resident, unopened map block, submit default, and arena remain unchanged.  Phase-9 report:
`data/analysis/live-agent-6553250/top-policy-objective-study-2026-07-18.md`.

Phase 9's complete Escdemon gate is now closed. First-affordability timing is exact in 25/26
games and the second worker is a pure wood converter, but the eventual spec cannot be selected
out of sample (8/26 nested leave-one-game-out versus 14/26 for the pre-existing resident plan).
The held-game tree ranker passes conditionally at 56.08%, then fails after autoregressive
integration at 52.12% MOVE accuracy / 46.92% worst fold. All 12 existing local policy skeletons
fail the shortcut gate. Do not build an Escdemon candidate or tune its remaining 270 waypoint
moves.

Immediate next work is Phase 10: model Norxondor's 0–4 worker controller jointly—planned worker
count, staged TRAIN triggers/spec families, stable roles, and utilization—under held-game gates.
The resident, submit default, sealed map block, and arena remain unchanged. Full evidence:
`data/analysis/live-agent-6553250/escdemon-complete-policy-gate-2026-07-18.md`.

Phase 10 is complete. Norxondor's four-stage max-affordable workforce ladder reproduces all
8,738 observed trigger decisions and 62/62 TRAIN specs; held-game spec accuracy is 57/62. The
missing affordability mechanism is a temporary two-worker funding coalition. A frozen
three-worker plateau is the strongest macro option, but its opponent-specific regressions prevent
direct promotion.

A confidence-buffered resident/three-worker opponent-label portfolio passed new generated seeds
210--239 at +6.213 mean margin with no negative opponent mean. Opponent identity is unavailable,
so this is only an information ceiling. A conservative observable TRAIN signature also passed its
offline gate, but the actual resident-prefix switch failed prospectively on seeds 270--299 at
-6.169 margin / -5.048 score and only 46/480 three-worker outcomes. The prefix changes the funding
path and opponent response; do not tune signature thresholds or build a candidate.

Immediate next work is Phase 11: freeze exact resident and exact-three-worker branches, capture
one shared early state, condition the opponent ambiguity set on observable transitions, and use a
one-shot repayment-length Monte Carlo comparison of both complete macro options. Validate the
actual integrated selector, then profile the 50 ms and 100 kB constraints. The resident, submit
default, sealed map block, and arena remain unchanged. Full evidence:
`data/analysis/live-agent-6553250/norxondor-controller-iteration-2026-07-18.md`.

Phase 11 is complete. The turn-three shared-state terminal teacher passed discovery and unchanged
validation at +26.081 mean margin / +15.194 score, positive means against all eight opponents,
and no selected losing cell. Its first useful approximation appears only at 240 turns. That proxy
retains 89.19% of teacher margin but validates at 88.33% precision, below the frozen 90% safety
bar. Running both branches and compatible models concurrently still takes 209.487 ms median /
279.460 ms p95; 0/80 profiled decisions fit 50 ms. Compact tree, deployable forest, and raw
signature distillation also fail their frozen gates.

Direct online Monte Carlo is closed. Immediate next work is Phase 12: generate many exact
resident-versus-worker-three outcomes offline, encode generic observable turn-one-to-turn-three
trajectory features, and fit a precision-first compact value classifier under blocked-seed and
leave-one-opponent-out gates. The expression must be frozen before any new validation block. The
62,725-byte resident, submit default, sealed holdout, and arena remain unchanged. Full evidence:
`data/analysis/live-agent-6553250/norxondor-shared-state-monte-carlo-2026-07-18.md`.

Phases 12--14 are complete and rejected. Generic turn-3/5/10 trajectory models produce positive
blocked-seed policies, but none passes the leave-one-opponent-family-out precision gate; turn 10
falls from 91.43% blocked-seed precision to 73.08% opponent-family precision. Post-funding role
and funding-profile factorials produce 0/26 and 0/20 robust policies. Compact Norxondor intent and
goal components pass held-game/size gates, but the joined native controller suffers closed-loop
state-distribution drift and loses -172.663 paired margin / -97.263 score after bounded repairs.

The one unresolved signal is opponent-robust map geometry. Its lower-quartile oracle selects
19/160 seed-seat groups at 90.789% expanded precision, +7.697 margin, +6.532 score, and positive
means against all eight opponents, but the small-sample forest fails. Phase 15 predeclares seeds
1000--1299 as discovery/training only for a 600-group replication. Seeds 402--999 and the sealed
official-map holdout stay unopened; no candidate or arena action is authorized. Full report:
`data/analysis/live-agent-6553250/norxondor-offline-distillation-and-native-controller-2026-07-18.md`.

Phase 15 is complete and rejected. The exact 4,800-cell / 600-group expansion contains 65 robust
positive groups. The oracle still gains +4.591 margin / +3.993 score with all opponent means
positive, but its 89.615% expanded precision misses the frozen 90% bar. All ten fixed map-only
forests fail; the best has 47.059% actual precision and -0.277 margin. Close this representation
without grid expansion, pooling/tuning, validation, candidate construction, or holdout use. The
next mechanism must preserve the resident trajectory and train on its own visited states rather
than transplant a complete foreign economy.

Phase 16 tested that remaining idea directly. A research residual wrapped the exact Yamo/Orchard
resident, changed only MOVE targets, preserved direct work and TRAIN, and used the prior fixed
4/16-turn, two-model, eight-turn-commitment profile. On consumed seeds 0--4 it gained +1.200
margin / +0.913 score with all opponent margin means nonnegative, but p95 was 130.047 ms and both
effect gates failed. A behavior-neutral event audit found shack redirects were the only coherent
positive class. Their fixed replication on consumed seeds 5--19 activated 103 times but gained
only +0.508 margin / +0.554 score, had ScriptBoss at -0.300, and ran at 92.852 ms p95 / 229.508 ms
maximum. Close resident residual search without distillation or tuning. Full report:
`data/analysis/live-agent-6553250/resident-residual-search-2026-07-18.md`.
