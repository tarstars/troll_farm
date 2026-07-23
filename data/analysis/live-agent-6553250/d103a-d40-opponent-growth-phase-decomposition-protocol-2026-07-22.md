# D103a D40 opponent-growth phase decomposition — frozen protocol

Date: 2026-07-22  
Status: frozen before implementation or execution

## Question

D102 proves that exact D40 creates the desired renewable workforce but loses `48.396` paired
margin to the resident. It adds `17.547` own score and `65.943` opponent score while extending the
mean game from 258.141 to 300.717 turns. Before changing another scheduler, localize that opponent
growth to one of three causal time boundaries:

1. the one/two-worker opening and worker-three funding interval;
2. the common-horizon interval after worker three exists; or
3. the turns D40 continues after the paired resident game has terminated.

This is a decomposition of already-consumed D102 trajectories. It is not a policy search and
cannot qualify a candidate.

The zero-cost precursor also records that all ten fixed current rank-one `delineate` games used by
D95 contain zero `MSG` commands. Therefore D88's explicit task-message decoder cannot be reused
for that agent; latent task imitation is not the next experiment.

## Frozen scope

- Exact D40: `CompleteMacroEnv::work_conserving_deficit_heuristic_action()` and `step()` from the
  same source used by D102. Calling the action/step loop must reproduce
  `run_work_conserving_deficit_heuristic()` exactly.
- Exact resident: `SecureOrchardBot::new()` from the current embedded source.
- Exact opponents, official generator, seeds `9_824_100..9_824_131`, both seats, and all eight
  opponent families from D102.
- No new map, public replay, platform request, TestSession, submission, or resident change.

Run once with one worker and once with twenty workers. Sort by
`(map_seed, seat, opponent, policy, interval_index)` and require byte-identical TSVs.

## Interval telemetry

One row represents every state interval that advances the referee turn. Resident intervals are
one turn. A D40 interval may span multiple turns because a persistent macro job executes until the
next natural decision boundary.

Record start/end turn, workforce, score, live owned/opponent/joint/ambiguous crop counts; interval
owned/opponent/joint/ambiguous crop births; owned/opponent crop removals; exact increments and
cumulative counts for owned-crop harvest, reinvestment, successful TRAINs, completed/invalidated
jobs, direct-command/provenance/deposit failures; and final action/state hashes.

For each owner class, removals are the exact stock-flow identity
`start_live + births - end_live`. This captures crops born and removed inside a multi-turn D40
interval even when no boundary snapshot observes them live.

## Integrity gates

All are mandatory before interpretation.

1. Both executions contain the same complete episode grid and byte-identical interval rows.
2. Every episode has contiguous interval indices, strictly advancing nonoverlapping turn bounds,
   one final row, and exact nonnegative stock-flow counts.
3. Final turn, scores, workforce, TRAIN/job/failure/crop/harvest/reinvestment counts, action hash,
   and state hash reproduce the frozen D102 TSV for every policy/task key.
4. Replayed D40 stepping reproduces the direct D40 terminal API in every field used by D102.
5. Both policies retain zero unresolved provenance/ambiguous failures and D40 retains zero invalid
   direct commands and deposit-prediction failures.
6. Boundary resolution is adequate: for the paired resident terminal turn, the nearest D40
   interval endpoint has mean absolute distance at most five turns and p95 at most fifteen turns.

If only gate 6 fails, report phase totals as coarse diagnostics but classify the boundary as
unresolved. Any other integrity failure permits measurement repair only.

## Frozen additive opponent-score decomposition

For each task define:

- `scale`: D40's first interval endpoint with at least three own workers; if no third worker is
  created, use D40 terminal and mark the task `unscaled`;
- `common`: the D40 interval endpoint nearest the paired resident terminal turn, with ties choosing
  the earlier endpoint;
- resident score at a D40 boundary: the resident one-turn endpoint nearest that turn, again with
  earlier ties.

Then decompose terminal opponent-score excess (`D40 - resident`) exactly, up to the recorded
nearest-boundary convention:

- **pre-scale:** D40 opponent score at `scale` minus resident opponent score at `scale`;
- **post-scale common horizon:** D40 growth from `scale` to `common` minus resident growth over the
  same endpoint turns; and
- **extension:** D40 opponent growth from `common` to D40 terminal.

For unscaled tasks, assign the whole D40-versus-resident common-horizon difference to pre-scale
and retain only the post-resident extension as extension. Compute the identical decomposition for
opponent-created crop births. Report both task means, sums, positive shares of the known D102
opponent-score excess, map-clustered uncertainty, both seats, all families, and the result under
the earlier/later D40 common-boundary sensitivity choices.

If D40 reaches worker three only at or after its chosen `common` endpoint, treat it as unscaled
within the common horizon: assign the common-horizon difference to pre-scale, set post-scale common
growth to zero, and retain later D40 growth as extension. This bookkeeping rule was frozen after
the excluded seed-`9_824_000` instrumentation smoke and before the 32-map panel; it prevents a
negative-duration “post-scale” interval and changes no controller or observed trajectory.

Also report D40 opponent-crop removal/birth ratios before and after scale, the resident overall
ratio, live opponent-crop stock at scale/common/terminal, and own production increments by phase.
These are mechanism diagnostics, not alternate objectives.

## Branch rule

Classify a **primary boundary** only if integrity including resolution passes and one component:

- has mean opponent-score excess at least `+20`; and
- accounts for at least 50% of the positive total mean D102 opponent-score excess.

Ties choose the earlier component. Otherwise classify the failure as mixed.

- **Pre-scale primary:** the next learned representation must jointly control renewable
  establishment, bill production, and early denial; late role grafts remain closed.
- **Post-scale primary:** preserve D40 opening/funding and test a bounded worker-three allocation
  learner with explicit opponent-crop stock/lineage state.
- **Extension primary:** preserve D40 through the common horizon and test a terminal liquidation /
  stop-producing controller, not another opening or workforce policy.
- **Mixed:** proceed only with complete closed-loop opponent-aware policy improvement; isolated
  phase rules and hard roles are ineligible.

No classification authorizes fitting on D103 outcomes, opening confirmation maps, packaging,
TestSession, submission, Arena, or resident mutation.
