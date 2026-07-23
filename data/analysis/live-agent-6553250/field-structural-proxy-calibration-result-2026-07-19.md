# Structural field-proxy calibration — result, 2026-07-19

## Verdict

**Close reuse of the eleven existing structural controllers as field proxies.**  The catalog
fails all five material support gates and still covers none of the held-out rich-immediate games.
The next proxy must be purpose-built for sustained late compounding rather than borrowed from a
controller whose original objective was candidate strength or single-agent imitation.

No previous candidate branch is reopened.  In particular, the native Norxondor controller's
prior `-172.663` candidate margin remains binding; this experiment used it only as an opponent
trajectory model.

## Integrity amendment

The first scorer invocation stopped before selection because `norx_funded_silver` legitimately
terminated at turn 98 in game `896284387`, leaving no turn-100 snapshot.  Before reading any
ranking, the protocol was amended to treat a referee-terminal state as absorbing: its exact final
state and counters are carried to missing checkpoints, while its true terminal turn retains the
independent terminal-distance penalty.  The full 1,760-cell grid was rerun under that rule; no
cell was dropped and no tolerance changed.

Artifacts: `field-structural-proxy-calibration-protocol-2026-07-19.md`,
`field-structural-proxy-phase21-local.tsv`, and
`field-structural-proxy-calibration-2026-07-19.json`.

## Frozen selections and confirmation

| Target | Discovery representative | Discovery macro/full | Confirmation representative macro |
|---|---|---:|---:|
| Rich 3+ farm+wood, immediate | `norx_compact` | 0/12, 0/12 | 0/9 |
| Compact farm+wood, deferred | `norx_compact` | 1/8, 1/8 | 0/6 |
| Compact wood-only, deferred | `norx_funded_silver` | 4/10, 1/10 | 1/4 |

| Gate | Required | Observed | Pass |
|---|---:|---:|:---:|
| Overall macro uplift | +10 pp | +4/80 = +5.00 pp | no |
| Overall full uplift | +5 pp | +2/80 = +2.50 pp | no |
| Catastrophic macro uplift | +15 pp | +0/19 | no |
| Worker-rich macro uplift | +15 pp | +1/28 = +3.57 pp | no |
| Every target representative >=20% | all | 0%, 0%, 25% | no |

Exact-opening support increased by only one ordinary game and by zero critical games.

## Rich residual and causal diagnosis

`norx_compact` is the least-distant rich discovery model despite covering 0/12.  On the nine rich
confirmation games it remains approximately aligned early:

- turn 50 mean errors: score -4.1, wood +0.4, workers -0.1, harvest -2.0, chops +6.9;
- turn 100 mean errors: score +9.0, wood +3.0, workers -0.6, harvest -7.2, chops +15.9.

It then collapses relative to the field by final:

- score -258.4;
- wood -65.8;
- workers -1.67;
- harvested fruit -42.2;
- successful chops -24.2; and
- dropped items -103.4.

Terminal timing differs by only +0.22 turn, so this is not a horizon artifact.  The model reaches
a plausible early state but fails to compound it into four productive generalists.  The existing
Norx workforce wrappers do not fix that because their continuations displace or misassign late
work; Boss4 is even farther from the rich discovery signatures.

At the abstraction levels that matter:

- **Opening:** a replay-derived staged generalist TRAIN ladder is directionally correct.
- **Funding:** the second and later workers need coordinated deficit collection, not passive
  affordability waiting.
- **Production:** after funding, workers must dynamically rotate among harvesting seed, planting
  renewable supply, chopping mature trees, and banking; fixed planter/chopper identities and
  imitation-state intents both fail.
- **Time:** turns 100--300 contain the missing multiplication.  Another opening-only change cannot
  close a 258-point final gap.

## Next experiment

Build a small frozen `LegendFieldProxy` grammar with four harvest/chop-capable generalists,
coordinated staged funding, renewable planting, and post-funding role rotation.  Cross only two
field-supported first-worker ladders with two farmer allocations and two fell-start phases (eight
configs), select on the rich discovery maps, and judge unchanged on confirmation.  This is a new
controller structure, not a wider parameter sweep over any closed policy.
