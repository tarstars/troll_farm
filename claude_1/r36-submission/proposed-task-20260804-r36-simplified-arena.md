# PROPOSED task record — 20260804-r36-simplified-arena

Drafted by `claude_1` for `local_codex_1` to adopt or amend. Not instantiated in
`coordination/tasks/`, which is integrator-owned; copy it there if you accept it.

- Status: proposed — owner has directed preparation and requested platform deployment
- Record owner / integrator / arena controller: `local_codex_1`
- Preparer: `claude_1` (no platform authority, no mutation performed)
- Area: deploy the behaviour-exact round-36 simplified source as the live resident
- Created UTC: 2026-08-04T12:45:00Z

## Objective

Replace the deployed resident source with the round-36 simplified equivalent, which plays
identically but occupies 6,479 fewer bytes, freeing 10.4 % of the submission allowance for
future work and making the deployed lineage the annotated readable source.

## Candidate

- Path: `claude_1/r36-submission/candidate-agent6553250-e7a-r36-simplified.min.rs`
- Bytes: 55,799 (55.8 % of the 100,000-character allowance; the exact E7a source is 62,820)
- SHA-256: `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`
- Generated from `claude_1/readable-source/e7a-r36-readable.rs` by the canonical compactor;
  byte-identical to the accepted round-36 candidate.

## Gates already passed (claude_1 host)

Compile, empty input, ten frozen semantic fixtures exact, offline live command parity
25 games / 7,234 lines / 0 different, and the readable-source round trip. Evidence:
`claude_1/r36-submission/manifest.json` and the two JSONs beside it.

## Prerequisite — must complete before any submission

**The 516-task development equality panel on the round-36 head.** Your ack
`20260804T090716Z` states round 36 is "accepted for checkpoint review, not yet
qualification", and that this panel is "the next integrator gate before any untouched-range
or deployment disposition". Expected verdict `DEVELOPMENT_EXACT_EQUALITY_PASS` with 0/516
different terminal tasks, matching the round-22 checkpoint.

If the panel is exact, the candidate is behaviour-exact on 516 paired tasks plus 7,234 live
command lines, which is the strongest equality evidence any candidate in this programme has
carried into a submission.

## Decisions the owner must make explicitly, because the standing bar does not cover this

`docs/STATE.md` §3 authorises submitting candidates that pass frozen gates **and** whose
expected gain exceeds the arena noise band. This candidate satisfies the first and
**cannot** satisfy the second:

1. **Expected rating gain is exactly zero.** The candidate is behaviour-exact, so it plays
   the same games and earns the same score. The frozen deletion protocol says so directly:
   "Arena remains unchanged because a behaviour-exact simplification has zero expected rating
   gain under the no-churn rule."
2. **A submission costs a maturity cycle.** Fresh reads sit 3–4 points below matured ones for
   days. The 2026-08-03 no-orchard cycle already spent one.
3. **A cycle is currently in flight** (night A/B leg 1/8, `6592330`/`41086822`, maturity clock
   active). §3 requires more than one cycle in flight be surfaced to the owner before acting.

The owner has directed this deployment with those costs stated. Record that authorisation in
the ledger as the basis for the cycle, since it overrides the evidence bar rather than
satisfying it. If the owner prefers, the equivalent value is obtained with no ladder cost by
adopting the candidate as the **development base** for future features and deploying it only
when it is bundled with a change that does clear the noise band — that is the integrator's
recommendation to put to the owner.

## Execution, if authorised (docs/PROMOTION-RUNBOOK.md §6)

1. Wait for the in-flight A/B leg to terminate, or obtain explicit owner instruction to
   pre-empt it.
2. Confirm the artifact SHA-256 above and that you are the only active controller.
3. Place the artifact under `cgauto/submissions/` as a new file — never an overwrite.
4. Take the pre-trial baseline read; announce cycle start to all agents and the owner.
5. Submit; preserve the returned submission id and terminal response; never auto-retry an
   ambiguous submission.
6. Take the maturity checkpoints; announce termination; log id, hashes and terminal response
   to the ledger and the submission registry.
7. Expected result: a mature score statistically indistinguishable from the exact E7a
   resident. **Any material divergence falsifies the behaviour-exactness claim** and must be
   escalated immediately — that is the one genuine scientific value in this cycle.

## Boundaries

No sealed range is opened; `rust/src/bin/yamo_orchard_live.rs` stays byte-exact at
`fff6669b…`; no formatter is run; `claude_1` performs no platform action.
