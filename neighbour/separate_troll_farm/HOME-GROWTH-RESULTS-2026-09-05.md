# Guarded home-growth candidate

Local experiment under HOME-GROWTH-PROTOCOL-2026-09-05.md. V439 remains the live bot,
last verified mature rank28; the top-seven goal is not achieved. No new platform request
or publication has been made for this candidate. Canonical bot.rs/submission.rs are unchanged.

## Implementation and primary review

The tested compact kernel is wrapped around the exact frozen V439 body. Its baseline runs
once per observed turn. At most one exact selected CHOP becomes MOVE onto that actor's own
cell, independently verified to have WAIT's game effect. All other commands and their order
are preserved. The wrapper does not clone or commit speculative policy memory.

Guards require an empty-handed own worker with capacity>=2/chop>0 on a young live tree
adjacent to home, no friendly occupancy or selected arrival, no current PICK/TRAIN spending,
at least two trees, supported finite bank stocks and remaining deadline, a strict kernel
banked-score gain, and no actual enemy able to arrive by the chosen first bank turn.
Enemy BFS starts at actual positions, including inside shacks, and does not clamp speed.
Only one actor is overridden per turn; all assumptions are reevaluated next turn.

Claude wrapper/export proposal54654 completed successfully, USD2.558923. Primary removed
an erroneous formatting-dependent <=180-line test: the proposed production wrapper had251
lines. The actual exported UTF-16 limit remains enforced. Primary added matched-compiler
execution of the Rust guard fixtures and tested the frozen panel preparation.

Claude adversarial review74682 completed, USD1.320058. Its concrete reordered-command
fixture exposed a latent friendly-slot guard hole, not reachable under the current sorted
two-worker baseline. The wrapper now refuses an override if a friend's slot names another
unit. Primary added a reachable speed4 fixture that would fail a speed3 clamp; an isolated
speed9 enemy alone would not test that boundary. All22 wrapper Rust cases pass, in addition
to the kernel's15 cases, including6920 independent referee transition comparisons.

## Frozen production and execution evidence

Working root: `/data/separate_troll_farm-working/home-growth/2026-09-05/`.
Initial `packaging/`, `benchmark8/`, `benchmark160/` and unused `panel/` are preserved;
the hardened finalist is `guarded-packaging/`. No adaptive games used the initial export.

- Readable SHA `7ad24bd45714a693e2efd1b93903fd62bf057ddb0a450d2d59fd590779925310`.
- Compact SHA `2a43df649a300013b03ed1ee7013808dd7548ff406d316e91e85ab82f8530dff`,
  **69,120 UTF-16 units**.
- Module SHA `2897f91eed60d64c3dce12a272218170544dd00198f6afb993116a31b7c3ff00`.
- Default matched rustc1.90.0 optimized builds, no command-line warning suppression:
  readable6.589s /compact6.535s, zero stdout/stderr. Exact command and binary hashes are in
  `guarded-packaging/exact-builds.json`. Local compiler success is not remote deployment proof.
- `guarded-benchmark160/report.json`:160 streams/43,263 turns,2273 kernel calls,41 overrides,
  zero fallbacks, zero readable/compact differences, zero differences from the pre-hardening
  candidate. Max decision8.964ms readable/9.993ms compact, zero over50ms. The41 changes cover
  24 archived games; this sparse activation is not evidence of competitive strength.
- `guarded-exact-aa.json`: actual uninstrumented readable/compact binaries agree on every
  archived turn. Its136 recorded-baseline-exact games compare the new policy with recorded
  V439, not a packaging requirement; the remaining24 are expected new-policy differences.
- `guarded-startup.json`:320 open-stdin launches across8 maps/both seats, correct first
  commands, max11.719ms, zero over50ms. Instrumented and exact binaries are kept distinct.
- Full repository suite: **562 passed in208.80s**, session50714 terminal0,
  `full-suite.log`. This includes the final guard and frozen panel-preparation tests.

## Adaptive comparison

The predeclared192-pair familiar8-map/12-proxy comparison completed in `guarded-panel/`.
Exact baseline module and the independently verified Java plant-order correction are frozen
in its manifest. The gate remains >=+1 match point, <=4 negative map point deltas, and zero
execution/timing failures. **FAIL: no additional match points. This candidate is closed and
does not advance to a real-agent screen or publication.** All192 pairs are included.

Both arms finish173W/5D/14L,175.5 match points. No individual paired outcome changes and all
eight map-point deltas are zero. Mean own/opponent scores: V439238.4583/110.5625, candidate
240.5677/110.3333. Margin127.8958→130.2344 (+2.3385), banked wood44.2917→44.7292.
Zero execution, command, critical, unclassified or timing failures. Max decision5.480ms
baseline/5.268ms candidate. The exact V439 arm reproduces the frozen familiar-panel reference.

Commands diverge in66 adaptive pairs; first divergence ranges from turn96 to293. Mean paired
margin gain by baseline outcome is+2.5087 in173 wins,0 in5 draws,+1.0714 in14 losses.
This diagnoses a small effect, not independent validation; it does not justify weakening the
match-point gate. The map-point bootstrap is [0,0] because this finite panel has no changed
outcomes, not because uncertainty over unseen maps/opponents is zero.

Each opponent has16 pairs. W/D/L below is identical for both arms; all have zero failures.
The complete baseline/candidate score, wood, margin, seat and map fields are in analysis.json.

| Opponent | Both W/D/L | Candidate own/opp score | Margin delta |
|---|---:|---:|---:|
| boss_real |14/0/2|239.000/77.000|+3.688|
| compact_gold |11/0/5|257.438/233.562|+1.938|
| gold_adaptive |16/0/0|217.438/92.812|+1.250|
| legend_balanced |14/0/2|283.438/148.000|+1.375|
| legend_v3_hp2_four |16/0/0|295.188/91.500|+0.750|
| legend_v7_hp2_four |16/0/0|289.938/66.625|+2.812|
| legend_v8_hp2_four |16/0/0|249.812/74.625|+1.938|
| mybot |15/0/1|225.125/134.875|+1.125|
| norx_native_three |15/0/1|263.562/106.625|+1.500|
| resident |8/5/3|140.312/136.250|+0.500|
| script_boss |16/0/0|243.625/78.125|+8.438|
| silver_boss |16/0/0|181.938/84.000|+2.750|

## Limits

The kernel is exact only for its stated single-cell economy. The wrapper does not prove future
seed stock, friendly traffic, opponent training or global end time. Two current trees merely
exclude the obvious last-tree case. Replanning and arrival guards reduce these risks; they do
not turn the model into an exact two-player forecast. No rank conversion or top-seven claim.
