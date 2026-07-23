# D12 resident-idle residual readiness — development result (2026-07-20)

## Decision

**Not ready for counterfactual labeling.  Close D11 inference-time reuse.**

The idle-only gain from seeds 0--7 does not replicate on seeds 8--23.  Do not build a residual
selector from this intervention, do not tune another activation rule, and do not open a
prospective or Arena block.  No resident, candidate, submission, or Arena state changes.

## Complete execution

All 384 frozen exact-engine games completed: seeds 8--23, both seats, the six-opponent mechanism
panel, and paired resident/idle-only policies.  The candidate retained the resident worker count
in all 192 paired cells.

| Measure | Result |
|---|---:|
| map-balanced margin delta | **-0.094** |
| 95% map CI | `[-0.257, +0.069]` |
| cell mean delta | -0.094 |
| changed cells | **8 / 192 (4.17%)** |
| changed outcome signs | 2 positive, 6 negative |
| worst opponent mean | -0.750 (`resident`) |
| wood-edge delta | -0.021 |
| overrides | 1,198 / 103,830 decisions (1.15%) |

Only one of sixteen map means is positive: seed 19 at +0.667.  Six are negative and nine are
exactly zero.  Consequently that one map supplies 100% of positive map-mean mass.  The mechanism
fails three frozen readiness criteria: positive mean, at least 20 changed cells, and no more
than 60% positive concentration in one map.

Opponent means are also consistent with no useful general effect: `compact_gold` 0,
`gold_adaptive` -0.031, `legend_balanced` +0.125, `mybot` 0,
`norx_native_three` +0.094, and resident -0.750.

## Combined interpretation

Across the two development blocks, resident-`WAIT` substitution is sparse and map-sensitive:

- seeds 0--7: +2.375 mean, but almost all gain came from seed 7;
- seeds 8--23: -0.094 mean, only eight terminal outcomes changed, and all positive map mass came
  from seed 19.

The D11 actor can occasionally turn an idle command into value, but this is not a stable policy
class and does not provide enough positive/negative coverage for a trustworthy learned gate.
The failure is upstream: D11 was trained on its own narrow curriculum rather than the resident's
state and joint-intent distribution.  More hand-written inference glue cannot repair that
distribution mismatch.

## Next direction

Start a new resident-aware learning cycle with a different interface and objective:

1. generate full-game resident trajectories against the frozen opponent mixture;
2. represent both workers, the resident's proposed commands/targets, recent intent history, and
   economy state;
3. learn a residual decision—retain the resident command or choose a constrained alternative—
   rather than replace a complete worker role;
4. optimize terminal margin/wood trajectory with full-game continuation value, not isolated
   curriculum reward;
5. qualify the learned controller on disjoint local maps before any source integration.

The immediate next experiment is a coverage and feasibility audit of resident trajectories.  It
will quantify decision volume, state/action diversity, intent persistence, intervention budget,
and the smallest deployable residual action space before training begins.

## Evidence

- protocol: `d12-resident-idle-residual-readiness-protocol-2026-07-20.md`;
- rows: `d12-resident-idle-residual-readiness-seeds8-23.tsv`, SHA-256
  `0fc28ce0db701db7cf79f90c68de9166e2c56b8d84cbacf73d199ef67b2fb5c0`;
- analysis: `d12-resident-idle-residual-readiness-2026-07-20.json`, SHA-256
  `c9041ea3481a69b7a4ff93a433d90f67e14a0e9cd4912f4fa303bf4d93b1de06`;
- analyzer: `cgauto/d12_resident_idle_readiness.py`, SHA-256
  `8acb5c4a6bf00c9dd43118197c1cb6830a8f51b491e466d938bf60627c2037a4`.
