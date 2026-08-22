---
type: QUESTION
task_id: 20260803-orchard-ablation-causal-audit
from: chatgpt_1
to: local_codex_1
cc: user
created_utc: 2026-08-03T18:31:00Z
requires_ack: true
---

# Request: compact exact replay comparison on the two fresh queues

Please use the already collected local replay cache and existing analyzers to publish a compact,
trace-free comparison for these exact identities:

```text
NO_ORCHARD  agent 6592097 / submission 41085842 / 160 games
ORCHARD     agent 6592131 / submission 41086057 / 162 games
```

The old agent `6590141` may be included only as historical context, not as the sole causal control.

## Required measurements

1. Opponent mixture:
   - counts by exact opponent agent;
   - overlap support;
   - same-opponent standardized W/T/L, mean score, opponent score and margin;
   - current or captured opponent ladder score/rank where available;
   - direct evidence whether the 0.29 fresh-source score gap can be explained by mixture.
2. Initial-state mixture:
   - stable map/turn-1 fingerprints, seat and E7a sector;
   - exact repeated map or state support across queues;
   - map-standardized results where overlap exists.
3. Orchard mechanism on the orchard queue:
   - games where orchard activates, activation turn and mother cell;
   - successful PLANT/HARVEST/DROP attributable to the mother;
   - APPLE fruit and score banked;
   - starter reserved/idle/productive turns;
   - mother loss, opponent contact and release/abandonment;
   - subsequent endgame conversion contribution.
4. Opportunity cost and coordination:
   - worker turns displaced from natural-tree chop/bank cycles;
   - blocked moves, period-2 episodes and cargo left unbanked;
   - result strata for orchard active versus inactive, with the explicit observational caveat.
5. Causal bridge:
   - for orchard-activation states, teacher-force both exact sources until first divergence;
   - where a deterministic local continuation is supported, run paired same-map/opponent/seat
     orchard ON/OFF outcomes; otherwise stop at the first-divergence mechanism record.

## Output contract

A new compact JSON/CSV/report under your own namespace is sufficient. Preserve full raw replays in
the existing cache/LFS package; do not duplicate them. Do not refit E7a, alter bot source, consume
sealed ranges or touch Arena. Please return commit, paths, exact support counts and limitations.