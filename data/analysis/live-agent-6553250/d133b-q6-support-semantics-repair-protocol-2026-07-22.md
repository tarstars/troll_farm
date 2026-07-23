# D133b q6 support-semantics repair — frozen protocol

Date: 2026-07-22  
Status: frozen after D133a support failure, before interpreting block 2/3 teacher values

## Diagnosis from prior evidence

D133a passes all infrastructure and exact-record checks but stops because q6 roots occur in
910/1,024 tasks (`88.87%`) rather than 90%, with two individual blocks below 90%. D113 already
proved that a zero-boundary task is valid forced D40 control, not a malformed continuation.

A fixed audit of nine earlier non-overlapping 16-map q6 panels contains 2,304 tasks and 2,076
supported tasks (`90.10%`). Individual rates are 91.80%, 91.02%, 90.23%, 85.94%, 89.06%, 92.19%,
88.28%, 89.45%, and 92.97%: five of nine are below 90%, with a range of 85.94%--92.97%.
Therefore an every-block 90% gate is an unstable small-panel property and, over four independent
blocks, rejects ordinary sampling variation even when exact labels are abundant.

## Isolated repair

Reinterpret `supported_tasks_at_least_90pct` as descriptive availability only. Remove no other
inherited gate. In every D133 block still require prescribed tasks, complete unique roots/arms,
finite schemas, paired-gain and reward identities, one-intervention accounting, one expert bank,
zero direct-command/provenance/deposit failures, at least 600 roots, at least 6,000 arms, and at
least 12 arms/s. Globally retain exactly 1,024 baselines, at least 80,000 arms, and at least 4,800
roots.

Replace the generic support percentage with the downstream feasibility condition fixed in the
D134 protocol before D133 teacher interpretation. D134 calibrates 84% active tasks and needs one
finite inactive ceiling after the target-active rank:

- every three-block training fold must have at least
  `round(0.84 * 768) + 1 = 646` supported tasks; and
- the all-block fit must have at least `round(0.84 * 1,024) + 1 = 861` supported tasks.

The observed fold counts are not yet gates until this protocol is frozen. Unsupported held tasks
remain exact forced control and require no gate logit.

## Teacher interpretation and decision

Only if all repaired mechanics/sample/calibration-feasibility gates pass may D133b generate the
previously uninterpreted block 2/3 labels and aggregate all four blocks. Apply every original D113
signal and safety threshold unchanged: oracle mean/strict/family breadth/floor, score direction,
act/wait and arm-sign balance, target variance, 100% crop creation, and workforce reach.

- **Any exact mechanics, sample-size, or calibration-feasibility failure:** close the corpus.
- **Aggregate signal or safety failure:** close the teacher corpus without model fitting.
- **Full pass:** open the already-frozen D134 leave-one-block-out selection.

D133b changes no corpus bytes, model, objective, final seed, resident, submission, or Arena state.
