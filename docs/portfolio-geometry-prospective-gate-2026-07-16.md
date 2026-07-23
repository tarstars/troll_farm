# Locked prospective gate — banana-5 geometry portfolio — 2026-07-16

This second-iteration protocol is frozen before any policy outcome is generated on its seed
block. The prior 10,000..10,299 block was used to diagnose the stack: all 21 bottom-decile losses
came from pre-seeding, while secure-orchard geometry had 11 wins, 197 ties, and zero seed-balanced
losses. That block is selection evidence and is not reused here as validation evidence.

## Frozen subject

- Candidate: `candidate-agent6553250-banana5-geometry-portfolio.min.rs`
- Candidate SHA-256: `781f35a07cd31f5b344381c0d7e1174f0e655e8076bb3084a4d5b115b5879afe`
- Candidate rule: initial banana fruit total <= 5 selects secure-orchard coverage; otherwise exact
  live. The pre-seed mechanism is absent.
- Secure-orchard reference SHA-256:
  `3e045b7b09f49b2f707382e769f81e779b4d2a6762fa193915ebd938d8e0bea7`.
- Control: exact live `agent-6553250-yamo-orchard-live.min.rs`.

## New prospective sample

- Seeds: 10,300 through 10,599 inclusive; none appeared in policy fitting, the first prospective
  gate, or component diagnosis.
- Frozen map split: 209 low-banana and 91 high-banana seeds.
- Opponents: `taskplan`, `race`, `yield`, `ringfix3`, and `chopharvest`.
- Both seats for every cell.
- Live and candidate run on all maps; the secure-orchard reference runs on low-banana maps only.
- Total: 4,045 paired cells / 8,090 games.
- Runtime: 16 process workers by default. Worker count may change on resume without changing any
  source, map, branch, opponent, seat, or gate.

The process-randomized historical `motion` bot remains excluded from this exact gate. It may be
run as a separately labeled repeated stochastic follow-up only if the deterministic gate passes.

## Predeclared research-pass rules

All must hold:

1. Every high-banana candidate cell exactly equals live.
2. Every low-banana candidate cell exactly equals the frozen secure-orchard reference.
3. Low-banana seed-balanced mean delta is positive.
4. Low-banana five-percent-trimmed mean is positive.
5. Low-banana mean remains positive after removing its largest seed result.
6. Low-banana wins exceed losses.
7. Mean delta is nonnegative against every deterministic opponent.

## Additional promotion rules

Promotion readiness additionally requires a positive lower normal 95% interval bound and a
nonnegative worst-decile mean on low-banana seeds. Even a full pass cannot authorize an arena
write: exact live remains resident until the platform first passes a healthy same-code A/A
reconvergence control.

## Frozen-gate result

All 4,045 paired cells / 8,090 games completed. The candidate matched exact live in all 455
high-banana cells and the secure-orchard reference in all 1,045 low-banana cells.

The low branch produced 5 wins, 204 ties, and 0 losses: +1.474 mean, +1.028 after removing the
largest seed, normal 95% interval [+0.103,+2.846], nonnegative worst decile, and positive means
against all five opponents. However, the five positive seeds are fewer than the ten observations
removed from each end by five-percent trimming; the trimmed mean is exactly 0. The predeclared
rule required it to be strictly positive. The formal frozen decision is therefore **reject**, even
though both additional promotion-tail checks passed. No motion follow-up or arena write follows.

Artifact:
`data/analysis/live-agent-6553250/portfolio-geometry-prospective-gate-2026-07-16.json`.
