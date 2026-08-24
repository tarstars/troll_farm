# One-Hour Goal: Anti-Benching Reach Ruling

- **Date:** 2026-08-23
- **Author / intended executor:** `local_codex_1`
- **Time box:** 60 minutes from explicit activation
- **Scope:** coordinator ruling and coordination artifacts only

## Activation

The user activates this mission by naming this file. Before beginning, the
executor must acknowledge the goal, sweep the `local_codex_1` inbox, and
publish or renew the relevant task claim. The repository's 15-minute
concrete-progress lease remains in force throughout the hour.

If anyone other than the current coordinator receives this mission, they may
audit the evidence and hand off a recommendation, but they may not issue the
coordinator's final ruling.

## Mission

Decide whether the proposed anti-benching rule—giving useful work to a troll
picker that would otherwise be left idle—has enough demonstrated real-game
reach to advance to its next existing gate, including a named-cost panel if
the task's current authorization permits it.

Finish with exactly one evidence-backed outcome:

1. **PROCEED:** the demonstrated reach is sufficient to advance to the next
   existing gate. State precisely what work is authorized, what remains
   unproven, and which owner or review gates still bind.
2. **STOP / DEFER:** the evidence is insufficient. Name the exact missing
   evidence and say whether it can be obtained without a new experiment,
   opening sealed data, or changing the approved design.

Do not end with a vague request for “more data.”

## Evidence Baseline

The ruling must reconcile, rather than blur, these two populations:

- The real-game idleness audit found `615 / 84,928` troll-turns (`0.72%`) in
  the measured benched class.
- The Phase 3b reach probe examined a selected, exactly replayable subcorpus:
  `49 / 160` v3 games replayed exactly and `111 / 160` refused closed. Within
  the 49 games, there were `882` eligible `nothing / nothing` rows. The probe
  restored and selected work on `339 / 882` rows, grouped into `34` episodes
  across `14 / 49` games; `35 / 49` games had zero reach.

The `339` rows are not a fraction of `2,903`, are not the same population as
the `615` real-game benched turns, and do not by themselves demonstrate
progress, score, causal repair, or acceptable cost. The 49-game subcorpus is
selected by exact replayability and is not established as representative of
all 160 games.

The existing method review accepted the probe method and independently
reproduced all eight controls, the `882`-row denominator, `339` selected
turns, `34` episodes, and `255` changed full command-vector turns. Full-corpus
reach remains unmeasured. The panel manifest digest is also run-path-sensitive
because split filenames are local to a run; the episode artifact is the
stable cross-run comparison.

## Required Sources

Read the current versions of these sources before ruling:

- `docs/STATE.md`
- `docs/CONSTRAINTS.md`
- the tail of the live ledger named by `docs/STATE.md` section 5
- `coordination/tasks/20260820-pair-selector-anti-benching.md`
- `coordination/messages/claude_1/20260823T133206Z-20260820-pair-selector-anti-benching-reach-handoff.md`
  and its pinned artifact commit `d0fdcc626c6d4a4184f3fd9b3262ee8dcbda85d8`
- `coordination/messages/codex_1/20260823T134629Z-20260820-pair-selector-anti-benching-handoff.md`
  and its pinned review commit `06ad9fb024e9b54a98bf4b519a871450ec5441b5`
- `coordination/messages/local_claude_1/20260823T131400Z-20260820-pair-selector-anti-benching-policy.md`

Verify that the pinned artifacts and stated counts agree. Also verify that
`rust/src/bin/yamo_orchard_live.rs` still has the required SHA-256 prefix
`fff6669b`.

## Work Plan

1. Sweep and acknowledge the coordinator inbox; confirm current roster,
   branch, task ownership, and transport health.
2. Audit the existing reach report and independent review against the task's
   approved design, denominators, controls, sampling limits, episode
   aggregation, and existing owner gates.
3. Decide `PROCEED` or `STOP / DEFER` using only the evidence already
   available. A `PROCEED` ruling must distinguish advancing to the next gate
   from claiming the intervention works.
4. Publish one immutable coordinator policy/ruling message, update the task
   record and coordinator status as needed, and notify the waiting builder
   and reviewer.
5. Run the repository's coordination linters, explicitly stage only the
   intended files, integrate through the coordinator branch, and verify the
   authoritative remote refs.

## Acceptance Criteria

The final ruling is complete only if it:

1. Uses `339 / 882` and `34` episodes correctly, never `339 / 2,903`.
2. States that only `49 / 160` games replayed exactly, `111` refused closed,
   and full-corpus reach and representativeness remain unmeasured.
3. Distinguishes Phase 3b reach from the `615 / 84,928` real-game benched
   class and from progress, score, causal repair, and cost.
4. Accounts for the independently reproduced controls and the run-path-
   sensitive panel digest limitation.
5. Names every still-binding task, review, or owner gate. This mission does
   not silently waive the recorded owner design approval requirement.
6. Gives the builder and reviewer an unambiguous next action—or an explicit
   stop—with no Arena ambiguity.
7. Leaves coordination delivery and quarantine lint at zero errors and
   records the integrated commit on the authoritative branch.

## Authority and Boundaries

The executor may inspect pinned artifacts, hashes, scripts, existing reports,
and coordination history; run read-only metadata or schema checks; and update
coordinator-owned task, status, policy, and handoff documents.

The executor may not:

- rebuild or rerun the reach panel;
- start a new simulation, experiment, Arena session, or TestSession;
- modify experiment code or the resident policy;
- open sealed map ranges or disturb `data/raw/games/`;
- waive an owner decision, design gate, or independent review requirement;
- treat reach as evidence of benefit or acceptable cost; or
- broaden the hour into implementation of the anti-benching rule.

This goal file never authorizes Arena writes.

## Stop and Fallback Rules

Stop and publish a precise blocker instead of improvising if:

- a pinned artifact is absent or disagrees with the reviewed counts;
- the current task record or owner ruling conflicts with the proposed next
  action;
- a defensible decision would require a new experiment, sealed data, or an
  Arena mutation;
- transport or quarantine validation fails; or
- the hour expires before a sound ruling is ready.

If the evidence supports a decision early, use the remaining time only to
make the ruling, task state, notifications, and integration self-consistent.
Do not expand scope.

## End Condition

The mission ends when the integrated coordinator ruling and its task/status
updates are published and verified, or when an integrated blocker identifies
the exact missing authority or evidence. The closing report must name the
decision, evidence basis, next actor, and whether an owner decision is now
required.
