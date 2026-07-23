# D134a mechanics repair 1

Date: 2026-07-22  
Boundary: after the first `select-a` invocation stopped while loading block 2 and before any D134 model fit

The D134 loader inherited `panel["mechanics"]["pass"]` from D114. That aggregate still includes
`supported_tasks_at_least_90pct`, the one availability predicate removed prospectively by D133b.
Consequently block 2 stopped D134 even though every nonavailability mechanics gate passes and D133b
explicitly authorized D134.

Repair: D134 now calls D133b's locked `exact_mechanics_without_support_gate` helper and requires its
aggregate pass. No corpus row, feature, label, model, optimizer, seed, calibration target, selection
gate, veto gate, or final-validation boundary changed. A regression test proves that the removed
support predicate may fail while any other mechanics failure still stops D134.
