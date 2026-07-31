---
type: HANDOFF
task_id: 20260731-doubtingiyov-tent-proximity-denial-policy
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T14:50:00Z
requires_ack: true
---

# DoubtinGiyov tent-proximity denial candidate review handoff

The owner-directed successor is implemented and locally validated at pushed commit
`a72c16973a74205c3283f59e496362fa29766243`.

Frozen semantics:

- the layer activates with the first standing tree cardinally adjacent to the enemy
  shack;
- at one or two, one worker performs ordinary chop/collect/bank on an adjacent tree,
  while the other denies an opponent-planted tree without a denial-driven return;
- above two, both workers target distinct adjacent trees without denial-driven returns;
- a worker banks pre-existing cargo before entering a non-banking role;
- zero qualifying trees preserves exact parent behavior.

Evidence:

- exact game `897547554` reconstructs 300/300 turns with zero unknown updates;
- the opponent created 37 adjacent generations and banked 24 adjacent-tree items before
  resident first contact;
- fail-closed parent SHA `307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd`;
- candidate
  `cgauto/submissions/candidate-agent6585578-owner-tent-proximity-denial-split-slim.min.rs`,
  67,704 bytes, SHA
  `3bd42d5b33dfb58724686ddfcca93205e953c0ac728595f520307798bb4fd900`;
- 5 compiled candidate tests plus 3 exact-game analyzer tests pass;
- exact 300-state open-loop first divergence is turn 14, with no stderr;
- eight unsealed both-seat smoke cells complete with zero stderr;
- sacred resident SHA remains exact at
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

Please ACK receipt and review the stateful role transition, pre-existing-cargo guard,
opponent-plant attribution, 0/1/2/3 boundaries, and deterministic move-conflict behavior.
This is a code/mechanism review only. Do not submit or mutate Arena state: agent `6585578`
is still the sole cycle in flight.
