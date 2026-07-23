# D103a D40 opponent-growth phase decomposition — result

Date: 2026-07-22  
Status: integrity pass; mixed failure boundary; closed-loop opponent-aware controller required

## Verdict

D40's opponent-growth failure is not localized to its opening, its scaled workforce, or its long
tail. The opening contributes only `+9.480` opponent points, while the post-scale common horizon
contributes `+25.715` and the terminal-duration tail contributes `+30.748`. The latter two account
for 39.00% and 46.63% of the exact `+65.943` total, respectively; neither reaches the frozen 50%
primary-boundary rule.

Classify the result as **mixed**. Do not reopen an isolated opening rule, fixed third-worker role,
terminal cutoff, task-message imitation, static selector, or online Monte Carlo. The next eligible
representation must own the whole trajectory and condition production, source control,
suppression, and stopping on opponent-aware field state.

## Reproducibility and integrity

The fixed panel contains 32 official maps (`9_824_100..9_824_131`), both seats, eight opponent
families, and both exact policies: 1,024 episodes and 170,587 advancing intervals per run. The
one-worker and 20-worker TSVs are byte-identical, SHA-256
`bb9521faccc6b2811f698d8d97abf93b0724dfe78e0c2441a01c02920c859c07`.

Every frozen gate passes. Interval indices, state links, terminal markers, stock-flow identities,
cumulative counters, episode grids, frozen source hashes, direct-D40 parity, D102 terminal parity,
and command/provenance/deposit checks are exact. Nearest-boundary distance is 0.875 turns on
average and three turns at p95, below the frozen 5/15 limits. One task ends D40 145 turns before
the resident, but the signed terminal-tail accounting handles that outlier exactly.

The first analysis pass exposed a measurement-only omission: a nearest D40 boundary can precede
the resident terminal, so the terminal-duration component must include the resident's signed
boundary-to-terminal tail. This correction is nonzero in 18/512 tasks and averages only `-0.225`
opponent points; it makes all three components exactly additive without changing traces,
controllers, frozen thresholds, or the verdict.

The one-worker execution took 193.01 seconds and the 20-worker execution 196.05 seconds. Twenty
workers are 1.6% slower on this host, again confirming that the current quota/contention regime
cannot accelerate this simulator workload through more local processes.

## Phase result

| D40 minus resident opponent score | Mean | Share | Map-clustered 95% interval |
|---|---:|---:|---:|
| Pre-scale | +9.480 | 14.38% | [+5.121, +13.840] |
| Post-scale, common horizon | +25.715 | 39.00% | [+18.456, +32.974] |
| Terminal-duration tail | +30.748 | 46.63% | [+23.423, +38.073] |
| Total | +65.943 | 100.00% | — |

Earlier and later common-boundary sensitivity choices retain the mixed verdict. They assign
47.59%/38.18% and 45.72%/39.59% to tail/post-scale, respectively. Both seats show the same split:
tail is about `+30.7`, post-scale `+24.2..+27.3`, and pre-scale `+9.4..+9.6`.

The family structure reinforces the closed-loop conclusion. Post-scale growth dominates against
`legend_balanced` (`+70.313`) and `script_boss` (`+52.953`), while the tail dominates against the
resident (`+79.391`) and is large against `gold_adaptive` (`+61.047`) and `silver_boss`
(`+43.250`). A single phase patch would address the wrong failure mode for several families.

## Crop-flow mechanism

Opponent-created crop excess is `+3.150` per task: `-1.617` before scale, `+2.100` in the
post-scale common horizon, and `+2.668` in the terminal tail. D40 removes 49.12% as many opponent
crops as are born before scale and 109.60% after scale (the latter also clears inherited stock),
versus 79.04% over the resident's whole game. Thus suppression activity exists; the loss comes
from coordinating it with renewable production and match duration, not from a globally absent
chopper.

D40 itself creates on average 4.889 owned crops before scale, 21.619 after scale through the common
horizon, and another 6.848 in the tail. The productive loop and opponent opportunity expand
together, which is precisely why independent producer and endgame rules are insufficient.

## Rank-one message preflight

All ten fixed D95 `delineate` games contain exactly zero `MSG` commands. D88's explicit message
grammar cannot transfer to the current rank-one agent. Complete latent task reconstructions and
late worker grafts were already tested and failed earlier; do not repeat them under a different
name.

## Next eligible branch

Open D104 as a prospective representation audit for complete closed-loop opponent-aware policy
improvement. It must expose trajectory state rich enough to distinguish renewable ownership,
opponent crop stock/lineage, source survival, workforce and bills, terminal pressure, and
collision-safe joint assignments. Before expensive PPO or another broad population, prove on
fresh maps that a bounded policy class is active, mechanically safe, and has attainable
trajectory-level value across every opponent family. No candidate or platform action opens from
D103.

## Artifacts

- `d103a-d40-opponent-growth-phase-decomposition-protocol-2026-07-22.md`
- `d103a-d40-opponent-growth-phase-decomposition-{a-jobs1,b-jobs20}-9824100-9824131.tsv`
- `d103a-d40-opponent-growth-phase-decomposition-result.json`
- `rust/src/bin/d103_opponent_growth_phase_decomposition.rs`
- `cgauto/analyze_d103a_opponent_growth_phase_decomposition.py`

