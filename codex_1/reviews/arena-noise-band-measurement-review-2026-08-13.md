# Independent review — Arena noise-band Phase 1

Date: 2026-08-13

Reviewer: `codex_1`

Integrated subject: `origin/main` at `ec5eb9f9`

Handoff artifact: `a890dfa94badf0e847eee78c4f87c66a927a5211`

## Verdict

**REVISION_REQUIRED — statistical interpretation only.** The registry repair, inputs,
arithmetic, confidence interval calculation, and reproducibility gates pass. One claim is not
supported by this design: `1.501` is not provably an upper bound on pure re-submission variance.

## Reproduced evidence

- `python3 cgauto/submission_history.py validate`: 53 observations validate cleanly.
- `python3 cgauto/arena_noise_band.py`: four families, 14 mature observations, 10 d.o.f.;
  pooled SD `1.501`; CI `[1.049, 2.634]`; single-run difference SD `2.123`; runs per arm
  `[5, 19, 51]` for target SE `[1.0, 0.5, 0.3]`.
- Independent calculation from the derived registry: pooled sum of squares
  `22.532333333333337`, SD `1.5010773908540938`, CI
  `[1.0488328981965016, 2.6342800287536168]`, difference SD
  `2.122844004317479`, runs `[5, 19, 51]`.
- `pytest -q tests/test_submission_history.py`: 47 passed.
- Runs 1–4 each have 160 finished, zero pending, `identity_clean=true`, no unexpected rows
  or fetch failures, and matching `arena` / `filtered_ladder` agent ids and scores. Run 2's
  deliberately selected `run2-checkpoint-initial.json` is substantively terminal and clean.

## Registry repair

Accepted. `cgauto/submission_history.py` now checks the identity of the `arena` block from which
score/rank/field size are consumed and honors a producer verdict of `identity_clean=false`.
The checkpoint producer defines clean identity by exact equality of both room and filtered ids
to the requested agent, so absent as well as mismatched identities are rejected at production.
The two regression tests cover the real stale-row incident and producer-verdict propagation.

## Required correction

The campaign is strictly sequential and ladder drift is unobserved separately. Drift can either
increase or decrease within-family dispersion depending on its direction, timing, and covariance
with deployment order. Therefore the observed pooled SD is neither an identified estimate of
pure re-submission variance nor a guaranteed upper bound on it.

Use wording such as:

> `1.501` estimates combined operational variability for sequential same-source deployments in
> the observed campaign. Pure re-submission variance and ladder drift are not separately
> identifiable from these data, and no inequality between them is established.

The runs-per-arm figures are arithmetically correct under independent, stationary observations
with variance `1.501²`. Present them as planning approximations, not guarantees. An interleaved
A/B design is still required to distribute drift across arms; persistent or autocorrelated drift
can prevent the nominal `1/sqrt(n)` improvement.

Locations requiring correction include `docs/STATE.md` §3 and the task record's final
confounding paragraph. The rest of the handoff is accepted.
