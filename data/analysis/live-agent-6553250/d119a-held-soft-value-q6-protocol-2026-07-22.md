# D119a locked held qualification — execution protocol

Date: 2026-07-22  
Status: frozen after validation selection and before any held collection

## Locked candidate

D119 validation admitted four of 24 prospectively frozen candidates. Its unchanged robust
selection order chose initialization seed `11901`, gate offset `0.0`, and canonical model hash
`a2a79d842732acf746225723754ebd3c54d7d95d3eefa43557c10f0f3002903f`. The evaluator must load
the exact 30,579-byte checkpoint selected by the validation artifact. There is no held-time model,
offset, threshold, family, or seed selection.

## Untouched held panel

Collect seeds `9,843,700--9,843,715`: 16 maps, both seats, all eight frozen opponents, and 256
tasks. Use the unchanged D112 exact dense collector with the frozen q6 expert population and 20
workers. The held lock must verify before evaluation. Mechanics require the complete prescribed
grid, zero provenance/accounting/direct-command failures, at least 90% supported tasks, at least
600 roots and 6,000 arms, at least 12 arms/s, exact paired/reward identities, and crop/workforce
fields.

## Single held decision

Evaluate only seed `11901` at gate offset `0.0`, with first-positive one-intervention semantics.
A pass requires all of:

- mean margin delta at least `+2`;
- strict improvement on at least 40% of tasks;
- worst opponent-family mean at least `-3`;
- at least six positive opponent families;
- nonnegative mean own-score delta or nonpositive mean opponent-score delta;
- intervention rate from 10% through 85%;
- crop creation on 100% of tasks; and
- worker-three reach no more than five percentage points below control.

A mechanics failure permits coverage repair only. A policy failure closes D119 without tuning on
held outcomes. A full pass opens quantized Rust parity/integration and a separately frozen final
untouched confirmation; it does not authorize TestSession, Arena, submission, or resident change.
