# A2-0b — referee and evaluation parity protocol

Status: **FROZEN before implementation; source correction A1 incorporated**
Owner/integrator: `local_codex_1`  
Reviewer: `chatgpt_1`  
Programme authority: `docs/A2-programme-charter-2026-07-30.md`, Phase 0b

Binding amendment:
`docs/a2-0b-referee-evaluation-parity-rng-amendment-2026-07-30.md`.

## Question

Can an isolated Architecture-2 evaluation path:

1. preserve the exact SHA1PRNG state after official map generation and use it for
   referee-random equal-best movement;
2. independently prove that every emitted command is legal under the Legend referee;
3. preserve the established two-seat/eight-family resident rig, deterministic thread
   behavior, trajectory bridge, and six waste detectors; and
4. reproduce a previously recorded resident control result

before any A2 Phase 1 number is trusted?

## Why this protocol exists

X1 found no unexpected mismatch in initialization, task priority, resource actions,
training, plant lifecycle, scoring, or termination. It did find two boundaries that make
the historical simulator insufficient as a claim of absolute referee parity:

- `Board.getNextCell` randomly selects among equal-best cells from the same `Random`
  instance used for map creation, while both local engines select lexicographically and
  `generate_official(seed)` discards the post-map PRNG state.
- The local parsers do not implement the referee's ownership, reuse, action-shape, skill,
  availability, and error checks.

The historical engine and map generator are frozen evidence. They are not edited.

## Fixed implementation boundary

Add a separate `game::a2_referee_parity` module and a separate A2-0b runner.

- The new module includes the unchanged D33 official-map implementation in a private
  namespace and adds a source-identical generator entry point returning both
  `GameState` and its post-generation `Sha1Prng`.
- Referee-mode movement copies `Board.getNextCell`/`MoveTask.apply` semantics. A target
  already reachable within speed returns directly with no RNG call. Every other path
  selection calls `nextInt(closest_count)` exactly once, **including bound 1**; a tie is
  where that mandatory draw can change the selected cell.
- All non-movement mechanics delegate to the unchanged, X1-audited engine functions,
  except the existing pre-PLANT choppable-cell snapshot is preserved explicitly.
- A source-shaped Legend command checker runs on both players' raw commands before every
  turn and records reason-counted parse-time and apply-time failures. It does not silently
  bless a command merely because the simplified engine can execute it.
- The runner supports `legacy` (unchanged engine) and `referee` modes over the same task.
  The legacy arm exists only to reproduce the fixed historical control. A2 uses the
  referee arm after this protocol.

No existing engine, generator, controller, opponent, detector, runner, lock, or result
file may be edited.

## Calibration panel — fixed and already consumed

Reuse D173b's completed panel solely as a calibration fixture:

- seeds **9,854,000–9,854,127**;
- 128 maps × 2 seats × 8 opponent families = **2,048 tasks**;
- families, in fixed order: `resident`, `gold_adaptive`, `compact_gold`,
  `norx_native_three`, `legend_balanced`, `mybot`, `script_boss`, `silver_boss`;
- resident control: `rust/src/d171a_control_resident_snapshot.rs`.

This range is already consumed. It may establish parity but may not select, tune, or
price an A2 policy. Phase 1 receives newly declared ranges under its own protocol.

## Known resident reproduction target

D173b recorded the unchanged resident control on this exact task matrix. The legacy arm
must reproduce, exactly:

- rows: **2,048**, all terminal;
- catastrophes (terminal margin ≤ −100): **49**;
- total negative-margin mass: **12,749**.

These fields are independent of D173b's candidate. They are frozen in
`d173b-harvest-before-chop-result.json`, SHA-256
`30a475cdb06190717ed7a86e4069cc4791a2281e440acccf5b730b06dda3e1dd`.
Exact equality is required; there is no tolerance and no retry/tuning path.

The current waste-detector library postdates D173b's locked detector version, so old
detector totals are not a valid reproduction target. The current six detectors must run
and cover all 2,048 trajectories in each mode, but their legacy/referee difference is
diagnostic rather than a value gate.

## Development/confirmation split

1. **Unit/source phase:** source anchors, initial-state identity, controlled movement
   ties, zero-draw unique moves, validation fixtures, and unchanged delegated mechanics.
