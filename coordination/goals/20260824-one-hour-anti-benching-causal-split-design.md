# One-Hour Goal: Isolate the Replant Option Before Another Cure

- **Date:** 2026-08-24
- **Author / intended executor:** `local_codex_1`
- **Time box:** 60 minutes from explicit activation
- **Scope:** read-only causal analysis and a design contract; no implementation or experiment

## Activation

The user activates this mission by naming this file. The hour begins when
`local_codex_1` accepts it, not when this file is committed.

On acceptance, sweep the `local_codex_1` inbox, verify the authoritative roster and remote
artifact pins, and publish a bounded claim for task
`20260824-anti-benching-causal-split-design`. Name the exact write set before starting.
The repository's 15-minute concrete-progress lease applies throughout the hour: every material
decision must become remotely inspectable within one lease, and the final memo must be committed,
pushed, and verified before it is called delivered.

This goal does not reprioritize unrelated project work or authorize another agent to edit the
same files. If an active claim overlaps the write set, stop and coordinate ownership first.

## Why This Hour Is Useful

The rejected anti-benching candidate produced **115 blocking games versus 35 for its exact base**.
That result is valid, and five direct command divergences violate the frozen rule that orchard-
eligible behavior must remain unchanged. The candidate remains rejected.

What caused the broader failure is not established. The rejected candidate combined at least four
mechanisms: preserving a replant `PICK` option, persistent regeneration commitment, duplicated or
reordered bank candidates, and joint pair selection. The 73 new long-stall labels also include a
future-dependent classification: in `m035` seat 0, the labelled interval ends at turn 99 while the
first candidate/base command divergence occurs at turn 100. The unrun progress gate means the
isolated replant option's benefit remains unknown.

The hour therefore separates the mechanisms on paper before anybody builds another combined cure.

## Mission

Produce one evidence-cited design memo with exactly one conclusion:

1. **`ISOLATABLE`:** the replant `PICK` can be specified as the only candidate-list difference,
   without persistent commitment, duplicate bank candidates, selector changes, or orchard-eligible
   command changes; or
2. **`NOT_ISOLATABLE`:** the pinned source semantics couple the replant option to one or more of
   those mechanisms. Name the smallest coupling that prevents a clean design and stop.

This is a design conclusion, not evidence that the option improves progress or score.

## Exact Evidence Pins

Read these exact artifacts; do not silently substitute newer files or working-tree copies:

1. `agent/chatgpt_1@a3d2b02a605800d147cc78b9995a7a3525b9e315:`
   `chatgpt_1/reviews/anti-benching-result-strategy-rereview-2026-08-23.md`
2. `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:`
   `claude_1/picker2/phase3-generator-route-2026-08-20.md`
3. `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:`
   `claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`
4. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:`
   `claude_1/picker2/candidate-door1-p1p2.rs`
5. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:`
   `claude_1/picker3/candidate-door1-p3b.rs`
6. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:`
   `claude_1/pipeline/fuzz_panel.py`, limited to `work_remaining`, `live_horizon`, and `eval_p4`
7. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:`
   `codex_1/reviews/pair-selector-phase3b-build-review-2026-08-23.md`
8. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:`
   `codex_1/picker3/results/gd-door1-panel-2026-08-23.md`
9. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:`
   `codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json`
10. `agent/local_codex_1@16b6e4ada72ab1381833162ed98e97ba930cd9b4:`
    `local_codex_1/reviews/pair-selector-gd-ge-unified-review-2026-08-23.md`

Also read the current `docs/STATE.md`, matching `docs/CONSTRAINTS.md` entries, and the tail of the
live ledger named by `docs/STATE.md` section 5 before making the design conclusion.

## Required Deliverable

Write:

`local_codex_1/reviews/anti-benching-causal-split-design-2026-08-24.md`

It must contain all of the following:

1. **Causal ledger.** One row each for the preserved replant option (Delta-A), persistent
   commitment, duplicated/reordered bank candidates (Delta-B), joint pair selection, the orchard-
   inertness check (P3), and the long-stall check (P4). Columns are exactly `observed`, `deduced`,
   `hypothesized`, and `missing evidence`.
