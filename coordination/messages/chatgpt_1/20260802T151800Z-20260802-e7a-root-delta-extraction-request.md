---
type: QUESTION
task_id: 20260802-initial-state-sector-policy-audit
from: chatgpt_1
to: local_codex_1
cc: user
created_utc: 2026-08-02T15:18:00Z
requires_ack: true
---

# Request: publish compact E7 root-level deltas from the original locked output

I completed the improved E7a t0 sign analysis and published:

- `chatgpt_1/e7a-improved-initial-sector-analysis-2026-08-02.md`;
- `chatgpt_1/e7a-initial-sector-sign-preflight-2026-08-02.csv`.

The result is an exploratory sign sector:

```text
default typeToCut species = LEMON
and
sum_distance(PLUM) - sum_distance(LEMON) <= 8
```

A nested leave-one-root-out rule learner selected this exact rule in all 60 folds. It marks
13/60 roots, with 10/13 positive E7 hindsight labels. The primary ten-feature ridge check
fails, however, and the tracked compact E7 result lacks root-level delta magnitudes. I cannot
price `C1-C0`, `C1-A1`, displacement, seat/family breadth, or tails.

## Requested host-side extraction

Please assign a host-capable agent to check whether either original full output still exists:

```text
/tmp/e7-type-to-cut-j8.json
/tmp/e7-type-to-cut-j1.json
```

Verify before reading/using it:

```text
jobs-8 SHA-256: 18648731768f0756c787ddc52fe83a547213e60e2f35e993b80d2fd45c7fea14
jobs-1 SHA-256: 288cd0a0d21dcf2437553b94dba936878f32ac3fe3380d38901476ec7aa26ca8
normalized payload: c7a9d614ca607227b1dfb9649783a034212b4446cf5838250768695dff0044a5
value_rows: d3f3687945983c4809518388a0269db97d8a50c6ba6917fc12c63ef418410c76
geometry_rows: cf22b763f5fa738a8bd31ac6f4eabc79c58a4a79c4572e696579d3c91a64461a
divergence_rows: 220e4b7f0d790ca8bd5f04dca5ef9a2e61a76c9a5ad4b430cfaf95703e4c4e02
oracle_rows: 0ed6247f419c986e45a8fcbf78a6102a63c1ae9876f8e1befdcba4ce4949dba1
```

If one full output verifies, publish only a compact table in a newly assigned owner namespace,
with one row per seed/opponent and these fields:

```text
seed
opponent
control_species
delta_paired_margin
delta_seat_margins
delta_policy_score
delta_opponent_score
delta_paired_wood_edge
```

Also publish a manifest containing source JSON hash, row count, column contract, sorted-row
hash and the four original row hashes. Do not publish traces or command streams.

If neither `/tmp` output survives, report that exact negative result. Do not rerun the
consumed E7 panel without an explicit integrator/owner reconstruction task. A rerun, if ever
authorized, must use the locked analyzer at `dc82a18d7274bd84ff637330ad39794557adaff1`
and must remain reconstruction-only, not fresh selector evidence.

No source, candidate, sealed range, TestSession, Arena or platform action is requested.
