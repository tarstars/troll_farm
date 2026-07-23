# D159a current-resident all-finished effect refresh — frozen protocol

Date: 2026-07-23  
Status: frozen before the current platform outcomes are fetched

## Question

Across every currently exposed finished battle of the exact stable resident, which failure
mechanisms repeat outside the original D23 sample strongly enough to justify the next controlled
resident-anchored experiment?

This is a read-only measurement experiment. It may read leaderboard, battle-list, and completed
game-result records. It must not create a game, use a reserved map, submit source, change the
resident, or construct a candidate.

## Frozen identity and corpus

- Current resident: agent `6561795`, submission `41015603`.
- Exact source: `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, 62,725 bytes,
  SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Historical control: the exact 80 game IDs in
  `d23-current-resident-field-refresh-2026-07-20.json`, SHA-256
  `0567f474d44270cb97087a2254c3506f55f49ae122694d82d2fb1dd863cc5075`.
- Request up to the most recent 250 finished battles exposed by the test-session handle and retain
  only rows whose player agent is exactly `6561795`.
- Define `historical80` by exact D23 game-ID membership, `suffix` as exact-resident game IDs not in
  D23, and `all_current` as their union. List position is never used as a cohort label.

Before fetching, repair one known referee-message omission in the existing parser: both
`damaged a tree` and `collected N WOOD` are one successful CHOP effect. This changes only effect
telemetry, not policy behavior or selection. Recompute both cohorts through the same corrected
parser; do not compare old and new `chops_landed` values across parser versions.

The reserved maps `9,844,200--9,844,215` remain sealed and are irrelevant to this read-only study.

## Integrity gates

The result is decision-bearing only if all of the following hold:

1. the leaderboard still identifies agent `6561795` as the resident;
2. at least 160 exact-resident games parse and `suffix` contains at least 80 games;
3. all 80 historical D23 game IDs are present exactly once;
4. there are no duplicate retained IDs, fetch failures, identity mismatches, or unknown replay-diff
   updates; and
5. terminal scores, turn count, effect telemetry, and crop provenance exist for every retained row.

If a gate fails, report the partial audit but do not prioritize an implementation from it.

## Frozen analyses

For `historical80`, `suffix`, and `all_current`, report:

- games, wins/ties/losses, mean and median margin, score components, and bootstrap 95% confidence
  interval for mean margin;
- ordinary loss and catastrophic loss (`margin <= -100`) frequency, negative-margin mass, and
  distinct-opponent breadth;
- own/opponent workers, successful plants, harvested fruit, wood, and opponent planted-tree value;
- opponent-crop contact/interception, reachable-but-uncontacted crops, and harvest-before-contact;
- score/wood/workforce/planting trajectories at turns 50, 75, 100, 150, 200, 225, and 300; and
- early-lead reversals, defined before seeing outcomes as positive resident score margin at turn
  100 followed by a negative terminal margin.

Use deterministic game-ID bootstrap resampling with seed `15901` and 10,000 replicates. Descriptive
early-risk rules may be shown, but no rule, selector, or candidate may be fitted on D159.

## Replication and prioritization rules

The old anti-compounding signature replicates only if the `suffix` independently has all four:

- catastrophic frequency at least 10%;
- catastrophes carry at least 50% of negative-margin mass;
- catastrophes span at least three opponents; and
- catastrophic opponents finish with at least +20 mean wood versus non-catastrophic opponents.

Regardless of that binary gate, create an attack-angle matrix with one row per repeated mechanism.
Score each direction from 1 (weak) to 5 (strong) on suffix replication, resident-relative upside,
resident-preserving testability, field fidelity, implementation tractability, and tail safety.
Rank by the unweighted total, then suffix replication, then resident-preserving testability. The
next experiment must use the exact resident as fallback/control and target the highest-ranked
mechanism that is independently visible in `suffix`; otherwise collect new field-native causal
data rather than reviving a closed simulator branch.

## Outputs

- corrected raw replay census:
  `d159a-current-resident-all-finished-effect-refresh-raw.json`;
- deterministic analysis:
  `d159a-current-resident-all-finished-effect-refresh-result.json`;
- human result and prioritized attack matrix:
  `d159a-current-resident-all-finished-effect-refresh-result-2026-07-23.md`.

No D159 outcome authorizes Arena submission or resident mutation.
