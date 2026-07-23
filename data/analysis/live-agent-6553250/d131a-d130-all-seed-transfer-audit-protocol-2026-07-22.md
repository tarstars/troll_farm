# D131a D130 all-seed transfer audit — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen after D130 failure and before any unselected D130 development score

Reproduce D130 seeds `13001--13004` under the exact locked coefficient-1 cross-sign pairwise
objective. Verify every model hash, training metric, fit gate, and D125-calibrated offset against
the D130 result. Score each fixed seed exactly once at its own frozen training-calibrated offset on
the already-consumed D126 panel. Do not scan offsets, coefficients, margins, epochs, seeds, widths,
or objectives.

Report each seed's unchanged D126 gates and Pearson correlations for fit mean, fit family floor,
proposal regret, pair accuracy, and positive-winner rate versus development mean/floor. Also report
whether any unselected seed descriptively passes all gates.

D131 is diagnosis only. It cannot select or qualify a controller, emit a checkpoint, open fresh
seeds, start Rust integration, or trigger platform interaction. Require two complete result
artifacts to be byte-identical.
