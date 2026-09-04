# chatgpt_1 status

- Updated UTC: 2026-09-04T13:01:37Z
- Branch: `agent/chatgpt_1`
- Identity: original `chatgpt_1` — opening-solver review, DP oracle, Rust anytime planner
- Current task: `20260904-start-game-optimizer-build`, owner-requested next-step judgement
- State: judgement complete; artifact publication and handoff in progress

## Judgement

Close the failed current build card. The accepted design remains viable, but the candidate cannot be patched after its pre-registered 19/24 mechanics result.

The single next experiment should be an **offline paired champion-prefix orchard-only oracle**:

- unchanged champion through its own second troll;
- no custom early-second prelude;
- third training disabled;
- search a small near orchard with `NO_PLANT` legal;
- exact candidate-versus-shadow-champion continuation to turn 300 under common opponent scenarios;
- progress deadlines as an execution guard, not as a substitute for economic comparison.

Working rating prior: about +2.5, wide range 0 to +4 and explicitly uncalibrated. Falsify on non-positive paired final-margin lower bound, negative own-score lower bound, predominant no-plant selection, high-raid reversal, any change to the champion's second-troll opening, or wood forecast outside the adopted calibration bound.

## Diagnosis correction

chatgpt_2's prelude finding strengthens but does not replace the blocker diagnosis. The turn-35 fallback is the same class of irreversible roster change handed to an unvalidated continuation. It does not explain every inactivity alarm; the planting schedule and missing progress certificate still matter. The harness `stalled` flag is a relative inactivity alarm, not a crash or automatic loss label.

## Measurement ruling

A 2.19-point range over five identical champion readings means one-hour single readings cannot resolve most small changes. It is not an irreducible floor: repeated interleaved readings can improve precision, while exact paired simulation can resolve small score mechanisms but cannot calibrate ladder rating. Reserve ladder work for candidates with a plausible effect above roughly 2.2 rating points.

## Boundary

Judgement only. No bot, panel, holdout, ladder, platform, Arena, cluster, champion or `main` action was taken.
