# Alternative-approaches execution — 2026-07-16

## Verdict

The pivot and its completed prospective follow-on produced one useful sparse mechanism and no
promotion candidate.

- Keep exact live resident.
- Archive the turn-one banana-5 stack/live portfolio after its deterministic research pass,
  promotion-tail failure, and motion non-generalization.
- Retain secure-orchard geometry as a mechanism to broaden, not as a submitted candidate.
- Reject both multi-worker macro transfers.
- Reject the learned maximin mixture: its optimum is exactly 100% live.
- Do not write to the arena while its same-code A/A control is degraded.

Deployable research artifact:
`cgauto/submissions/candidate-agent6553250-banana5-stack-portfolio.min.rs`, 91,101 bytes,
SHA-256 `96ef33e77c10281510f0f3ee5ceef912bb6cf27e3b463276b8257aa6e9a234db`.

## Analysis at multiple levels

| Level | Question | Evidence | Result |
|---|---|---|---|
| Mechanics | Does the local referee preserve official material state? | 361,752 comparable replay transitions | 92.145% exact, 7.855% position-only movement differences, 0 material mismatches |
| Tactical policy | Do complete variants beat live across behaviors? | Four policies × six opponents × 60 maps × both seats | Stack is best raw policy, but uncertainty and one weak opponent remain |
| Map-conditioned policy | Can turn-one information choose when risk is useful? | Even/odd seed stump split | Banana fruit ≤5 selects stack; otherwise live; positive holdout trimmed mean |
| Robust ecosystem | Is any fixed mixture safe against every opponent? | Train-split maximin payoff matrix | No; optimizer selects 100% live |
| Macro architecture | Do top-player worker roles transfer causally? | 618 replay appearances plus two complete macro candidates | No; activated three-worker transfer loses decisively |
| Position search | Can exact search certify critical endings? | 26 terminal fixtures / 416 positions | Sample proof works, but official fixture coverage is presently too small |

## 1. Referee and replay conformance

The simulator was repaired before using it as an architecture discriminator:

- planted tree health is species-specific: plum/lemon 4, apple 8, banana 2;
- growth adds the species health slope while preserving accumulated damage;
- compact replay diffs apply known CHOP commands before implicit growth;
- a same-turn plant cannot be hit by a CHOP aimed at a previously empty cell;
- same-type plant collisions merge and charge every planter; mixed types cancel and charge none;
- map generation now uses the same species-specific base health.

Final one-turn replay conformance covers 1,302 games and 361,752 comparable turns: 333,336 are
exact, 28,416 differ only in unit position from referee movement RNG, and none has a material
mismatch.  Three malformed historical command strings are excluded explicitly.  This makes the
corrected simulator credible for economy comparisons, while preserving an honest movement-RNG
limitation.

Artifact: `replay-conformance-2026-07-16.json`.

## 2. Diverse complete-policy league

Every cell uses a common generated map and both seats.  Deltas compare a policy with live on the
same map and opponent.  The run contains 360 paired cells per policy, or 720 games per policy.

| Policy | Seed-balanced mean | 5% trimmed | W/T/L seeds | Worst decile | Worst opponent mean | Decision |
|---|---:|---:|---:|---:|---:|---|
| live | 0.000 | 0.000 | 0/60/0 | 0.000 | 0.000 | control |
| pre-seed | -0.219 | -0.165 | 33/1/26 | -9.014 | -4.175 motion | reject globally |
| geometry | +1.588 | -0.062 | 27/7/26 | -7.792 | -0.192 motion | park |
| stack | +2.069 | +0.276 | 31/1/28 | -8.292 | -0.092 motion | retain for conditioning only |

The stack's cell-level interval is positive, but map seeds—not opponent cells—are the independent
unit.  Its seed-balanced interval is [-1.415,+5.554], and seed 31 contributes +98.333.  It is
therefore not a global winner.

Artifact: `offline-policy-league-2026-07-16.json`.

## 3. Cross-validated map portfolio

Only turn-one, seat-invariant features were eligible.  The stump was fit on 30 even seeds and
evaluated once on 30 odd seeds.  It selected:

```text
initial banana fruit total <= 5  -> complete stack
initial banana fruit total > 5   -> exact live
```

The analytical holdout is +4.350 mean and +1.354 5%-trimmed versus live, with 11/11/8 W/T/L.
It also beats the training-selected global policy in paired holdout comparisons (+4.889 mean,
+1.869 trimmed).  The result is still high variance: its 95% normal interval is
[-2.224,+10.924], worst decile is -3.917, and maximum is +98.333.  It passes a discovery gate,
not a promotion gate.

