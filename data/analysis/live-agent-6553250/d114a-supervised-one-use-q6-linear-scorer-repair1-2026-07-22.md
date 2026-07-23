# D114a repair 1 — nested arm key

Date: 2026-07-22  
Status: frozen after collection, before any ridge solve or validation metric

The first fitter invocation loaded the complete train panel and generated its backward labels, then
stopped with `KeyError` before constructing the target vector. The label dictionary used
`(seed, seat, opponent, boundary, slot)` while the common arm helper returns
`((seed, seat, opponent), boundary, slot)`. No ridge model, candidate score, validation metric,
admission result, or population was produced.

Repair exactly that key shape and change nothing in the frozen clips, alphas, offsets, weighting,
rounding, admission gates, tie-break, refit, held ranges, or decision rules. Preserve and hash the
already collected train/validation matrices in the repair manifest before rerunning the fitter.
