# A2-1 — economy-skeleton protocol

Status: **FROZEN before implementation and before either panel**

Owner/integrator: `local_codex_1`

Reviewer: unassigned

Programme: `docs/A2-programme-charter-2026-07-30.md`, Phase 1

## Question

Can a new closed-loop policy establish and reap an early orchard, bank fruit from its own
plantings, mine without dedicated detours, and train worker 3 by turn 110 in at least 40%
of fresh referee-mode tasks?

This is a mechanism gate for a new bot. It is not a resident patch, a same-panel value
claim, a promotion test, or an Arena candidate.

## Fixed semantic boundary

- **Early planting** establishes and partially renews a fruit base used by the workforce
  bill.
- **Late planting** converts accumulated fruit into future wood before liquidation.
- These are complementary phases. The policy may exploit partial renewal but may not
  assume population-level self-replacement: A2-0a measured median reproduction
  `R≈0.75`.
- The worker-3 target is the charter's amended K1: fruit-funded worker 3 in at least 40%
  of tasks by turn 110, plus non-zero reap of the policy's own planted crops.
- Mining is opportunistic only. A policy may issue `MINE` when a worker is already
  adjacent to iron as part of its ordinary route; it may never create a movement target
  whose purpose is reaching iron.

## Frozen substrate

Only the referee arm locked by A2-0b r1 may execute A2-1 panels:

- A2-0b implementation commit:
  `cd424a19a1f746d72afcfc8b7c824284cdda4012`;
- `rust/src/game/a2_referee_parity.rs` SHA-256:
  `518c222881ac23f8548cc13c858bacc93577ea920ecfbdbf0fd0e588cad1bf83`;
- `rust/src/game/a2_continued_mapgen.rs` SHA-256:
  `8e841958c47db42920ca23150bd2afbdb88acaa06c1a13f97ee684fbfea2a84d`;
- `rust/src/game/engine.rs` SHA-256:
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`;
- `rust/src/game/official_mapgen.rs` SHA-256:
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
- frozen resident control snapshot and byte-sacred dev copy SHA-256:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

`rust/src/game/mod.rs` is part of the A2-0b lock and remains byte-exact. The new A2-1
runner includes its new policy source through a runner-local `#[path]` module. The locked
A2-0b runner is read-only; legacy mode is not executed in A2-1.

Every panel uses the same eight `MacroOpponentMode` families and both seats. A fresh bot
instance and opponent instance are created for every task. Referee terminal semantics use
the standing `MACRO_TOTAL_TURNS` and `has_stalled` rule.

## Fresh ranges and information firewall

Fixed-string searches over tracked protocols, task records, sources, and result records
found no prior reference to either range before this freeze.

- **Development:** seeds `9,880,000–9,880,031`, 32 maps × two seats × eight families =
  512 tasks.
- **Confirmation:** seeds `9,881,000–9,881,127`, 128 maps × two seats × eight families =
  2,048 tasks.

Development may be inspected and rerun while implementing. Confirmation is sealed until:

1. focused tests and the complete development panel pass;
2. the policy, runner, analyzer, this protocol, and every direct dependency have SHA-256
   entries in a remotely published implementation lock;
3. the remote implementation commit is fetchable; and
4. no source changes follow that lock.

Any source change after the lock burns an attempted confirmation and requires a new
versioned protocol and a new fresh confirmation range. There is one confirmation look.

## Policy boundary fixed before development

The first skeleton is a deterministic stateful scheduler that owns the whole action stream:

1. every trained unit has `harvest_power ≥ 1` and `chop_power ≥ 1`;
2. the guaranteed worker-2 opening uses a legal real bill, vacates the shack under
   post-move legality, and never uses synthetic credits;
3. orchard placement prefers reachable grass adjacent to water, with deterministic
   tie-breaking and collision-free per-worker targets;
4. PLUM, LEMON, and APPLE planting/harvest/banking serves worker-3 deficits; BANANA may
   serve later wood conversion but cannot satisfy a worker bill;
5. self-planted fruiting crops are protected during the funding phase;
6. ripe owned crops, carried resources, planting commitments, and legal training take
   priority over fallback chopping;
7. `MINE` is issued only in-place when already adjacent to iron, never after an
   iron-directed `MOVE`;
8. late liquidation may plant banked fruit early enough to grow, then chop it for wood;
9. every unit receives at most one unit-bound command per turn and all resource
   reservations are decremented transactionally within the decision.

Development may change the deterministic priority details or thresholds, but every change
must be made before the implementation lock and described in the development result.
There is no selection among confirmation outcomes.

## Ownership and fruit-funding accounting

Plant ownership is reconstructed from successful commands and state transitions:

- a generation is `own` only when A2 issued `PLANT` on an empty cell, the expected species
  appears after the referee step, and no opponent command makes the origin ambiguous;
- removal closes that generation; later planting on the same cell creates a new generation;
- a successful `HARVEST` on a live own generation credits the observed positive carry
  delta by bill fruit species;