The selector was then packaged into one Rust source.  It reproduces all scores, wood, action
counts, opponent responses, and terminal turns of the selected branch in 300/300 deterministic
map-opponent cells.  The remaining historical `motion` opponent uses process-randomized Rust
`HashMap`/`HashSet` iteration, so separate processes are stochastic outcome samples rather than
an exact equivalence oracle.  In the deployable candidate's fresh run, the untouched odd split
is +3.686 mean / +0.821 trimmed, 17/1/12 W/T/L, interval [-2.975,+10.347], worst decile -9.028.
Overall it is +2.017 mean / +0.312 trimmed across 60 seeds.

Artifacts: `policy-portfolio-analysis-2026-07-16.json` and
`portfolio-candidate-study-2026-07-16.json`.

## 4. Minimax policy mixture

The four-policy payoff matrix was fitted on the even seeds with weights in 0.05 increments.
Because every non-live choice has a negative training payoff against at least one opponent, the
maximin solution is 100% live.  Its worst-opponent improvement is zero, not positive.  This is
the strongest reason not to promote the portfolio despite its positive average holdout.

## 5. Top-player archaeology and macro transfer

The census covers 618 selected-agent appearances.  Top-five agents average 1.915 successful
trains and first train at median turn 2; live always trains exactly once and first trains at
median turn 8.  Hybrid choppers occur in 52.7% of top-five appearances across four distinct
agents and never in live.  The role is a stable discriminator, but not yet causal evidence.

The first hybrid-opening candidate issued only the ordinary one train per game.  It validly
rejected replacing live's second worker with the expensive hybrid (-23.914 mean / -20.114
trimmed), but instrumentation showed that it did not test worker three.

The repaired candidate keeps both existing workers in explicit fruit/iron collection until the
third worker is affordable.  Activation is conclusive: 356/360 paired cells reach three workers
in both seat games, three cells in one game, and one cell in neither.  It then scores -28.349
mean / -27.364 trimmed versus live, with interval [-42.201,-14.496], 18/0/42 W/T/L, and negative
means against all six opponents.  Reject the role transplant.  Top bots' worker counts are part
of a coupled farming/planning architecture and cannot be copied as an isolated training sequence.

Artifacts: `top-player-macro-census-2026-07-16.json`,
`macro-architecture-study-2026-07-16.json`, and
`macro-architecture-funded-study-2026-07-16.json`.

## 6. Critical-state solver coverage

The existing oracle independently validates the sample forced win: CHOP, CHOP, MOVE, DROP for
a final score difference of +8.  None of 416 positions from 26 terminal fixtures fits the
documented one-unit-per-side envelope.  A relaxed probe admits 85 positions in 11 fixtures, but
the oracle omits TRAIN and uses deterministic movement ties.  It is useful for small etudes, not
yet a full official-game policy layer.

Artifact: `critical-state-coverage-2026-07-16.json`.

## Selection and next gate

The banana-5 portfolio is the only direction worth another offline iteration because it is the
only approach with positive mean and trimmed holdout evidence, a deployable implementation, and
exact deterministic branch equivalence.  Exact live remains both the resident and the robust
maximin choice.

Before any arena reconsideration:

1. Run at least 200 new, untouched seeds stratified by the banana-5 branch.
2. Repeat or replace the process-randomized motion opponent; require every deterministic opponent
   mean to remain non-negative.
3. Require positive mean and trimmed mean, and for promotion require a positive lower interval
   bound plus a non-negative worst decile.
4. Re-establish arena health with a same-code A/A reset that reconverges before any candidate
   write.

No arena submission or external write was made during this roadmap.

## Prospective follow-on

The requested larger validation is complete. On seeds 10,000..10,299, the stack portfolio passed
all six deterministic research checks (+1.934 mean, +0.492 trimmed, CI lower +0.497, and positive
means against all five opponents) but failed promotion with a -4.952 worst decile. A separately
frozen five-repeat `motion` study found no stochastic support: low mean -0.070 versus a -0.030
exact-live null, adjusted difference -0.039.

Component diagnosis then showed that all 21 bottom-decile losses came exactly from pre-seeding.
Secure orchard alone was 11/197/0 W/T/L across the activated seeds. A pre-seed-free geometry
portfolio was therefore frozen and run on further-new seeds 10,300..10,599. It was 5/204/0 with
+1.474 mean, positive CI lower bound, nonnegative worst decile, positive opponent means, and exact
branch references—but its five wins were all removed by five-percent trimming, producing the
predeclared disqualifying value 0. It is formally rejected; no motion or arena escalation follows.

Full prospective synthesis:
`data/analysis/live-agent-6553250/portfolio-prospective-execution-2026-07-16.md`.

## Validation

- Python: 230 tests passed.
- Rust: full `cargo test` passed, including the long oracle size-budget test; only the repository's
  existing ignored tests and warnings remain.
- Both new candidate checksums pass and both sources compile with optimized Rust.
- All result JSON parses and `git diff --check` is clean.
