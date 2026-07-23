# Ten-direction execution report — 2026-07-16

## Outcome

All ten attack angles in the improvement roadmap were instrumented or tested.  Two narrowly
scoped mechanisms survive the local evidence ladder:

1. low-supply pre-seeding, which advances an ordinary seed pickup after turn 100; and
2. broader secure-orchard geometry, which admits the existing exclusive orchard on a larger but
   still enemy-distant set of maps.

The composed artifact is
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs` (90,547 bytes,
SHA-256 `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`).  Over 1,000 paired
seeds with corrected referee semantics it gains **+4.025 mean margin** and **+0.5715 wood**, with
244 wins / 632 ties / 124 losses.  Its paired-margin SD is 26.135, SE is 0.826, and the
normal-approximation 95% interval is **[+2.405, +5.645]**.  The 5%-trimmed mean remains positive
at +0.313.

This is a local self-harm gate, not an arena estimate.  A subsequent user-authorized arena test
was inconclusive: the stack read 23.3 at +20 minutes versus an established 26.3 bracket, but the
byte-identical restored baseline reached only 16.1 at its own +20 read and 19.9 at +35.  Exact
live was restored conservatively; platform capacity/reset variance invalidated the comparison.

## Arena follow-on

Candidate submit `41002151` landed as agent `6555355`.  It rose from cold start to a transient
peak of rank 11/104 at 25.3, then read rank 34/104 at 23.3 by +20 minutes.  The standing rule
triggered rollback via submit `41002271`, which landed exact source as agent `6555394`.  That
same-code control was only 16.1 at +20 and 19.9 at +35, making the candidate comparison invalid.
The stack is neither promoted nor causally rejected.  Full record: `arena-verdict-2026-07-16.md`.

## Analysis by level of abstraction

| Level | What the evidence says | Consequence |
|---|---|---|
| Referee / outcome | Most exact-live local games end by the persistent stall rule, not turn 300 | Timing candidates must use real grace, stuck-resource, and mercy semantics |
| Economy | The repeated loss is low private wood conversion, not insufficient chop volume | Prefer exclusive value and efficient worker allocation over generic activity |
| Strategy | Shared renewable supply is recaptured by the opponent; exclusive orchard supply can compound privately | Expand only proven defensible geometry; do not restore broad mother loops |
| Tactics | Small scheduling changes can help; static opponent ETA and raw inventory scarcity are too weak to drive target rejection | Keep pre-seeding, but park race/denial filters until their state model includes shared work and alternatives |
| Planner | The live exhaustive two-unit assignment and score-aware endgame already add value | Preserve both; do not replace them with greedy roles or score-blind behavior |
| Execution | Routing reaches every emitted target; no blocking/door-stall defect was observed | Do not spend the next iteration on pathfinding |
| Evidence | Rare geometry activation creates a heavy-tailed mean, while distributed pre-seeding supplies a smaller robust gain | Carry both forward, but require controlled activation telemetry before promotion |

## Execution matrix

| # | Direction | Discriminator executed | Result | Verdict |
|---:|---|---|---|---|
| 1 | Correct evaluator semantics | Port referee stall/grace/mercy behavior to Rust and Python; validate independently | 196/200 telemetry games end by stall; corrected 60-match baseline has 58 stall endings at median turn 129 | **Done; foundational** |
| 2 | Stall-aware terminal controller | Gate an ordinary low-supply seed pickup from turn 100 | n=1,000: +0.259 margin, +0.115 wood, 221/655/124; 95% interval [+0.137,+0.381] | **Local pass** |
| 3 | Opponent completion-race filter | Suppress the focus bonus, then reject the tree, when static opponent bank ETA wins | soft filter +0.005 on n=200 and only 7 active seeds; hard reject -0.1075 | **Park static ETA model** |
| 4 | Dynamic training-resource denial | Before opponent training, focus its scarcer plum/lemon resource | raw +0.935 on n=200, but SD 14.779, 95% interval [-1.113,+2.983], 5%-trimmed +0.003; one +206.5 outlier | **Reject candidate; retain telemetry** |
| 5 | Comparative-advantage joint assignment | Ablate exhaustive two-worker pairing to greedy assignment | -6.480 margin, -1.7525 wood, 39/23/138 on n=200 | **Keep live joint assignment** |
| 6 | Evidence-derived workforce sequence | Cheap harvest/seed hand, followed by dedicated wood worker | -67.908 margin, -15.800 wood, 0/0/60 | **Reject decisively** |
| 7 | Exclusive renewable geometry | First relax enemy-door distance only; then use the existing broader safe boundary | door-12 relaxation is inert; coverage branch is +3.7625 margin, +0.4525 wood, 26/973/1 on n=1,000 | **Local pass, heavy-tail caution** |
| 8 | Score-state asymmetric policy | Restrict pre-seed to behind states; separately remove the live behind/low-supply endgame switch | behind-only is 200/200 inert; score-blind ablation is -0.5775 and -0.2425 wood | **Keep existing asymmetry; no new branch** |
| 9 | Zero-commitment bundles | Price cashout/fell and harvest/bank/fell on 26 validated close-game fixtures | 40 feasible cashout/fell frames span 38 episodes and 23 immediately select DROP; 8 harvest frames collapse to only 2 episodes, one win and one loss | **Measured; no candidate justified** |
| 10 | Motion/interference audit | Audit 34,427 moves; test a small remembered-tree bonus | all targets reached; zero no-progress, duplicate landing, stationary-teammate target, or door stall; bonus +0.150 with interval crossing zero | **Keep routing; park bonus** |

## Why the two winners compose

The geometry branch changes commands on only 27/1,000 seeds.  Of those outcome changes, 26 are
favorable and one is a -0.5 loss.  Its mean (+3.7625) is heavy-tailed—the range is -0.5 to
+276.5 and the 1%-trimmed mean is +1.578—so its magnitude must not be read as a stable arena
effect.  Its sign pattern and positive wood delta are the stronger local evidence.

Pre-seeding is broader: it changes commands on 452/1,000 seeds, has range -12 to +15.5, and
retains a +0.209 5%-trimmed mean.  It therefore supplies the stack's distributed, lower-variance
component.

The stack changes commands on 473/1,000 seeds.  On 996 seeds its margin and wood deltas are
exactly the sum of the two isolated branches.  Mean interaction is only +0.0035 margin and
+0.004 wood, so there is no material destructive interaction hidden by the aggregate.

## Integrity gates

- The secure-orchard diagnostic probe and non-probe candidate emit identical command streams in
  200/200 games (100 seeds, both seats).
- The composed artifact and geometry-only parent emit identical command streams through turn 99,
  before the pre-seed gate can open.
- Both promoted artifacts reproduce deterministically from the immutable live source and their
  SHA-256 sidecars validate.
- Both compile standalone with `rustc --edition 2021` and remain below the 100 KB source limit.
- All 195 Python tests and the release Rust regression suite pass; existing Rust warnings and
  ignored tests are unchanged.

## Recommended next move

Retain the exact live artifact and pause arena writes until platform capacity normalizes.  If
the stack is revisited, first require a same-code reset control that reconverges, then isolate
pre-seed from orchard activation in a controlled field panel.

Machine-readable evidence:

- `preseed-orchard-coverage-stall-corrected-1000.json`;
- `secure-orchard-coverage-stall-corrected-1000.json`;
- `preseed-low-supply-stall-corrected-1000.json`;
- `training-denial-telemetry.json`;
- `motion-audit-telemetry.json`;
- `terminal-bundle-telemetry.json`;
- `terminal-race-telemetry-2026-07-16.json`.
