# D12 resident-idle residual readiness — development protocol (2026-07-20)

## Question

Does the only positive D11 advisory mechanism—letting PPO control the resident-trained second
worker only when the resident says `WAIT`—produce enough distributed terminal signal to support
an offline resident-state residual learner?

This is a mechanism replication and dataset-readiness test.  It is **not** another selector
search, candidate gate, prospective gate, or Arena authorization.

## Frozen substrate

- Stable resident owns training, roles, routes, and every non-idle command.
- Frozen D11 V7 actor adopts the actual trained worker's stats.
- Compare only `resident` and `native_second_idle_only`; no thresholds or action sets may be
  tuned after looking at the block.
- Exact runner SHA-256:
  `3547ff337a69c668d66b865c029af11c5581771b88d124bdc71c6d34a49f4515`.
- V7 source/binary SHA-256:
  `9beae086bd92b4d4be4f7a1e2c40042102ed15ff4bd427cf53ad7e249f859f5b` /
  `30d584ee89c6f225039d8e9c3900622745e328760daed0cc597cedc41f0db9d5`.

## Development replication block

- Seeds 8--23, both seats.
- Frozen six-opponent mechanism panel:
  `resident`, `gold_adaptive`, `compact_gold`, `norx_native_three`,
  `legend_balanced`, `mybot`.
- Two paired policies.
- Games: 16 × 2 × 6 × 2 = 384.
- Parallelism: 20 exact independent games.

These maps are new to the immediately preceding D11 layer catalog but have appeared elsewhere
in project development.  They are therefore a replication block, not a holdout.

## Frozen readiness criteria

The mechanism is suitable for a residual-labeling investment only if all of the following hold:

1. all 384 games complete and resident worker-count parity is 192/192 candidate games;
2. map-balanced mean margin delta is positive;
3. worst opponent mean margin delta is at least -2;
4. at least 20/192 paired cells (10%) change terminal margin;
5. changed cells appear on at least 4/16 maps and against at least 3/6 opponents;
6. both positive and negative changed cells exist, so an accept/reject learner has nontrivial
   examples on both sides;
7. no single map supplies more than 60% of the sum of positive map-mean deltas.

These are dataset-readiness criteria, not promotion criteria.  Passing authorizes only the next
offline experiment: exact one-intervention continuation labels at resident-`WAIT` decisions,
followed by a compact residual accept/reject model and disjoint evaluation.

Failure closes D11 reuse.  The next learned controller must instead change its state
distribution and objective directly: resident trajectories, explicit joint intent/assignment
features, and full-game reward.

## Outputs

- rows: `d12-resident-idle-residual-readiness-seeds8-23.tsv`;
- analysis: `d12-resident-idle-residual-readiness-2026-07-20.json`;
- result: `d12-resident-idle-residual-readiness-result-2026-07-20.md`.
