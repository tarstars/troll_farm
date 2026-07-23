# Locked prospective gate — banana-5 portfolio — 2026-07-16

This protocol is frozen before the prospective outcomes are generated.  No feature, threshold,
policy branch, opponent, seed, or decision rule may be changed after looking at the result.

## Frozen subject

- Candidate: `candidate-agent6553250-banana5-stack-portfolio.min.rs`
- SHA-256: `96ef33e77c10281510f0f3ee5ceef912bb6cf27e3b463276b8257aa6e9a234db`
- Branch rule: initial banana fruit total <= 5 selects the complete stack; otherwise exact live.
- Control: `agent-6553250-yamo-orchard-live.min.rs`

## Prospective sample

- Seeds: 10,000 through 10,299 inclusive.  This lies outside the previously reused 0..999 range.
- Opponents: `taskplan`, `race`, `yield`, `ringfix3`, and `chopharvest`.
- Both seats for every map/policy/opponent cell.
- Eight worker threads.
- Total: 3,000 paired cells / 6,000 games.

Execution note: the first 450 paired cells used eight process workers.  At the user's explicit
request, the resumable runner then increased to 16 process workers on the 20-core host.  Worker
count affects elapsed time only; all outcome-defining seeds, sources, hashes, opponents, seats,
and gates remain frozen.

The historical `motion` opponent is excluded from the exact prospective gate because its Rust
`HashMap`/`HashSet` iteration is process-randomized.  It may receive a separately labeled repeated
stochastic follow-up only after this deterministic gate.

## Predeclared research-pass rules

All must hold:

1. Every high-banana portfolio cell is exactly equal to live in scores, wood, command counts,
   opponent responses, and terminal turns.
2. On low-banana seeds, seed-balanced mean delta is positive.
3. Low-banana 5%-trimmed mean is positive.
4. Low-banana mean remains positive after removing its largest seed result.
5. Low-banana wins exceed losses.
6. Mean delta is non-negative against every deterministic opponent.

Failure of any rule rejects the portfolio.  Passing retains it as a research candidate.

## Additional promotion rules

Promotion readiness additionally requires a positive lower 95% normal interval bound and a
non-negative worst-decile mean on low-banana seeds.  Even if those pass, no arena write is allowed
until an exact-live same-code A/A control reconverges normally.

## Frozen-gate result

The completed run contains all 3,000 paired cells / 6,000 games. There were 208 low-banana and
92 high-banana seeds. High-banana equivalence passed in 460/460 cells.

On low-banana seeds the candidate scored +1.934 mean, +0.492 five-percent-trimmed mean, and
+1.427 after removing the largest seed. The normal 95% interval was [+0.497,+3.370], wins/ties/
losses were 96/40/72, and all five opponent means were positive. Every frozen research rule
therefore passed. The worst-decile mean was -4.952, so the additional promotion rule failed and
the frozen decision is **retain as a research candidate, not promotion-ready**.

Artifact: `data/analysis/live-agent-6553250/portfolio-prospective-gate-2026-07-16.json`.
