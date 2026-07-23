# D138a best-stop +3pp calibration q6 — result

Date: 2026-07-22  
Decision: **close D138 on consumed-panel veto; stop tuning the four-block corpus**

Two complete selections are byte-identical (SHA `a6bf7052...`). Adding exactly 23 active training
tasks per fold makes two pairs eligible. Family-floor-first selection chooses 13401/13701 with
`+3.688`, 40.33% strict gains, every block positive, all eight families positive, `+0.281` family
floor, and 71.88% activity.

The full fit has 688 exact positive-stop tasks, adds the frozen 31-task guardband, and calibrates
719/1,024 D133 tasks (70.21%). D126 activity is 70.31%, proving the calibration and task-level
activation rate transfer almost exactly. Policy value does not:

- mean `+0.645` and strict gains 32.81%;
- folds `+1.203` and `+0.086`;
- four positive families and floor `-5.875` (`compact_gold`);
- own delta `-0.191`, opponent delta `-0.836`, crop 100%, and workforce parity.

Mean, strict, family breadth, and family floor fail; no checkpoint or final-validation authority is
emitted. The D126 task-choice accuracy is 23.53% and balanced act/wait accuracy 45.05%.

This separates threshold transfer from representation/evidence transfer. D134--D138 repeatedly
produce clean four-block held results that do not predict D126 family outcomes; D136 already found
held mean correlation `r=0.004`. Another model seed, threshold, or small loss adjustment on the same
64 maps is unlikely to be informative.

Next double independent evidence before model work. Collect a second 64-map q6 corpus on unused
seeds `9,844,064--9,844,127` as four more 16-map blocks through the byte-validated D132/D133 YT
backend at `//home/delivery_ml/research/tarstars/troll_farm`. Keep D126 veto-only and final seeds
untouched. Result SHA is `99a52e73...`; lock SHA is `c3a6b1fd...`.
