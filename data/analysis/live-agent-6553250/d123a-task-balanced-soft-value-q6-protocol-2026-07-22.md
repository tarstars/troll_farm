# D123a task-balanced soft-value q6 — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen before D123 training or scoring

## Isolated hypothesis

D119 gives every decision root equal rank/gate loss. On its 16-map fit panel, `script_boss` supplies
251 roots and `resident` 229, while `mybot` supplies 73 and `legend_balanced` 89. Tasks with long
q6 opportunity sequences therefore dominate optimization. D123 changes only root loss weights so
every supported task contributes equal total loss across its roots.

Retain the 6,626-parameter factorized architecture, temperature-10 soft proposal targets, equal
rank/gate coefficients, 80 epochs, root batches of 128, Adam `1e-3`, weight decay `1e-4`, one
training thread, deterministic PCG64 shuffles, and offsets `{-1,-0.5,0,0.5,1,1.5}`. Use four fresh
initializations `12301--12304` and the original D114 16-map fit data only.

## Retrospective development audit

Score all 24 fixed candidates on the already-consumed D121 80-map panel. Crop safety is corrected
prospectively to `policy crop rate >= control crop rate`; every other held policy gate remains:
mean `+2`, strict 40%, floor `-3`, six positive families, directional score safety, activity
10%--85%, and relative workforce safety. Also require the unchanged D119 structural fit gates and
D118 fit-policy gates on training data.

Require two complete JSON artifacts to be byte-identical. A retrospectively eligible candidate
may justify freezing a fresh validation protocol, but the consumed panel cannot qualify the model,
serve as confirmation, or authorize integration/Arena/submission. If none is eligible, close the
task-balanced objective without buying simulation.
