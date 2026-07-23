# Opponent-crop candidate — Phase 21 controlled arena protocol, draft 2026-07-18

## Status and authorization

**Draft only. Do not execute without explicit user authorization.** Submitting either source
creates a new arena agent and changes external state. This document does not authorize that write.
It does not change `cgauto/api_submit.py`.

Current read-only snapshot: restored resident agent `6559583`, rank 45/107 in Legend, score 22.1,
with 162 listed completed games. Exact resident source is 62,725 bytes, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.

Frozen candidate:
`cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs`, 64,522 bytes,
SHA-256 `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`.
No parameter or source regeneration is allowed after the first arena write.

## Why a fresh control is mandatory

Arena capacity and opponent mix have varied during this project. A candidate reset cannot be
compared safely with the incumbent's historical score alone. Submit the byte-identical resident
first, allow a fresh control to converge, and proceed only if capacity is healthy. If capacity
fails, the active code is still the resident and the protocol stops safely.

## Fixed sequence

1. Reverify both hashes, standalone compilation, current saved-source hash, and candidate sidecar.
2. Submit the exact resident explicitly as a same-source capacity control; do not use the default
   helper implicitly.
3. Observe at 60 and 120 completed games. Fetch every control result read-only and audit invalid,
   timeout, runtime-error, margin-at-most--100 frequency, and total negative-margin mass.
4. Capacity passes only if the 120-game score is at least 21.3, no validity/runtime signal appears,
   and a second read at least 15 minutes later shows at least 20 additional completed games with
   score still at least 21.3. Otherwise stop with the resident active.
5. Submit the frozen candidate exactly once.
6. At 60 games, reject early only for a validity/runtime signal or score at least 1.5 below the
   matched control checkpoint. Never promote at the early read.
7. At 120 games, promote only if candidate score is at least 0.8 above the control's matched
   checkpoint, candidate score is at least 22.1, catastrophic-loss rate is no more than two
   percentage points above control, and total negative-margin mass is no more than 10% above
   control. Confirm score on a second read at least 15 minutes later.
8. If score difference is between -0.5 and +0.8 with all safety gates clean, extend both comparison
   interpretation and candidate observation to 180 games; promote only at at least +0.5 on both
   final reads. Any result below -0.5 rejects.
9. On rejection or infrastructure ambiguity, explicitly restore the exact resident and verify its
   source hash. On promotion, update documentation first; changing the submit default remains a
   separate explicit action.

## Interpretation

Generated-map paired effects and official-state activations are prerequisites, not arena outcome
evidence. The same-source control is the arena capacity discriminator. Do not tune thresholds,
crop logic, or source after seeing any control or candidate result; a failure closes this exact
`b100_e6` transfer attempt.
