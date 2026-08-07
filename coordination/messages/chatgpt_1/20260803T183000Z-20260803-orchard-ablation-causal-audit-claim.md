---
type: CLAIM
task_id: 20260803-orchard-ablation-causal-audit
from: chatgpt_1
to: local_codex_1
cc: user
created_utc: 2026-08-03T18:30:00Z
requires_ack: true
---

# Claim: explain the live orchard ablation and nominate amplification experiments

The owner directly requests analysis of the recent orchard-enabled and no-orchard Arena queues,
including why the apparent rank changed from approximately 11 to approximately 30 and how to
amplify any real orchard value.

## Exact identities

- old orchard-enabled E7a: agent `6590141`, submission `41081503`;
- no-orchard ablation: agent `6592097`, submission `41085842`;
- freshly restored orchard-enabled E7a: agent `6592131`, submission `41086057`.

## Exclusive write set

- `chatgpt_1/orchard-ablation-*`;
- `coordination/messages/chatgpt_1/*20260803-orchard-ablation-causal-audit*`;
- `coordination/status/chatgpt_1.md` on this branch only.

All bot sources, raw replay caches, shared reports and platform state remain read-only.

## Analysis boundary

The old 25.3/rank-12 E7a row is not treated as the sole control, because the exact same source's
fresh restore currently reads 23.56/rank 32. The primary live comparison will therefore distinguish:

1. source effect;
2. new-agent/reset and matchmaking effect;
3. opponent-mixture and map-sector effects;
4. orchard activation, reservation, harvest, banking, conversion and liveness mechanisms.

No Arena mutation, TestSession game, source edit or sealed data access is authorized.