# Curriculum Level 5 crop-before-scale D9 prospective result — 2026-07-20

## Verdict

**Accept the isolated crop-before-scale naturally funded three-worker abstraction without a new
checkpoint.**  On exact unopened seeds 2,027,000--2,028,999, prospective teacher/random are
1,999/2,000 and 0/2,000.  The unchanged accepted Level-4 actor is 1,908/2,000 = **95.40%** and
passes every frozen gate.

This reproduces the 95.40% development result exactly at four times the sample size.  No behavior
clone, PPO update, YT job, checkpoint selection, deployment, or Arena action occurred.

## Prospective controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **99.95% / 99.92%** | >=95% / >=95% | pass |
| Worst recipe / height | **99.64% / 99.80%** | >=90% / >=93% | pass |
| Player crop / renewable harvest | **99.95% / 99.95%** | >=95% / >=98% | pass |
| Illegal selections / success before 180 | **0 / 0** | 0 / 0 | pass |
| First / third-worker training | **100% / 95.65%** | >=98% / >=90% | pass |
| Fresh receipt before both transactions | **100%** | 100% | pass |
| Standard-chopper / feeder productivity | **100% / 91.50%** | >=98% / >=85% | pass |
| Rival crop creation / own-crop harvest | **99.95% / 88.40%** | >=98% / >=85% | pass |
| Player-crop destruction / above one | **99.80% / 0** | >=95% / 0 | pass |
| Maximum rival workers | **3** | <=3 | pass |
| Random legal | **0/2,000** | <=5% | pass |

The only teacher failure is one hybrid-chopper episode; no recipe, height, or opponent mechanism
is close to its rejection floor.

## Prospective fixed actor

| Measure | Actor | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **95.40% (1,908/2,000)** | >=90% | pass |
| Nontrivial success | **96.10% (1,132/1,178)** | >=88% | pass |
| Worst recipe | **92.74%** | >=82% | pass |
| Worst height | **94.38%** | >=87% | pass |
| Player crop presence | **95.50%** | >=90% | pass |
| Renewable player harvest | **99.20%** | >=95% | pass |
| Paired-teacher median delay | **0 turns** | <=30 | pass |
| Third-worker training / feeder productivity | **95.70% / 91.70%** | >=90% / >=85% | pass |
| Rival crop creation / own-crop harvest | **99.95% / 89.40%** | >=98% / >=85% | pass |
| Player-crop destruction / above one | **99.45% / 0** | >=95% / 0 | pass |
| Fresh funding / maximum workers | **100% / 3** | 100% / <=3 | pass |

The opponent remains fully active under the actor.  Its 107.56 mean score, 95.70% third-worker
training, and 89.40% renewable harvest exclude an interaction-avoidance explanation.

## Conclusions at different abstraction levels

### Causal mechanism

The D6--D8 failures were not evidence that worker three was economically impossible.  They exposed
an ordering bug: the funder abandoned crop establishment before expansion.  Requiring one real
crop before the second funding epoch raises prospective rival crop activation to 99.95% while
retaining ordinary costs and fresh receipts.

### Workforce policy

The result reconciles strong bots' large workforces with prior negative extra-worker patches.  A
worker is valuable only inside a productive sequence:

`two-worker production -> renewable source -> funded expansion -> distinct productive role`.

Adding a worker before the source, or redirecting a productive worker into an unbounded denial
role, pays the purchase and opportunity costs without creating the compounding return.

### Actor representation

The accepted recipe-conditioned actor already represents this level of reactive low-level control.
Its transfer loss from teacher is modest and evenly distributed.  The next missing object is not
another low-level PPO repair; it is broader repeated pressure and eventually autonomous selection
of which macro plan to pursue.

### Compute

Local Rust controls sustain roughly 65k--100k transitions/s; CPU neural evaluation sustains about
9.9k transitions/s and the 2,000-episode actor confirmation takes 71.8 seconds.  YT would be useful
for repeated multi-million-transition neural training, especially parallel PPO replicas.  It is
not profitable for one-off controls or for D9, where the unchanged actor passes and no training is
needed.

### Goal and transfer

D9 remains an isolated curriculum acceptance.  It does not select a first move, maximize a
300-turn score, cover the full strategic opponent, fit a deployed learned controller into the
100k source limit, or provide Arena-rank evidence.  It creates no submission candidate.

## Next direction

Keep the accepted crop-before-scale economy and isolate repeated crop pressure: replace the
one-destruction cap with a small preregistered bound while preserving natural funding, roles, and
turn-180 validity.  Only a control-valid actor failure would open clone/PPO and the local-versus-YT
benchmark.  After repeated pressure, broaden opponent scope or connect an autonomous first-move
selector rather than tuning worker prices.

## Reproducibility anchors

- prospective protocol:
  `143ac45739025e9326b04a7a981f6f98cdd858afe49131246d47c6e14e823c28`;
- prospective teacher:
  `e4b77a71d937611a3a369dbace71550816706e7033a26ecaa4f968471bc27048`;
- prospective random:
  `75440725137a1f66dfbf3290f594365f4c23bf778178959168e06108b427db0e`;
- prospective actor:
  `edd9efb57805bcfff16f381091accd6cb63afa21ec28ef2dc209a194aeb6defb`;
  and
- accepted checkpoint, unchanged:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
