# D164a current-field macro-transition audit — frozen protocol

Date: 2026-07-23  
Status: frozen before the D164 platform snapshot

## Question

Which recurrent action episodes and economy-state transitions used by the current Legend leaders
are absent from the exact resident and from the fixed D162/D163 option grammar, and therefore
deserve the next resident-anchored causal implementation?

D164 is read-only hypothesis generation. It may read the public leaderboard, battle lists, and
finished replay bodies. It must not start a game, submit source, change the resident, open a local
reserved map, fit a score selector, or produce a candidate.

## Immutable acquisition

- Target resident identity: agent `6561795`, submission `41015603`, exact source SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Snapshot ID: `20260723T074715Z-d164a`.
- Use the existing unauthenticated, rate-limited immutable snapshot collector with resident
  `6561795`: retain all exposed finished resident battles and the latest ten finished battles for
  each current leaderboard rank 1--20 agent. Sampling must not use outcomes.
- Store the raw cache, snapshot metadata, parsed trajectories, and other bulk products only below
  the external-backed logical root `data/external/arena-corpus`; run the storage preflight first.
- The acquisition is bounded to at most 500 unique games and at least 0.35 seconds between public
  requests. A larger manifest invalidates analysis; it does not authorize extending the pull.
- Reuse bodies already present in that external cache. Do not copy browser state, credentials, or
  private session material.

## Integrity and population gates

The result is decision-bearing only if:

1. the snapshot completes with zero request, replay-shape, parse, identity, or unknown-diff
   failures;
2. the leaderboard contains exact agent `6561795` under pseudo `tass`;
3. at least 160 exact-resident games and at least 15 current top-20 source agents parse;
4. at least 150 current top-20 source appearances exist, with no more than ten appearances per
   source agent selected by the collector;
5. game IDs and decoded trajectories are unique, terminal inventory/score telemetry is present,
   and decoded turn counts agree; and
6. no sealed-confirmation trajectory is enumerated or used. D164 analyzes only the snapshot's
   open products.

If acquisition is healthy but a population threshold fails, retain the snapshot and issue a
non-decision-bearing freshness report.

## Frozen abstractions

Analyze each actor/game occurrence without using outcome for inclusion. Compare current ranks
1--5, ranks 6--20, and the exact resident at four levels:

1. **Actions:** successful TRAIN, PLANT, HARVEST, CHOP, DROP, PICK, and MINE by phase and worker.
2. **Episodes:** ordered, referee-confirmed motifs within a worker or worker pair:
   own-crop creation then reaping; reaping then banking; banking/funding then TRAIN; persistent
   production overlapping opponent-crop suppression; and producer/suppressor role handoff.
3. **State transitions:** workforce, deposited and carried stock, live own/opponent crop assets,
   fruit, wood, and production/suppression roles at turns 75, 100, 125, 150, 175, 200, and 225.
4. **Controller grammar:** classify each repeated motif as represented by exact resident behavior,
   D162 fixed reserve/commit/abort, D163 fruit routing, D163 IRON routing, D163 consumption
   protection, or **missing**.

Report cohort prevalence, distinct-agent support, timing, both seats, and score/margin only as
descriptive endpoints. A “field-stable missing motif” requires:

- presence in at least 30% of rank-1--5 appearances;
- support from at least three rank-1--5 agents;
- presence in at least 20% of rank-6--20 appearances; and
- exact-resident prevalence at least 15 percentage points lower than rank 1--5.

Rank surviving motifs on breadth, resident gap, causal isolatability, exact-resident fallback
compatibility, implementation cost, and tail risk. History constraints override descriptive rank:
a motif already causally rejected by D102, D162, or D163 is closed unless the audit identifies a
specific missing state transition or coordination primitive that makes it materially different.

## Decision

Freeze exactly one next causal hypothesis: the highest-ranked field-stable missing motif that is
not already represented or causally closed. Its first experiment must use exact resident
fallback/control on already-consumed local maps and must separately prove activation, resident
parity outside the bounded episode, mean value, own-score protection, family breadth, and tail
safety.

If no motif survives, do not tune the fixed reserve grammar. Change representation to
trajectory-conditioned action valuation and specify what new causal data it requires.

D164 cannot authorize a platform game, Arena submission, PPO fit, or resident mutation.
