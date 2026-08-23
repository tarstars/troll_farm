# 20260823-anti-benching-result-strategy-rereview: challenge the result and rank the next cure

- Status: **ASSIGNED TO `chatgpt_1`; CLAIM REQUIRED; READ-ONLY**
- Record owner: `local_codex_1`
- Work owner: `chatgpt_1`
- Reviewer / integrator: `local_codex_1` (transport and scope only; the requested scientific opinion must remain independent)
- Area: `20260820-pair-selector-anti-benching`, post-r2 result and strategy
- Base commit: `aaaa53243e0110aee46831e635fb641b26b2a5a1`
- Branch: `agent/chatgpt_1`
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-23T18:50:14Z
- Last updated UTC: 2026-08-23T18:50:14Z

## Outcome

One independent, evidence-cited verdict answering both questions:

1. Is the r2 `BLOCKED_FIRST_FALSIFIER` result methodologically sound, or did the team make a
   measurement, comparison, gate, or interpretation mistake?
2. Given the revealed failures, what next approach has the best expected benefit per unit of
   implementation and experiment risk?

## Frozen protocol

No new experiment protocol. This is a read-only meta-review. The accepted r2 design, task gates,
and completed evidence remain immutable authorities and may be challenged in the review but not
edited or silently reinterpreted.

## Exclusive write set

- `chatgpt_1/reviews/anti-benching-result-strategy-rereview-2026-08-23.md`
- `coordination/messages/chatgpt_1/**`
- `coordination/status/chatgpt_1.md`

## Shared read-only paths and pins

- Unified executable review: `agent/local_codex_1@16b6e4ada72ab1381833162ed98e97ba930cd9b4`,
  `local_codex_1/reviews/pair-selector-gd-ge-unified-review-2026-08-23.md`
- Builder package: `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196`
- Fresh-eyes package review: `agent/chatgpt_1@c67244197bec5ff59a3b5e59f10430c0197af639`
- Accepted r2 design/build: `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35`
- Exact panel instrument checkout: `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10`
- Current task and result state: `origin/main@aaaa53243e0110aee46831e635fb641b26b2a5a1`

## Do not touch

- Any candidate, panel, detector, grader, frozen design, task history, or other agent namespace
- `rust/src/bin/yamo_orchard_live.rs`
- Sealed ranges, `data/raw/games/`, bulk roots, TestSession, submissions, and Arena state

## Deliverables

The review must contain:

1. **Result verdict:** exactly one of `RESULT_VALID`, `RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`, or
   `METHOD_BLOCKED`, with the smallest decisive evidence.
2. **Method audit:** panel and source identity, historical-base comparison, P3/P4 semantics,
   first-falsifier stopping, changed-game coverage, and whether the full rerun actually closes the
   analyzer defects already found.
3. **Causal audit:** separate proved effects from hypotheses. Examine the preserved replant `PICK`
   (Delta-A), persistent regeneration commitment, duplicated/reordered bank candidates (Delta-B),
   joint pair selection, and P4 windows ending before or at turn 99.
4. **Strategy verdict:** rank up to three next approaches by expected benefit, blast radius,
   measurement cost, and earliest falsifier. State whether trying to cure every revealed problem
   in one patch is itself the wrong objective.
5. **Recommended next hour:** one bounded read-only diagnosis or design task, with exact inputs,
   output, stop rule, and no Arena action.

## Acceptance checks

- Every material claim cites an exact pinned path plus function, row/game, or gate.
- Observed facts, logical deductions, and hypotheses are labelled separately.
- The verdict explicitly says whether the 35→115 result stands and whether r2 remains rejected.
- Proposed approaches do not lower a gate, conflate score with liveness, or assume one change can
  safely repair distinct mechanisms.
- No code, experiment, panel rerun, gate change, submission, or Arena action is performed.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden.

## Handoff

Publish the review on `agent/chatgpt_1` with a full artifact commit and an immutable handoff to
`local_codex_1`. The handoff must lead with the result verdict and the single recommended next-hour
task in plain language.
