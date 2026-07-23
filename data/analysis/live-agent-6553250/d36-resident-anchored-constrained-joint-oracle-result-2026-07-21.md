# D36 resident-anchored constrained joint oracle — result (2026-07-21)

## Verdict

**The resident-anchored overlay is causally useful but far too small; reject the architecture and
advance to a complete learned controller.**

Across all 128 exact official-map tasks, the repeated constrained oracle adds **+19.617 own score**
and **+10.633 margin** over uninterrupted resident control while allowing only +8.984 opponent
score. Repetition itself is real: relative to the paired constrained one-shot choice it adds
+8.953 own score and +5.836 margin. Nevertheless, the frozen upper-bound requirements were +68
own score and +25 margin. The representation passes ten of fifteen value gates and fails five.

The result is not an inactive-wrapper failure. A non-control bundle is selected in 112/128 tasks,
87 tasks execute at least two bundles, and 292 non-control epochs are executed. Rather, complete
two-worker bundles followed by return to the resident can improve local decisions without creating
the sustained production regime seen in strong policies. No threshold, target, objective, or
additional resident-overlay iteration is authorized.

Confirmation seeds 9,500,008--9,500,019 remain sealed. No policy was trained, no candidate was
built, and no TestSession, submission, resident, or Arena state changed.

## Integrity and support

- All 128 seed/seat/opponent tasks reach the exact first resident state with two workers at or
  after turn 50. The matrix contains 378 epochs and **17,963 terminal option rollouts**.
- Independent seed-9,500,000 repeats are byte-identical: rows
  `ce9efd9d451fff0720cd16776545deab3dc80b998856e02c45c23892d19f4742`, scenario manifests
  `26c35b8ff177590efb8f1f91f53932b1781a6c1733dce315d42d1526b9a57ab8`.
- Every resident root/control identity, catalog count, plan key, option selection, feasibility
  decision, execution prefix, completion boundary, epoch chain, terminal replay, final outcome,
  and stop reason passes the independent analyzer.
- There are zero attribution/history mismatches, collisions, illegal direct commands, TRAIN
  successes, branches above three own workers, duplicate options/keys, or recorded rollout errors.
- Four focused D36 Rust tests and five analyzer tests pass. The analyzer tests include deliberate
  constraint, replay, completion-boundary, and weak-value failures.

## Paired outcome

| Seed-clustered measure | Result | 95% normal seed interval |
|---|---:|---:|
| Own-score gain vs resident | **+19.617** | [+17.993,+21.242] |
| Opponent-score excess vs resident | +8.984 | [+5.475,+12.494] |
| Margin gain vs resident | **+10.633** | [+7.929,+13.337] |
| Own-score delta vs constrained one-shot | +8.953 | [+7.492,+10.414] |
| Opponent-score delta vs constrained one-shot | +3.117 | [+0.377,+5.857] |
| Margin delta vs constrained one-shot | +5.836 | [+2.675,+8.997] |
| First-root terminal-margin choice: own delta vs resident | +4.125 | [+1.124,+7.126] |
| First-root terminal-margin choice: opponent delta vs resident | **-9.016** | [-15.982,-2.049] |
| First-root terminal-margin choice: margin delta vs resident | +13.141 | [+8.901,+17.380] |

Every opponent-family own-score mean is positive, but the range is only +13.438 to +25.750; zero
families reach the frozen +50 floor. Family margin means range from exactly 0 against compact Gold
to +19.063 against Legend Balanced; only two of eight reach +15. Thus the aggregate misses are
broad architectural shortfalls, not one adversarial outlier.

Repeated control eliminates the one-shot catastrophe (1/128 to zero) and reduces one-shot
negative-margin mass from 678 to 484. It remains slightly worse than uninterrupted resident's 454,
so the strict tail gate fails by 30 points of mass.

## Frozen gates

Ten of fifteen gates pass: activation, repetition rate, opponent-score ceiling, repeated-vs-one-shot
own and margin value, nonnegative family means, provenance breadth, and catastrophe frequency.
Five fail:

| Failed gate | Result | Requirement |
|---|---:|---:|
| Own-score gain vs resident | **+19.617** | >=+68 |
| Margin gain vs resident | **+10.633** | >=+25 |
| Opponent families with own gain >=+50 | **0/8** | >=6/8 |
| Opponent families with margin gain >=+15 | **2/8** | >=6/8 |
| Repeated negative-margin mass | **484** | <=resident 454 and <=one-shot 678 |