- a subsequent successful `DROP` at the own shack credits those units to cumulative
  banked own-crop proceeds;
- failed, ambiguous, opponent, and natural generations receive no own credit.

This follows A2-0a's disclosed fungibility limitation: once banked, individual fruit units
cannot be physically distinguished. A task has a **fruit-funded worker 3** exactly when:

1. a successful `TRAIN` changes own roster from two to three;
2. the post-step turn is at most 110;
3. before that training command, at least one PLUM, LEMON, or APPLE unit was successfully
   harvested from an unambiguous own generation and banked; and
4. the real revealed training bill was affordable from the actual pre-TRAIN inventory.

The result additionally reports cumulative fruit by origin, deposited own fruit by
species, bill size, and a conservative counterfactual `bill_needs_owned_fruit` flag
computed by subtracting still-banked own credit from the pre-TRAIN inventory. The
conservative flag is diagnostic, not substituted for the preregistered A2-0a-compatible
gate.

## Policy-owned command-quality gate

The runner records referee issues separately for A2 and the opponent. For A2:

- critical issues: exactly zero;
- unclassified issues: exactly zero;
- `unknown_command`, `unit_not_found`, `unit_not_owned`, `unit_already_used`,
  `out_of_board`, `invalid_skill`, `cant_afford_train`, `no_plant`, `no_fruit`,
  `no_capacity`, `no_harvest`, `invalid_plant`, `no_grass`, `existing_plant`,
  `no_seeds`, `no_chop`, `out_of_stock`, `no_shack`, `nothing_to_drop`, `no_iron`,
  `pick_stock_lost`, `train_affordability_lost`, `train_shack_blocked`, and
  `train_failed`: exactly zero;
- only `move_blocked` and `opponent_plant_blocking` may be non-zero;
- allowed own issues: at most 0.5% of A2's non-WAIT commands and at most 10% of tasks;
- the six standing detectors must run with exact trajectory coverage, and
  `repeated_failed_command` must remain zero.

Opponent issues remain diagnostic under A2-0b's supported taxonomy and do not count
against the policy-owned rate. Critical or unclassified issues from either player fail the
substrate gate.

## Development gate

The 512-task development panel must satisfy:

- all tasks terminal;
- every seed, seat, and opponent family appears exactly once;
- policy-owned command-quality gate passes;
- fruit-funded worker 3 by turn 110 in at least 40% of tasks;
- at least one unambiguous own generation is reaped and banked;
- successful `MINE` yield is positive at roster ≥2 and at roster ≥3;
- zero iron-directed movement targets;
- one-thread and 20-thread sorted TSV outputs are byte-identical;
- analyzer compilation and a non-vacuous synthetic self-test pass;
- focused Rust tests cover post-move training, own-generation reconstruction, harvest and
  deposit credit, ambiguous planting exclusion, no-detour mining, and deterministic
  commands.

Failure before lock permits at most one documented architecture repair within the same
fixed policy boundary. If the repaired development panel still misses the 40% gate, A2-1
stops without opening confirmation.

## Confirmation gates and verdict

Run the locked 2,048-task confirmation at one thread and 20 threads. Require:

| gate | requirement |
|---|---|
| C1 coverage | 2,048 terminal rows; exact 128 × 2 × 8 matrix |
| C2 amended K1 | fruit-funded worker 3 by post-step turn ≤110 in ≥40% of tasks |
| C3 own reap | positive unambiguous own-crop harvest and bank totals |
| C4 scaled mining | positive mined iron at roster ≥2 and at roster ≥3; zero iron-directed moves |
| C5 command quality | the frozen policy-owned and global critical/unclassified gates pass |
| C6 determinism | sorted one-thread and 20-thread TSV files are byte-identical |
| C7 integrity | implementation hashes, resident hash, range, task uniqueness, and fresh-instance checks pass |
| C8 detector bridge | all six detectors cover all dumped trajectories; repeated failures remain zero |

The analyzer reports overall, seat, family, and seed-block breakdowns. No subgroup threshold
is selected post hoc.

- **QUALIFIED:** C1–C8 all pass. This authorizes only Phase 2 protocol design.
- **FAILED / K1:** C2 fails. Stop the A2 programme and report the negative result.
- **BLOCKED:** integrity, determinism, source, coverage, or evaluator validity fails; do
  not interpret value and do not silently rerun.

Scores, margins, catastrophes, and negative mass are descriptive in Phase 1. A2 cannot be
called resident-competitive, deployable, or an Arena candidate from this protocol.

## Commands and materialization

Exact build, test, development, lock, confirmation, detector, and analyzer commands are
recorded in the implementation lock after the new CLI exists. Trajectory dumps are bulk
artifacts and require:

```text
python3 cgauto/check_external_storage.py --required-free-gib 5
```

before writing through `artifacts/`. Compact TSVs, hashes, aggregate JSON, and Markdown
results remain in the repository.

No Arena, TestSession, submission, raw-game, cron, sealed-range, or platform action is
authorized.
