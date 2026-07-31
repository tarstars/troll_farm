# Independent review — Dridriun fruit-control postmortem

- Reviewer: `chatgpt_1`
- Task: `20260731-dridriun-fruit-control-postmortem`
- Reviewed coordinator head: `12b7fb5ca1ee93b52d3214aadd52265f59fdf860`
- Review date: 2026-07-31
- Proposed empirical verdict: `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`
- Review disposition: **`BLOCKED_PENDING_COMPACT_EVIDENCE_CORRECTION`**

## Decision

The published one-game reconstruction supports a narrow read-only follow-up in principle,
and it does not reopen any broad policy intervention. The internal generation counts,
turns, geometry, ripe-CHOP accounting, and actual-capture correction are coherent.

Independent acceptance is nevertheless blocked because the compact evidence does not yet
meet the task's own exact-state acceptance list. It also uses HARVEST command counts where
later prose can be read as confirmed fruit-unit flow, and it labels a distance quantity as
ETA without publishing the selected unit and movement-speed conversion. These defects are
repairable from the already-read exact game; no other replay or experiment is needed.

## 1. Internally reconciled replay facts

The compact records a 300-turn exact decode with zero unknown diff updates, final score
252–276, resident shack `(8,5)`, and Dridriun shack `(9,3)`.

The enemy-door APPLE at `(9,2)` has nine successive generations. Their published HARVEST
command counts are:

`33 + 4 + 6 + 6 + 10 + 5 + 1 + 0 + 18 = 83`.

Their resident CHOP command counts are:

`14 + 10 + 10 + 10 + 10 + 10 + 10 + 10 + 0 = 84`.

Eight generations are removed and the ninth remains alive. For the first generation,
plant turn 3 and first resident CHOP turn 63 give the stated 60-turn delay. Its published
25 pre-contact HARVEST commands and 33 total HARVEST commands are internally consistent
with the generation row.

The resident creates nine door-APPLE generations: six at `(8,4)` and three at `(9,5)`.
Four ripen. Their ripe CHOP counts reconcile as

`12 + 8 + 1 + 1 = 22`,

and fruit present at final removal reconciles as

`3 + 3 + 1 + 1 = 8`.

The first two ripe generations are attributed to unit 0 with `harvest_power = 1`, and the
compact reports opponent harvest-capable co-location on turn 225 and turns 240–244. The
important correction is explicit and consistent throughout the compact: Dridriun issued
zero HARVEST commands against resident-created apples and captured zero resident-created
apple fruit in this replay.

## 2. Accounting and causal boundaries are mostly correct

The result correctly refuses to promote three tempting but invalid quantities into causal
margin:

- 83 is an observed command count, not automatically 83 banked opponent points or 83
  recoverable points;
- eight fruit present at removal is one-game destroyed stock, not eight independent net
  points after HARVEST, DROP, delayed wood conversion, and displaced scheduling;
- opponent reach/capability around resident apples is a feasibility risk, not observed
  capture.

One replay establishes neither field frequency nor policy value. A changed denial,
planting, or harvest decision can alter later routing, growth, chop damage, replanting,
conversion timing, and both players' inventories. The no-simulation and no-policy-edit
boundary is therefore necessary.

## 3. Relationship to prior closures

The prior-arm reconciliation is directionally sound but must remain narrow:

- Phase 21 tested a generic ETA-6 opponent-crop score doubling and lost 7.77 Arena rating;
  it does not justify another unconditional urgency bonus.
- D173a/b tested broad harvest-before-chop rewrites and failed family, catastrophe, and
  negative-mass gates; it closes a broad local action rewrite, not every possible
  observational predicate.
- B3.7's population conclusion remains conversion-by-design. Four ripe resident
  generations are a tail inside that population, not a contradiction.
- B3.10's 4.84/game gross direct-stock closure covers its frozen near-camp domain,
  `own_door_distance <= 2`. The enemy tree here is published at resident-door BFS 3, so
  this exact recurring enemy-door stream is outside that narrow spatial subset.
- The broader B3.8 fruit-unit audit can still overlap this replay because it includes
  individual opponent-harvested or chop-destroyed fruit whenever an own unit comes within
  BFS 3 during that fruit's lifetime. Any successor precheck must explicitly join against
  that existing event ledger rather than call the entire stream previously unmeasured.
- H3a proves source reconstruction only and supplies no treatment-value evidence.

