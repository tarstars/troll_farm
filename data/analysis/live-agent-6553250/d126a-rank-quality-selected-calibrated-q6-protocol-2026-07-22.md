# D126a rank-quality-selected calibrated q6 — frozen protocol

Date: 2026-07-22  
Status: frozen before D126 fit selection or fresh validation collection

## Isolated change

D125's exact 84% fit-activity calibration produces three eligible controllers, but the inherited
lexicographic terminal selector chooses seed11902 on a `0.094` minimum-fold edge. That model is
inferior to seed11903 in proposal regret, mean, and family floor and has no feasible D124
development point. D126 changes only seed selection.

Reproduce the unchanged D119 models and D125 empirical activity thresholds, activating exactly
215 of 256 fit tasks. Retain all structural and fit-policy gates. Among eligible models, select the
lowest mean proposal regret; ties use higher within-ten coverage and then lower fixed seed. This
criterion is fixed because D117--D119 identified proposal ranking as the controller bottleneck,
not because of a fresh outcome. Require two complete fit-selection artifacts to be byte-identical.

## Conditional fresh validation

Only exact repeated selection opens untouched seeds `9,843,780--9,843,795`, 16 maps and 256
balanced tasks. Collect with the exact D112 binary, fixed q6 expert bank, and 20 workers. Score one
model/offset without refitting. Use D125 policy-evaluation mechanics: support, root count, and arm
count are descriptive because zero-boundary tasks are valid forced controls; every exact integrity,
failure, and 12 arms/s throughput gate remains mandatory.

The fixed policy gates are unchanged: mean at least `+2`, strict gains at least 40%, both folds
nonnegative, worst family at least `-3`, six positive families, directional score safety, activity
10%--85%, crop performance no worse than control, and worker-three reach within five percentage
points of control.

Mechanical corruption permits collector repair only. Policy failure closes D126 without tuning.
A full pass may emit a checkpoint and opens quantized Rust parity plus a separate untouched
confirmation. It does not by itself authorize integration, Arena, submission, or resident change.
