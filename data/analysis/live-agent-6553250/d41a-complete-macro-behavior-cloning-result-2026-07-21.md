# D41a complete-macro behavior cloning — result (2026-07-21)

## Verdict

**Reject and close the independent `44 -> 32 -> 16 -> 1` candidate scorer before PPO.** None of
the three frozen model seeds passed teacher-forced validation, so closed-loop development was
correctly skipped. D40 remains the complete-policy teacher; this result does not reject its macro
environment or behavior.

The failure is now localized. A separate parameter-free decoder reconstructed D40's branchwise
lexicographic ordering using only the exported action IDs and 44 candidate features. It selected
the exact teacher action on **85,047/85,047** held-out decisions, including every decision in all
four branches. The observation contains the necessary information; an independently scored tiny
ReLU MLP is the wrong function class for the exact discontinuous ordering.

## Frozen execution and integrity

- Training consumed exactly 500,000 teacher decisions from the stream beginning at map 9,700,000.
- Seeds 401, 402, and 403 used the same stream, frozen optimizer, two-epoch chunks, and cosine
  schedule. End-to-end training and validation took 888.686 seconds.
- The two 4,096-decision candidate-feature streams had the identical SHA-256
  `306779511abd482bd0a102c9cb0949f4ff40e0180ea1895fc8cefc9c584ef4fd`.
- Every actor has the expected 1,985 parameters: 7,940 float32 bytes or 1,985 int8 bytes. All
  checkpoints and exported weight archives were written, but none is eligible for deployment.
- Rust/Python shape, legal-label, deterministic-feature, overflow, and direct-episode parity tests
  passed before the run. Eleven focused wrapper/trainer/diagnostic tests pass after it.

The authoritative training artifact is `d41a-macro-bc-result.json`, SHA-256
`9cb8905a75d408c71658068c6b09bb48937cc65e3e1307cea4e917849ae4b68d`.
The independent exact-prior diagnostic is
`d41a-exact-prior-diagnostic-2026-07-21.json`, SHA-256
`9e26a2e5f6b812192bbdb0b8cdd96d7a1e32f679a12790963933e5b59382323e`.

## Teacher-forced validation

The frozen floors were 99% overall accuracy, 97% in every branch, and 0.95 action-plane macro F1.

| Seed | Overall | TRAIN | Deficit | Evacuation | Rate | Plane macro F1 | Verdict |
|---:|---:|---:|---:|---:|---:|---:|---|
| 401 | 84.386% | 98.737% | 46.943% | 38.095% | 75.854% | 0.8580 | fail |
| 402 | 84.801% | 98.737% | 63.085% | 38.095% | 73.986% | 0.8579 | fail |
| 403 | 84.960% | 98.737% | 48.685% | 33.333% | 76.890% | 0.8581 | fail |

All three models miss every aggregate gate family. The rare evacuation branch is worst, but it is
not the whole problem: deficit and the high-volume rate branch also miss by large margins. The
similar outcome of three initializations makes an unlucky seed implausible. Per protocol, no model
was run closed-loop, no model was selected, and no kernel, confirmation, TestSession, submission,
or Arena action occurred.

## Exact-prior diagnosis

The diagnostic independently decodes integer ETA, reward rate, deficit reduction, job kind,
target, plant cell, turn, workforce, and action plane from each observation. It then applies the
already-frozen D40 keys:

1. deterministic TRAIN goal from deadline and workforce;
2. maximum positive deficit reduction, then ETA/bank/kind/target/plant ordering;
3. shortest non-idle evacuation with the same stable tie breaks; or
4. maximum D37 rate/provenance value, then ETA/kind/target ordering.

It never consumes `teacher_index` while selecting.

| Branch | Decisions | Exact matches | Accuracy | Plane accuracy |
|---|---:|---:|---:|---:|
| TRAIN | 40,531 | 40,531 | 100% | 100% |
| Deficit | 6,542 | 6,542 | 100% | 100% |
| Evacuation | 336 | 336 | 100% | 100% |
| Rate | 37,638 | 37,638 | 100% | 100% |
| **Overall** | **85,047** | **85,047** | **100%** | **100%** |

This separates three levels of explanation:

- **Data/observation:** sufficient. There is no hidden-state or missing-feature excuse on the held-out
  teacher trajectory.
- **Function class:** failed. A shared continuous scalar approximator must learn conditional
  integer comparisons, priority filters, and stable tuple ordering from examples. Its 85% plateau
  is structural enough that more seeds or the same model with more rows is low-value.
- **Strategic behavior:** still untested for the learned models. Their validation failure prevented
  autoregressive errors from contaminating the conclusion. D40's +32.027 development-independent
  teacher margin and complete workforce result remain the active behavioral anchor.

## Decision and next experiment

Do not retune learning rate, epochs, model seed, or width, and do not run PPO from any D41a
checkpoint. Replace imitation of the exact ordering with an **exact-prior residual actor**:

1. compute D40's candidate ordering deterministically at runtime;
2. initialize a compact residual scorer at exactly zero so deterministic action selection is D40;
3. verify exact closed-loop reproduction on the already-frozen development grid, including terminal
   action/state hashes and an independent repeat; and
4. only after that preflight, freeze a separate outcome-optimized PPO protocol in which finite
   prior-rank logits provide conservative exploration and the residual learns deviations.

This is a new actor representation, not a reopened D41a model. It removes behavior cloning as a
lossy compression step while retaining a small trainable policy surface.
