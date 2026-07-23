# D134a block-transfer-selected soft-value q6 — result

Date: 2026-07-22  
Decision: **close unchanged D119 abstraction on consumed-panel veto**

## Execution integrity

The first selection invocation stopped before any fit because the inherited D114 aggregate still
contained D133b's removed support-percentage predicate. Mechanics repair 1 changed only that
inheritance, retained every nonavailability mechanics gate, added a regression test, and was
re-locked before training.

Selection A and B each completed 16 deterministic 80-epoch fits in 120.28 and 123.79 seconds.
Their complete 81,010-byte JSON artifacts are byte-identical (SHA `d80ceb3f...`). Peak resident
memory was 1.91 GB. The full fit plus consumed-panel veto took 23.68 seconds and peaked at 2.00 GB.

## Leave-one-block-out result

Three of four fixed seeds pass every held-block gate. Seed 13403 wins the frozen lexicographic
selector:

- pooled mean `+3.132`, strict gains 45.31%, and activity 83.59%;
- block means `+3.457`, `+0.813`, `+2.055`, and `+6.203`;
- all eight opponent families positive, with family floor `+0.773`;
- crop rate 100% and worker-three reach exactly at the 89.26% control rate.

Seed 13401 and 13404 also qualify. Seed 13402 alone fails because one block is `-0.137`.
This is positive evidence that independent-block selection is materially more stable than D131's
single-panel fit-regret selector.

## Full fit and D126 veto

The selected full-corpus model hash is `3d019f01...`; training calibration activates 860/1,024
tasks (83.98%). On consumed seeds `9,843,780--9,843,795` it obtains:

- mean `+1.020` (fails required `+2`) and strict gains 42.97% (passes);
- fold means `+0.883` and `+1.156` (both pass);
- four positive families (fails six), with floor `-1.750` (passes);
- own delta `+0.582`, opponent delta `-0.438`, crop 100%, and worker-three parity (pass); and
- activity 89.06% (fails the 85% ceiling).

Thus three of nine veto gates fail. No checkpoint is emitted, untouched final seeds
`9,843,800--9,843,815` remain closed, and there is no Rust, submission, resident, TestSession, or
Arena mutation. Result SHA is `2620d164...`; lock SHA is `d0a3b798...`.

## Interpretation and next hypothesis

More independent data repaired seed selection but did not make the state-only gate transfer its
absolute activation rate or suppress enough low-value winners. The ranker still produces a chosen
proposal, yet the gate sees only 64 state features; it cannot condition the act/wait decision on
the identity, predicted value, or confidence of that winner. The next isolated test should retain
the ranker and first-positive runtime semantics but train a winner-conditioned gate from state plus
the selected proposal representation and rank-confidence summaries. Use D133 leave-one-block-out
selection and consumed D126 veto again; do not collect new maps or open final validation.
