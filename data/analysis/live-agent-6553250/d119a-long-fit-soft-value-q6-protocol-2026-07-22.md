# D119a long-fit soft-value q6 ranker — frozen protocol

Date: 2026-07-22  
Status: frozen before D119 fit-only training or validation collection

## Isolated hypothesis

D118's value-aware factorized model produces multiple fit policies above `+3`, but its best mean
proposal regret (`18.213`) and within-ten rate (43.39%) narrowly miss frozen gates of 18 and 45%.
Soft rank cross-entropy is still descending at epoch 40. D119 changes only training horizon from 40
to 80 epochs.

Retain exactly:

- the 6,626-parameter `379 -> 16 -> 1` proposal ranker plus `64 -> 8 -> 1` state gate;
- temperature-10 soft value targets and equal rank-CE/gate-BCE coefficients;
- D114 fit-only roots, root batches of 128, Adam `1e-3`, weight decay `1e-4`;
- one CPU training thread, deterministic PCG64 shuffles, and no schedule/early stop;
- four fresh initialization seeds `11901--11904`;
- gate offsets `{-1.0, -0.5, 0.0, 0.5, 1.0, 1.5}`; and
- first-positive one-intervention runtime semantics.

Require two complete fit artifacts to be byte-identical.

## Unchanged fit gate

At least one model/offset must have mean proposal regret at most 18, within-ten rate at least 45%,
gate balanced accuracy at least 60%, and both gate recalls at least 50%; its fit policy must have
mean at least `+3`, strict at least 30%, both folds nonnegative, worst family at least `-3`, at
least six positive families, activity 10%--85%, crops 100%, and worker-three reach within five
percentage points of D40. Do not lower a gate or add an epoch after observing D119.

## Conditional validation and held

Only an exact repeated fit pass authorizes freezing model hashes and collecting still-unused
validation seeds `9,843,670--9,843,685` (16 maps, both seats, eight opponents, 256 tasks). Require
the unchanged exact collector, zero failures, 90% support, 600 roots / 6,000 arms, and 12 arms/s.
Evaluate all 24 candidates without refitting.

Validation gates and selection order remain identical to D118: mean `+2`, strict 30%, both folds
nonnegative, floor `-5`, five positive families, directional score safety, activity 10%--85%, crop
and workforce safety; select by minimum fold, floor, mean, strict, lower activity, fixed order.

Only full validation admission can open held seeds `9,843,700--9,843,715`, under unchanged held
gates and a separately frozen evaluator. A full held pass opens quantized Rust parity/integration
and final untouched confirmation, not automatic submission.

No branch authorizes TestSession, Arena, submission, or resident mutation.