2. **Development smoke:** seeds 9,854,000–9,854,015, all seats/families, one thread.
   Inspect only integrity, legality reasons, and legacy reproduction plumbing.
3. **Implementation lock:** freeze all new source hashes plus every unchanged dependency
   hash before the remaining range is executed.
4. **Confirmation:** execute the complete 128-map panel once at 1 thread and once at
   20 threads. Result rows are sorted by `(seed, seat, family)` before serialization.
5. **Trajectory/detector pass:** dump the 20-thread legacy and referee trajectories to
   external-backed `artifacts/experiments/a2-0b-referee-parity/`, then run all six
   standing detectors without threshold changes.

Any implementation change after step 3 invalidates confirmation and requires a newly
versioned protocol. There is no same-protocol repair.

## Frozen gates

### G1 — source and isolation

- X1 referee commit/file hashes match.
- `engine.rs` SHA-256 remains
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`.
- `official_mapgen.rs` SHA-256 remains
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`.
- resident snapshot and dev copy remain
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

### G2 — initial state and RNG continuity

- For at least 1,024 nonzero deterministic seeds, the new generator's `GameState` is
  field-identical to `generate_official(seed)`.
- A direct target already reachable within speed consumes zero draws.
- Every non-direct path selection consumes one bounded draw, including a unique-best
  `nextInt(1)`, and selects the indexed best cell in referee x-major/y-minor order.
- RNG draw totals are deterministic and reported per panel.

### G3 — command legality

Across **both players, both modes, and every turn**, counts must be zero for:

- unknown/bad-shape/overflow command;
- nonexistent, unowned, or reused unit;
- out-of-board move;
- unavailable action or invalid item/skill;
- missing plant/fruit/capacity/power/seed/stock/shack/iron precondition;
- apply-time MOVE blocking, PICK stock loss, TRAIN affordability/shack blocking, or any
  other source-defined failure.

Any nonzero count yields **BLOCKED**. The record must retain reason counts and first
examples; it may not discard or relabel failures.

### G4 — evaluation integrity

- exact 2,048-task matrix, both seats and all eight families;
- every game reaches referee terminal semantics;
- one-thread and 20-thread sorted TSV outputs are byte-identical;
- no stateful controller instance crosses task boundaries;
- legacy reproduction is exactly 49 catastrophes / 12,749 negative mass.

### G5 — detector bridge

All six current `cgauto.waste_sweep` detectors execute without error and cover exactly
2,048 legacy plus 2,048 referee trajectories. Counts are reported separately by mode.
No detector result is used to tune this harness.

### G6 — semantics-change accounting

Report:

- tasks/turns with an equal-best RNG draw;
- first legacy/referee state divergence;
- terminal score/margin deltas by family and seat;
- tail counts/mass in both modes;
- action/state hashes and RNG draw totals.

This is a calibration description, not an A2 value estimate. A large legacy/referee
difference does not fail parity if G1–G5 pass; hiding it does.

## Verdict

- **QUALIFIED:** every gate G1–G6 passes. A2 Phase 1 may use only the referee-mode path.
- **BLOCKED:** any gate fails. No A2 Phase 1 evaluation may start; preserve the evidence
  and open a separately reviewed repair protocol.

## Locked dependencies at protocol freeze

- referee commit:
  `290129129db7a7539d98739ebdb0ed63ee6ceb50`;
- `rust/src/game/state.rs`:
  `0b75b26b7a700ce023d2f0d65993a57a0f6e577b54dc1b2012dd00b6ff3fde9c`;
- `rust/src/game/engine.rs`:
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`;
- `rust/src/game/official_mapgen.rs`:
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
- `rust/src/d171a_control_resident_snapshot.rs`:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- `cgauto/waste_sweep.py`:
  `cb5c813d591f3defd3809f97b25b61f6c7cdf67f039836d7b43c0544d29cad02`.

## Storage, safety, and authority

Before writing trajectories, run
`python3 cgauto/check_external_storage.py --required-free-gib 5`. Stop if it fails.
No YT is expected: the panel is comfortably local and below one hour.

Do not touch sealed ranges, `data/raw/games/`, the collection cron, the resident,
submission tooling, TestSession, or Arena. Do not format `rust/src/bin/` or `cgauto/`.
