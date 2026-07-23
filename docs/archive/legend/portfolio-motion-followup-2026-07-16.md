# Locked stochastic-motion follow-up — banana-5 portfolio — 2026-07-16

This supplementary protocol is frozen after the deterministic prospective gate passed its
research rules and before any result against the randomized `motion` opponent is generated.
It does not alter, replace, or relax the deterministic promotion gate.

## Frozen subject and sample

- Candidate: `candidate-agent6553250-banana5-stack-portfolio.min.rs`
- Candidate SHA-256: `96ef33e77c10281510f0f3ee5ceef912bb6cf27e3b463276b8257aa6e9a234db`
- Control: exact live `agent-6553250-yamo-orchard-live.min.rs`
- Opponent: historical `v1.20.0-motion.min.rs`
- Maps: the same prospective seeds 10,000 through 10,299, without refitting.
- Repetitions: five independently launched matches per seed, policy, and seat pairing.
- Both seats in every repetition.
- Total: 3,000 paired cells / 6,000 games.
- Runtime: 16 process workers by default. Worker count may change on resume because it cannot
  affect an outcome-defining source, map, repetition, seat, or rule.

Rust randomizes `HashMap`/`HashSet` iteration independently in newly launched processes. Live and
portfolio therefore cannot share an identical random draw from this opponent. Results are first
averaged across the five repetitions within each seed and policy. The policy delta is then the
portfolio average minus the live average. On high-banana maps the portfolio executes exact-live
logic, so its observed delta distribution is retained as an empirical null for this launch noise.

## Predeclared interpretation

Directional stochastic support requires all of the following on low-banana seeds:

1. Mean delta is positive.
2. Five-percent-trimmed mean is positive.
3. Mean remains positive after removing the largest seed result.
4. Wins exceed losses.
5. Mean delta exceeds the high-banana exact-live empirical-null mean.

Strong stochastic support additionally requires the lower bound of the normal 95% interval for
the low-minus-high mean difference to be positive.

Regardless of the outcome, this follow-up cannot make the candidate promotion-ready: the locked
deterministic gate's worst-decile requirement failed. Its purpose is to decide whether the next
iteration should preserve the scarcity branch's average benefit and specifically reduce tail risk,
or reject the branch because its benefit does not survive the randomized opponent.

## Frozen-follow-up result

All 3,000 paired cells / 6,000 games completed. On the 208 low-banana seeds the repeated-motion
delta was -0.070 mean, -0.587 trimmed, -0.463 after removing the largest result, and 95/12/101
wins/ties/losses. The high-banana exact-live empirical null was -0.030 mean. Low minus high was
-0.039 with normal 95% interval [-2.343,+2.265]. Every directional check failed; the frozen
decision is **no stochastic support**. This cannot alter the deterministic gate and does not
promote or arena-authorize the candidate.

Artifact: `data/analysis/live-agent-6553250/portfolio-motion-followup-2026-07-16.json`.