A genuinely distinct continuation is therefore limited to a read-only corpus query over a
strict joint relative-control predicate: repeated opponent-door flow, relative access and
kill burden, own production exposure, and a presently legal own ripe-stock action. It
must report overlap with B3.8/B3.10 and must not repackage the closed broad arms.

## 4. Blocking defect — invalid frozen base reference

The task record gives base commit

`c2df65565e49316b187a7d37babf69e09a2427a0`,

which does not exist. The claim commit shows that the actual coordinator head/parent was

`c2df655468a39c9f6f90da77a798f92b247ec6a8`.

The task, compact manifest, and corrected handoff must carry a valid frozen base so an
independent reviewer can reproduce the evidence boundary.

## 5. Blocking defect — HARVEST commands versus fruit units

The exact decoder used by the evidence distinguishes two quantities:

- `harvest_turns`, appended when a unit is assigned HARVEST on the generation cell;
- `fruit_harvested`, computed from the unit's positive carry delta.

The compact publishes only a field named `opponent_harvests`, whose generation rows are
clearly command-turn counts. The human report begins with the precise phrase “HARVEST
commands” but later says Dridriun “harvested 25 apples” and describes 83 as observed flow.
That stronger wording is not supported by the compact as published.

For every enemy-door generation and in total, the correction must publish separately:

- HARVEST command count;
- confirmed successful HARVEST command count, if distinct;
- actual fruit units gained from carry deltas;
- failed or zero-gain HARVEST command count.

Until then, the canonical prose must say “HARVEST commands,” not “apples harvested,” and a
successor precheck must value carry-delta-confirmed fruit units rather than command
pressure.

## 6. Blocking defect — missing exact state and capability appendix

The task explicitly requires exact turns, cells, units, harvest/chop capability, camp
distances, fruit, health, and generation fate. The result provides turns, cells,
generation fates, planter harvest power, fruit maxima, and selected co-location turns, but
not enough state to verify the proposed strict relative-control predicate.

For the first enemy-door generation, each distinct removal regime, and all four ripe
resident generations, the compact needs decisive-event rows containing:

- acting resident and opponent unit IDs;
- movement speed, carry capacity, harvest power, and chop power;
- carry contents and free capacity before the command;
- tree health and fruit stock before and after the command;
- emitted command and confirmed carry/health effect;
- raw BFS distance, movement-speed-adjusted ETA, and co-location where relevant.

This evidence is needed to distinguish “harvest-capable and co-located” from a presently
legal and useful HARVEST alternative. A harvest-capable unit can still be full, assigned a
conflicting action, or face a conversion/scheduling tradeoff. It is also needed to verify
that the repeated enemy-tree removal is low-lethality rather than merely command-heavy.

## 7. Blocking defect — BFS and ETA are conflated

The human result says the nearest opponent harvest-capable troll was “BFS 1–5 away.” The
JSON field is named `opponent_harvest_capable_eta_at_plant`, and the handoff calls the
first two values “ETA 2/1.” The compact does not publish the selected unit ID, its movement
speed, the `harvest_power > 0` filter, or whether the numbers are raw BFS or
`ceil(BFS / movement_speed)`.

The correction must publish both raw BFS and movement-adjusted ETA, at planting and at the
first ripe turn when the capture-risk claim depends on later access. The selected capable
unit must be identified. This also prevents the same state-index ambiguity already found
in N5 from being silently repeated.

## Final disposition

The exact game contains a real recurring enemy-door command stream and a real resident
ripe-CHOP tail, while actual capture of resident apples is zero. Those facts can justify a
separately reviewed read-only precheck after the compact is corrected.

Until then, the independent verdict is
`BLOCKED_PENDING_COMPACT_EVIDENCE_CORRECTION`. This is not evidence for a broad
intervention and does not reopen Phase 21, D173, B3.7, B3.10, source editing, threshold or
capability changes, simulation, a panel, a candidate, TestSession, submission, or Arena
action.

## Validation performed

- Cross-read the task, claim, handoff, compact JSON, human result, manifest, and live
  backlog disposition.
- Recomputed every published generation, command, delay, ripe-CHOP, and removed-fruit
  aggregate.
- Inspected the exact decoder's state indexing, generation attribution, unit ETA, command
  attribution, and carry-delta fruit accounting.
- Reconciled the proposed continuation against Phase 21, D173a/b, B3.7, B3.8, B3.10, and
  H3a boundaries.

No other game, replay, trajectory, map, range, or bulk artifact was opened. No analyzer,
source, frozen artifact, runner, simulation, panel, threshold, capability, candidate,
TestSession, submission, or Arena state was changed.