2. **Option-only design contract.** Specify the single allowed candidate-list difference and the
   exact same-state preconditions for it. Explicitly forbid persistent commitment, duplicate bank
   rows, selector or score changes, unrelated candidate reordering, and command changes in
   orchard-eligible states. This is prose and pseudocode only, not a source patch.
3. **Decisive counterexamples.** Tabulate the five direct orchard-inertness failures—`m035`,
   `m065`, `m074`, `m104`, and `m114`, all seat 0—with their turn-100 commands. Include the
   `m035` long-stall interval ending at turn 99 before the first divergence at turn 100.
4. **Future measurement matrix.** For each still-open claim, name the smallest future measurement,
   control arm, population, output, and earliest falsifier. Label every row **unexecuted**.
5. **Stage order.** If and only if the option is isolatable, put a same-state candidate-list and
   selection proof before any panel run. Put a bounded cross-turn transaction behind demonstrated
   option-only progress. Put any change to P4 semantics in a separate evidence-tool charter that
   cannot waive the rejected candidate's result.
6. **Conclusion and limits.** State `ISOLATABLE` or `NOT_ISOLATABLE`; retain the accepted
   `RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN` verdict; state that progress, score, full-corpus value,
   and Arena readiness remain unmeasured.

Every causal statement must be labelled as observed, deduced, hypothesized, or unresolved. A code
reading may prove structural coupling; it may not prove behavior or value that was never measured.

## Suggested Hour

1. **Minutes 0–10:** verify pins, task ownership, sacred resident hash, and transport health.
2. **Minutes 10–25:** trace the candidate-list and commitment semantics; build the causal ledger.
3. **Minutes 25–40:** write and try to falsify the option-only design contract.
4. **Minutes 40–50:** record the five direct failures, the pre-divergence P4 counterexample, and
   the separate P4 evidence-tool boundary.
5. **Minutes 50–60:** write the unexecuted measurement matrix, validate citations and conclusion,
   publish the memo, and issue the coordination handoff.

## Authority and Boundaries

The executor may read pinned Git objects, inspect source semantics without editing them, run
read-only Git/hash/schema checks, and create the memo plus its own task/status/message artifacts.
As coordinator, `local_codex_1` may integrate those exact coordination and memo files after
validation.

The executor may not:

- implement or patch a candidate;
- run or regenerate the 240-game panel, the progress gate, a simulation, or a replay corpus;
- change P3, P4, any detector, grader, protocol, or frozen result;
- reinterpret the 73 P4 labels as 73 proved candidate-caused stalls;
- claim the replant option restores progress merely because it is legal or selected;
- edit or format `rust/src/bin/yamo_orchard_live.rs`, `rust/src/bin/`, or `cgauto/`;
- open sealed ranges, touch `data/raw/games/`, or write through bulk roots;
- start a TestSession, submit a bot, or touch Arena state; or
- assign implementation work to another agent from this goal alone.

This goal file never authorizes Arena writes.

## Stop and Fallback Rules

Stop with `NOT_ISOLATABLE` as soon as a pinned source dependency proves that Delta-A cannot be
specified without commitment or Delta-B. Do not repair the coupling during this hour.

If a pin is missing, inconsistent, or not reachable from the named canonical branch, publish the
exact blocker and stop. If the evidence does not establish a causal link, write `unresolved`; do
not fill the gap by inference. If an overlapping active claim exists, stop until ownership is
resolved.

If the hour expires before the memo is complete, publish a resumable progress marker containing
verified pins, completed sections, unresolved questions, and the exact next step. Partial work gets
no `ISOLATABLE` verdict.

## End Condition

The mission ends when the memo is committed and pushed on `agent/local_codex_1`, its exact commit
and path are recorded in a valid handoff, the coordination checks pass, and integration is either
verified or explicitly deferred. The closing report must give the design conclusion, the smallest
decisive evidence, the still-unmeasured claims, the proposed next gate without activating it, and
confirmation that no code, experiment, TestSession, submission, or Arena action occurred.
