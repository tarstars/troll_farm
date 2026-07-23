# Opponent-crop candidate — Phase 21 controlled transfer execution, 2026-07-18

## Status

**Closed: do not promote the candidate; exact resident restored.**  The same-source capacity
control passed, but the candidate entered the predeclared extension band and arena scheduling
stopped at 160 games, short of the mandatory 180-game read.  Step 9 treats that as infrastructure
ambiguity.  Execution followed `opponent-crop-controlled-transfer-protocol-2026-07-18.md`.

## Frozen identities and preflight

| Role | Bytes | SHA-256 |
|---|---:|---|
| Exact resident/control | 62,725 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| Opponent-crop `b100_e6` candidate | 64,522 | `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19` |

Both artifacts compiled standalone.  Immediately before the first write,
`recover_live_source.py` recovered 62,725 bytes and verified the platform source as the exact
resident SHA above.  The candidate's `.sha256` sidecar also matched its bytes.  No source was
regenerated or edited after preflight.

## Same-source capacity control

The exact resident path was passed explicitly to `cgauto/api_submit.py`.  CodinGame accepted the
write through `TestSession/submit` as submission `41012256`; the authoritative room then exposed
new agent `6560240`.  This is a byte-identical resident reset, not a strategy change.

| Read | Finished games | Score | Rank | Catastrophic losses | Negative margin mass | Runtime/validity signals |
|---|---:|---:|---:|---:|---:|---:|
| Early audit, 19:20:54 UTC | 15 | 23.66 | 31/107 | 2/15 (13.3%) | 214 | 0 |
| Formal 60, 19:35:34 UTC | 60 | 24.45 | 23/107 | 13/60 (21.7%) | 3,677 | 0 |
| Formal 120+, 19:55:25 UTC | 122 | 24.83 | 18/107 | 21/122 (17.2%) | 6,113 | 0 |
| Delayed confirmation, 20:11:11 UTC | 160 | 24.77 | 18/107 | 31/160 (19.4%) | 9,195 | 0 |

All 60/60 formal-checkpoint results were fetched and parsed, every target agent record had
`valid=true`, and the submission/agent identity audit was clean.  The margins at or below -100
were ordinary valid losses, not execution failures.

The delayed read was 945.7 seconds and 38 games after the formal 120+ read.  All 160/160 results
parsed, score remained above 21.3, and the identity/runtime audit remained clean.  The frozen gate
evaluator returned `pass` with no reasons.

## Candidate trial

Immediately before the second write, the platform source was recovered again as the exact resident
SHA.  The frozen candidate recompiled and its sidecar still matched SHA
`6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`.
CodinGame accepted it as submission `41012399`; its battle stream identifies new agent `6560269`.

The 60-game checkpoint may reject only for a validity/runtime signal or score at least 1.5 below
the matched 24.45 control read.  It cannot promote early.  The formal 120-game score/tail gate and
delayed candidate confirmation remain pending.

| Candidate read | Finished games | Score | Rank | Catastrophic losses | Negative margin mass | Runtime/validity signals |
|---|---:|---:|---:|---:|---:|---:|
| Formal 60+, 20:28:53 UTC | 61 | 24.45 | 22/107 | 11/61 (18.0%) | 2,149 | 0 |
| Formal 120+, corrected audit, 20:50:12 UTC | 129 | 24.58 | 20/107 | 24/129 (18.6%) | 5,677 | 0 |

The early evaluator returned `continue` with no reasons.  Score delta against the 60-game control
was exactly 0.00; catastrophic rate was 3.63 percentage points lower and negative-margin mass was
58.4% of control.  Those tail figures are provisional and do not authorize early promotion.

The first 120+ audit initially found the word `timeout` in game `896285678`.  Raw replay inspection
showed candidate seat 0 valid and winning 114 to -2; all three timeout frames and the `$1 timeout`
tooltip belonged to opponent seat 1.  The collector had searched global tooltips, so it was fixed
to inspect only target-seat frames and target-addressed tooltips, and a regression test was added.
The corrected reproducible audit contains zero candidate runtime signals.

Against the 122-game control, the corrected candidate score delta is -0.25, catastrophic-rate gap
is +1.39 percentage points, and negative-margin mass ratio is 0.929.  All safety gates pass, but
the score is in the frozen `[-0.5, +0.8)` ambiguity interval.  The evaluator therefore returns
`extend-180`.  At the extended read, comparison uses the mature 160-game control confirmation:
candidate score must be at least 25.27 (+0.5), with a second final read at least 15 minutes later
also at least +0.5; the existing safety bounds remain mandatory.

| Extended/interim read | Finished games | Score | Rank | Catastrophic losses | Negative margin mass | Runtime/validity signals |
|---|---:|---:|---:|---:|---:|---:|
| Scheduling plateau, 21:06:03 UTC | 160 | 24.89 | 17/107 | 31/160 (19.4%) | 7,771 | 0 |

At matched 160-game count, control was 24.77 with the same 31 catastrophic losses and 9,195
negative-margin mass.  Candidate score was only +0.12, below the +0.5 extended bar, while negative
mass was 15.5% lower.  The platform then produced no additional game for more than 15 minutes and
showed zero pending games.  Prior A/A history also plateaued at exactly 160.  The required 180 read
was therefore unavailable; the rating threshold was not relaxed.

## Restoration and final status

The exact 62,725-byte resident was rehashed and recompiled, then submitted explicitly as
submission `41012593`.  CodinGame registered restored resident agent `6560289`; the platform source
was recovered at SHA `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
`cgauto/api_submit.py` remains resident-defaulted.

**Final Phase 21 decision: reject/close this exact arena transfer under infrastructure ambiguity.**
The live resident is exact.  Preserve the candidate's mechanism evidence for hypothesis generation,
but do not retune or resubmit `b100_e6` on these consumed games.

## Reproducible checkpoint tooling

`cgauto/arena_transfer_checkpoint.py` requires the expected agent and submission IDs, rejects a
mixed battle stream, fetches every finished result, and records the protocol's rating and safety
metrics.  Its focused tests are in `tests/test_arena_transfer_checkpoint.py`.
