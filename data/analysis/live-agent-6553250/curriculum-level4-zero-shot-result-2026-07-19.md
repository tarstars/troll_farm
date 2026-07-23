# Curriculum Level 4 zero-shot composition diagnostic — 2026-07-19

## Result

The accepted seed-79 Level-3 actor solves 1,805/2,000 (90.25%) Level-4 episodes without seeing a
Level-4 label.  Nontrivial success is 91.01%, height floor 89.20%, crop creation 94.35%, renewable
harvest 92.45%, and paired teacher median delay zero.  This is diagnostic only and did not change
the frozen Level-4 plan.

| Recipe | Zero-shot success |
|---|---:|
| cheap planter | 67.06% |
| compact farmer | 97.74% |
| balanced producer | 99.60% |
| harvest producer | 70.36% |
| Level-1 anchor | 94.02% |
| lean chopper | 98.36% |
| standard chopper | 98.42% |
| hybrid chopper | 97.40% |

The actor retains most of Level 2's conditioning despite four million fixed-standard-chopper PPO
decisions at Level 3.  Errors are concentrated in the two recipes whose worker capabilities differ
most from the fixed chopper in post-training execution: low capacity/low chop and high harvest/low
chop.  This supports transfer from Level 3 and confirms that the frozen clone should focus on
recipe-conditioned role execution rather than relearn the renewable loop from scratch.

Artifact SHA-256:
`177540f81b0936b2aaed30b072b7470e5b05f9a4c1e41e64fa2173895afe1425`.