The opponent ceiling itself is respected with 56 points of mean slack. Moreover, the separately
recorded first-root terminal-margin winner is feasible in all 128 tasks. The miss therefore cannot
be repaired by claiming the constraint destroys all useful interventions. Relaxing or retuning
the ceiling after observing the result is prohibited in any case.

## Analysis by abstraction level

### Causal mechanism

The validated D35 representation survives a resident anchor: joint persistent jobs, repeated
completion-boundary decisions, and provenance-specific targets still create positive terminal
value. Sixty of 292 selected epochs are provenance-specific, covering seven opponent families and
all four epochs. These are useful components, not a sufficient controller.

### Decision horizon

Only 16 tasks stop on control immediately; 25/36/9/42 tasks execute one/two/three/four bundles.
The selected epoch gains in own score remain positive throughout: +10.664, +5.536, +3.218, and
+4.824 relative to each epoch's control. Forty-two tasks hit the four-epoch cap. This does not
authorize a fifth overlay epoch: even four terminally selected interventions produce less than
one third of the preregistered own-score gain, and the protocol explicitly closes overlay depth on
failure.

### Objective and constraint

At the first root, selecting terminal margin instead of feasible maximum own score trades roughly
6.5 own points for about 14.9 opponent points. That option is feasible in every task and yields
+13.141 margin but only +4.125 own score. The experiment therefore exposes a real production /
suppression frontier, yet neither end supplies a complete economy. Post-result scalarization is
not the missing architecture.

### Controller architecture

The resident remains responsible for the opening, training, global reservations, and every command
outside short completed bundles. The D36 catalog has no TRAIN action. Consequently the overlay can
exploit local production opportunities while repeatedly collapsing back to the same suppressive
two-worker scheduler. Strong-policy scale requires one coherent policy to own crop creation,
funding, workforce growth, production, and rival-loop denial over the full trajectory.

### Learning and transfer

D36 is a hindsight upper bound with exact terminal opponent continuation. It cannot be deployed,
and it fails its local development gate. Distilling D36 labels would teach a ceiling of only
+19.617 own score. The next learner must be optimized and evaluated closed-loop as the complete
controller; neither low-level D11 command substitution nor unconstrained D21 full-policy PPO is
eligible for reuse unchanged.

## Next experiment

D37 must freeze a **complete hierarchical policy-learning pilot** rather than another oracle or
resident residual:

1. let the learned controller own the game from the initial state through terminal, with no
   resident commands or phase fallback;
2. use the validated factorized persistent-job/provenance vocabulary as the high-level action
   interface, extended prospectively with explicit workforce-funding/TRAIN decisions;
3. retain exact official maps, both seats, the eight-opponent panel, exact referee/stall behavior,
   and terminal score decomposition;
4. train closed-loop with a conservative curriculum/initialization that preserves renewable
   production mechanics while optimizing the dual own/opponent terminal objective;
5. evaluate every selectable checkpoint on fixed development seeds against resident, productive
   complete-economy, D11, and random controls, including family and catastrophe gates; and
6. use YT only after a fresh local/GPU backend-parity check passes for this new environment.

The first D37 discriminator is environment/action sufficiency and learning signal, not Arena
placement. A pilot must demonstrate material deterministic held-seed improvement without the
production erosion and tail expansion seen in D21 before any full-scale replica portfolio.

## Evidence and SHA-256

- protocol: `b8fdea694dca73cfa93091c961f4c131781784c07cf49b10beaf45f69e30fbe9`;
- runner wrapper: `6b970b57a6bf9a3589d6569d6822ca12a25c25a968cdef64db71cade96dbeb3d`;
- D36 implementation: `13103106886fdce425fbfd3d2357d02a6cef5f7f5d5ee9c0687553f5cf013033`;
- shared D35 implementation used by the build:
  `267c69b3ede19319d7a69ff3683fbacb7a9858a977e569b7d4db47e1eb248628`;
- analyzer: `cd92e117a10eef9d1765de669e1afb479d0fc1aa0508d5b6f692202c6c4eee3a`;
- development rows: `e16ebd89b59eb0937a1f0144abd8fec65ac043cebb0c9cf7f3ec7391e55d4ae8`;
- development scenario manifest:
  `db768230558239269773ec4c13926f60aed9f15c190bb1394aa988c25b1e3f74`;
- result JSON: `d8d7469d24b84a543e6cc1e56663a941ad87d69964c790a2dbd13efc49496ee3`.
