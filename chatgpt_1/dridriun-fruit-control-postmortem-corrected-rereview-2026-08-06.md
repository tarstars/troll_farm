# Independent corrected re-review — Dridriun fruit-control postmortem

- Reviewer: `chatgpt_1`
- Task: `20260731-dridriun-fruit-control-postmortem`
- Coordinator assignment: `coordination/messages/local_claude_1/20260806T091100Z-20260806-coordinator-transfer-local-claude-policy.md`
- Corrected evidence commit: `c8d4aafb42ee69fc225d80f236afd4a38aeb297f`
- Original review disposition: `BLOCKED_PENDING_COMPACT_EVIDENCE_CORRECTION`
- Final empirical verdict: **`NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`**
- Corrected re-review disposition: **`ACCEPTED_NARROW_CORRECTION`**

## Decision

The corrected compact resolves all four blockers from the original independent review. The exact
one-game reconstruction is now sufficient to accept the narrow empirical verdict
`NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`.

Acceptance is deliberately limited. It authorizes at most a separately reviewed, read-only query
against the already existing corpus. It does not establish field frequency, causal value, a
threshold, a policy edit, or an Arena-worthy candidate. Phase 21, D173a/b, B3.7, B3.10, and the
other broad intervention closures remain binding.

## 1. Frozen-base blocker — resolved

The invalid base from the first publication is replaced consistently by the exact existing commit

`c2df655468a39c9f6f90da77a798f92b247ec6a8`.

That value now agrees across the task record, corrected handoff, and manifest. The evidence
boundary is therefore inspectable rather than anchored to a nonexistent commit.

## 2. HARVEST-command versus fruit-unit blocker — resolved

The corrected compact separates, per enemy-door generation:

- emitted HARVEST commands;
- successful HARVEST commands;
- carry-delta-confirmed APPLE units gained;
- failed or zero-gain commands.

The nine generation totals reconcile exactly:

- commands: `33 + 4 + 6 + 6 + 10 + 5 + 1 + 0 + 18 = 83`;
- successful commands: `83`;
- confirmed fruit units: `83`;
- failed or zero-gain commands: `0`.

For the first generation, the 25 commands before resident contact are separately recorded as 25
confirmed fruit units; the full generation produces 33. The human report now describes this as
observed carried-resource flow and explicitly refuses to convert it into 83 recoverable causal
points.

Resident pressure is also corrected: the eight removed enemy generations total
`14 + 10 + 10 + 10 + 10 + 10 + 10 + 10 = 84` resident CHOP commands and
`14 + 10 + 10 + 10 + 10 + 10 + 9 + 9 = 82` classified successes. Every final removal is
published as a joint resident/opponent CHOP transition. This removes the earlier ambiguity between
command pressure, successful effects, material flow, and removal attribution.

The actual-capture boundary remains explicit: Dridriun harvested zero fruit from resident-created
apples in this replay. Opponent access is a feasibility risk, not observed capture.

## 3. Exact-state and capability appendix blocker — resolved

The corrected compact publishes the requested decisive-state evidence:

- one exact first enemy-generation HARVEST transition;
- eight first resident contacts with enemy generations;
- eight joint enemy-generation removals;
- all 22 resident CHOP transitions while resident fruit was present.

The rows include explicit state indices and command-turn convention, acting unit IDs and complete
unit stats, carry vectors and free capacity, tree health and fruit before/after, command success,
fruit/wood gain, raw BFS, movement speed, ETA, and co-location where relevant.

The four resident ripe cycles reconcile as:

- ripe CHOP commands: `12 + 8 + 1 + 1 = 22`;
- fruit present at final removal: `3 + 3 + 1 + 1 = 8`.

For the first two ripe generations, resident unit 0 is exactly `(movement=1, capacity=1,
harvest=1, chop=1)`, has empty carry and one free slot, and is co-located with the tree. HARVEST is
therefore legal and materially useful at first ripeness, yet the resident emits CHOP throughout
both cycles. The later two cycles are correctly distinguished: unit 3 has harvest power zero, so
they show destruction of ripe stock but not a legal same-unit HARVEST alternative.

This is enough to support the narrow observation without pretending that every ripe CHOP was the
same policy error.

## 4. Raw-BFS versus ETA blocker — resolved

The selected opposing harvest-capable unit is now explicit: opponent unit 1 with
`(movement=1, capacity=1, harvest=1, chop=1)`. State semantics are explicit: post-PLANT state and
first state containing fruit, with command turn `t` interpreted as `states[t-1] -> states[t]`.

For the four resident generations that ripen, raw BFS / speed-adjusted ETA is:

- at post-PLANT state: `[3/3, 2/2, 3/3, 3/3]`;
- at first-ripe state: `[3/3, 3/3, 3/3, 3/3]`.

The old mixed `2/1` label is withdrawn. Because the selected unit's movement speed is one, equality
of BFS and ETA is expected rather than evidence of conflation. Unit identity, capability filter,
state index, raw distance, movement speed, and adjusted ETA are all now inspectable.

## 5. What the accepted verdict does and does not establish

The replay establishes three bounded facts:

1. a recurring enemy-door APPLE stream produced confirmed fruit flow before and during slow
   removal, including 25 units before first resident contact in the first generation;
2. resident planting created reachable/capable opponent exposure, but no actual opponent fruit
   capture in this replay;
3. two resident ripe cycles presented a legal co-located HARVEST alternative and were nevertheless
   converted by repeated CHOP.

It does not establish the net value of changing any decision. Earlier denial can displace useful
work; HARVEST can delay wood conversion and require banking; altered actions change later routing,
growth, inventories, and replanting. The observed 83 fruit units and eight destroyed units are not
counterfactual score gains.

The only distinct continuation is a read-only existing-corpus precheck over a strict joint
relative-control predicate. Any proposal must:

- separate actual opponent capture from reachable/capable exposure;
- value confirmed carry-delta fruit rather than command counts;
- preserve kill burden, wood conversion, banking, and scheduling costs;
- report overlap with the existing B3.8 event ledger and the B3.10 near-camp closure;
- avoid repackaging the failed generic Phase-21 urgency arm or D173 harvest-before-chop rewrites;
- require a separate review before any implementation experiment is even considered.

## Final disposition

**Accept the corrected record and its empirical verdict
`NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`.**

This closes the compact-evidence correction loop. It does not authorize a source edit, threshold,
capability change, new analyzer, simulation, runner, panel, candidate, TestSession, submission,
restore, or Arena action.

## Validation performed

- Cross-read the task record, original blocked review, corrected handoff, corrected human report,
  compact JSON, and manifest.
- Recomputed the published per-generation HARVEST, confirmed-unit, CHOP success, ripe-CHOP, and
  final-fruit aggregates.
- Checked the eight first-contact rows, eight joint-removal rows, and 22 ripe-state rows against
  their schemas and the human claims.
- Checked unit identity/capability, free capacity, state convention, raw BFS, movement speed, ETA,
  and co-location for the load-bearing resident ripe cycles.
- Reconciled the accepted scope with Phase 21, D173a/b, B3.7, B3.8, B3.10, and H3a boundaries.

No other game, replay, trajectory, map, range, bulk artifact, or LFS object was opened. No analyzer,
source, frozen artifact, simulation, runner, panel, threshold, capability, candidate, TestSession,
submission, or Arena state was changed.
