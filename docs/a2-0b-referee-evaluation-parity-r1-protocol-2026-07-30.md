# A2-0b r1 — source-faithful referee-error protocol

Status: **FROZEN before r1 implementation lock and confirmation**
Owner/integrator: `local_codex_1`
Reviewer: `chatgpt_1`
Predecessor:
`docs/a2-0b-referee-evaluation-parity-protocol-2026-07-30.md`

## Trigger and scope

The frozen v1 development smoke stopped before implementation lock because G3 required
zero referee errors. Ordinary deterministic play produced source-defined noncritical
errors, predominantly `MOVE_BLOCKED`. The immutable v1 verdict is
`BLOCKED_BEFORE_IMPLEMENTATION_LOCK`; its evidence remains at
`data/analysis/live-agent-6553250/a2-0b-v1-development-blocker-result.json`.

R1 changes only the command-legality gate. It inherits v1, including amendment A1, for
the source boundary, consumed calibration range, resident reproduction target,
development/lock/confirmation split, thread parity, detector bridge, semantics-change
accounting, storage checks, and prohibitions.

## Fixed error taxonomy

An issue is **critical** when the harness cannot prove an exact source-defined outcome:

- bad grammar, numeric overflow, unknown verb/item, or another unparsed command, recorded
  as `unknown_command`;
- an apply-time path not identified by a source-defined reason, including the defensive
  `train_failed` fallback;
- any reason outside the frozen supported-noncritical set below.

The supported noncritical set is:

```text
unit_not_found
unit_not_owned
unit_already_used
out_of_board
invalid_skill
cant_afford_train
no_plant
no_fruit
no_capacity
no_harvest
invalid_plant
no_grass
existing_plant
no_seeds
no_chop
out_of_stock
no_shack
nothing_to_drop
no_iron
move_blocked
opponent_plant_blocking
pick_stock_lost
train_affordability_lost
train_shack_blocked
```

R1 may neither add a supported reason nor reclassify a critical issue after the
implementation lock. A new reason requires a separately versioned protocol.

## Source-faithful behavior obligation

Every supported noncritical reason must have a focused test that proves:

1. player, phase, reason, and `critical=false` accounting;
2. the rejected command/task does not execute effects that the Legend source rejects;
3. commands/tasks that the source still executes in the same simultaneous phase retain
   their effects; and
4. turn tick, plant tick, score recomputation, and later phases still occur when the
   source performs them.

Apply-time tests must cover collision-blocked movement, mixed-type simultaneous planting,
stock lost between PICK parse/apply, affordability lost between TRAIN parse/apply, and
occupied-shack TRAIN failure. The defensive `train_failed` branch must be
`critical=true` and must have a focused classification test even though the panel must
never reach it.

The checker runs before both legacy and referee turns. Legacy validation shadows the
unchanged legacy state and retained movement RNG; it does not alter legacy execution.

## R1 development smoke and lock

The development smoke reuses consumed calibration seeds 9,854,000–9,854,015, both seats,
and all eight frozen families. It may use multiple threads because no scientific value is
selected from this range. Before lock it must show:

- 256 rows, all terminal;
- zero critical issues in each mode;
- zero unclassified reasons in each mode;
- noncritical counts, reason counts, and first examples retained;
- counts split by A2-controlled seat (`own`) and opponent;
- the inherited source, initial-state, RNG-continuity, and frozen-file tests pass.

Then publish an implementation lock containing SHA-256 for every new source, runner,
analyzer, protocol, and unchanged dependency. Any implementation change after that lock
invalidates confirmation and requires a new protocol version.

## Replacement G3r — command semantics and accounting

Across both players, both modes, and every turn:

- critical issue count is exactly zero;
- unclassified issue count is exactly zero;
- every noncritical reason belongs to the frozen set and has a passing state-effect test;
- total issues equal own plus opponent issues;
- critical issues equal own plus opponent critical issues;
- reason totals equal the sum of per-row reason totals;
- the result retains first overall, first own, first opponent, and first critical
  examples without relabelling or suppression.

Nonzero supported noncritical counts do not by themselves fail A2-0b. They remain
diagnostic and are reported separately by mode, seat role, family, reason, and phase.
This exception does not weaken any later A2 policy protocol: Phase 1 must preregister its
own policy-owned command-quality gate before examining a new panel.

## Inherited confirmation gates

After the remotely published lock:

1. run all 2,048 consumed tasks at one thread and 20 threads;
2. require byte-identical sorted TSV outputs;
3. reproduce the legacy resident target exactly: 49 catastrophes and 12,749 total
   negative-margin mass;
4. require every game terminal and no controller instance shared across tasks;
5. preserve exact historical engine, map generator, and resident hashes;
6. dump 2,048 legacy and 2,048 referee trajectories only after the external-storage
   preflight, and run all six standing detectors with exact coverage;
7. report RNG draws, true ties, first state divergence, action/state hashes, score/margin
   deltas, and tail counts/mass separately by mode, family, and seat.

The inherited source hashes at r1 freeze are:

- `rust/src/game/engine.rs`:
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`;
- `rust/src/game/official_mapgen.rs`:
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
- resident snapshot:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- `cgauto/waste_sweep.py`:
  `cb5c813d591f3defd3809f97b25b61f6c7cdf67f039836d7b43c0544d29cad02`.

## Verdict

- **QUALIFIED:** G3r and every inherited v1 gate pass. Only the locked referee path may
  be used by a separately frozen A2 Phase 1 experiment.
- **BLOCKED:** any critical/unclassified issue, coverage mismatch, baseline mismatch,
  thread mismatch, detector failure, source drift, or other inherited gate failure.

No Arena, TestSession, submission, sealed-range, raw-game, or collection-cron action is
authorized.
