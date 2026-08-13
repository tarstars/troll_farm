# E7a half-size closed-loop iteration — 2026-08-03

## Boundary

This is engineering evidence for the owner-directed logical simplification task.  The
deterministic generated-map `motion` smoke is a fast regression discriminator, not an
Arena predictor and not a qualification panel.  No Arena mutation occurred.

Exact baseline:
`cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`, 62,820
bytes, SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`.
The target ceiling is 31,410 bytes.

## Iteration history

The first size-qualified source, r5, was 30,949 bytes but destroyed renewable supply and
closed-loop value: across eight seeds and both seats against `motion`, its mean paired
margin delta was -262.5, with 14/16 catastrophes versus 2/16 for the exact E7a baseline.
It is retained only as proof that the size target is mechanically reachable.

Successive functional repairs restored, in order: scarcity-gated regeneration, cargo-first
banking, stable per-worker doors, fruit-cargo banking, immediate DROP priority, and
route-aware second-worker selection.  Intermediate r6--r17 results were negative
engineering iterations.  They are preserved as generated sources and manifests in the
owner worktree but are not candidate artifacts.

r18 is the best current behavior-preserving point:

| Measurement, 8 seeds x 2 seats vs `motion` | Exact E7a | r18 |
|---|---:|---:|
| Source bytes | 62,820 | 35,146 |
| Mean own score | 169.3125 | 148.5 |
| Mean opponent score | 156.1875 | 142.0 |
| Mean final own wood | 42.25 | 36.6875 |
| Catastrophes | 2/16 | 3/16 |
| Maximum period-2 MOVE-target run | 6 | 3 |
| Mean paired margin delta | — | -6.625 |
| Seat-0 / seat-1 mean delta | — | -12.625 / -0.625 |

r18 is still 3,736 bytes above the ceiling, so it cannot satisfy the task.

r19 added two speculative direct-chop rules: avoid trees occupied by an opponent chopper,
and value predicted size growth during travel/chop.  It grew to 35,589 bytes and regressed
mean paired margin delta to -11.4375; candidate score fell to 145.9375, catastrophes stayed
3/16, and the maximum period-2 run rose to 4.  Both additions were rejected and the builder
was restored byte-exact to r18 output (SHA-256
`588c6c046e5f7e61688c3629c641603768a88035286b0bec743043a956be13d8`).

## Reproducibility

Runner:
`local_codex_1/e7a-half-size-logical-simplification/evaluate_motion_smoke.py`.

Exact result records:

- `integrated-half-r18-motion-smoke.json`
- `integrated-half-r19-motion-smoke.json`

The runner compiles the exact baseline, candidate, and frozen `motion` opponent, installs
the deterministic clock/entropy shim, and evaluates seeds 0--7 with both seat assignments.

## Current decision

Continue from r18 behavior, not r5 size and not r19 forecast.  The remaining reduction is
3,736 bytes.  The next deletion target is structural duplication in the focused
second-worker estimator and two-worker movement guard.  Any successor must first retain
r18's training/banking/liveness behavior on this smoke, then clear the frozen semantic,
liveness, open-panel, and latency gates before Arena use.

Sacred source verification remains exact at SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
