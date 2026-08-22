# X1 mechanics re-derivation — source-backed conformance audit

Date: 2026-07-30  
Owner: `local_codex_1`  
Verdict: **CORE MATCH, WITH TWO A2-BLOCKING PARITY OBLIGATIONS**

## Source identity

Primary source is the public Troll Farm referee at commit
`290129129db7a7539d98739ebdb0ed63ee6ceb50`. The audit pins SHA-256 for the 16
core Java files covering `Referee`, `Player`, `Board`, `Constants`, `Unit`,
`Plant`, and every task implementation. The executable inventory is
`cgauto/mechanics_rederivation_audit.py`; a changed commit, file, or semantic
anchor fails the audit.

Local evidence was checked against:

- `rust/src/game/official_mapgen.rs`, SHA-256
  `5746607acdbaabed91720a9f7e75d73b55b6d87fdfe37f4f14ae3e4934d67971`;
  D33's untouched confirmation remains 120/120 exact turn-one streams.
- `rust/src/game/engine.rs`, SHA-256
  `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`,
  byte-identical to the frozen D169a lock and the later D170/D173 locks.
- The maintained Python simulator, exercised directly on task-order and
  resource edge cases by `tests/test_mechanics_rederivation.py`.

## Conformance matrix

| Area | Referee source | Local evidence | Result |
|---|---|---|---|
| Legend initialization | `Board.createMap`; `Player.init`; `Player.recomputeScore` | D33 exact generator; audit anchors | **MATCH** |
| Map generation | `Board.createMap`, `placeTree`, `placeTerrain`, `isValid` | D33 120/120 confirmation and unchanged source hash | **MATCH** |
| Movement and collisions | `Board.getNextCell`; `MoveTask.apply` | Python/Rust movement and collision implementation | **MISMATCH on equal-best tie only** |
| Task ordering | task `getTaskPriority` methods; `Board.tick` | dynamic MOVE/PICK/TRAIN/DROP/PLANT checks; Rust step anchors | **MATCH** |
| Command legality | `Task.createTask`, `Task.parseUnit`, task constructors | simplified Python/Rust parsers | **MISMATCH at parser boundary** |
| Harvest / plant / chop / mine | corresponding task `apply` methods; `Unit.harvest`, `Unit.mine` | dynamic duplication/plant-tick checks; Rust anchors | **MATCH** |
| Training | `Unit.getTrainingCosts`, `Unit.canTrain`; `TrainTask.apply` | dynamic post-MOVE/post-PICK/pre-DROP checks; Rust anchors | **MATCH** |
| Plant lifecycle | `Plant.tick`, `damage`; `Constants` plant arrays | dynamic water/cooldown check; Rust anchors | **MATCH** |
| Scoring | `Player.recomputeScore` | dynamic score check; Rust anchor | **MATCH** |
| Termination | `Board.hasStalled`; `Referee.gameTurn` | dynamic zero-grace check; frozen Rust implementation | **MATCH** |

The executable result contains zero source failures, zero dynamic failures, and
zero unexpected mismatches. Its verdict is
`CORE_MATCH_WITH_TWO_A2_PARITY_OBLIGATIONS`.

## Mechanics corrected or made explicit

For Legend, map height is uniformly selected from 8 through 11 and width is
twice the height. Each of PLUM, LEMON, APPLE, BANANA, and IRON receives an
independent inclusive-uniform draw from 2 through 10, and the same resulting
inventory is assigned to both players. Expected starting fruit is therefore 24
and expected starting iron is 6. Starting score is the four fruit draws, not
zero. The starting troll has `(movementSpeed, carryCapacity, harvestPower,
chopPower) = (1,1,1,1)`.

The starting bank was missing from `docs/mechanics.md`, but it was **not**
missing from `official_mapgen.rs`. This is a documentation/provenance defect,
not a newly discovered implementation defect.

Training a player with `n` existing trolls costs:

`PLUM=n+ms²`, `LEMON=n+cc²`, `APPLE=n+hp²`, and `IRON=n+chop²`;
BANANA and WOOD cost zero. TRAIN rechecks both affordability and shack occupancy
when priority 6 applies. Consequently MOVE can vacate the shack before TRAIN,
PICK can consume bank currency before TRAIN, and same-turn DROP cannot fund
TRAIN.

The complete task order is MOVE 1, HARVEST 2, PLANT 3, CHOP 4, PICK 5, TRAIN 6,
DROP 7, MINE 8, then plant tick and score recomputation. Same-type simultaneous
PLANT commands on one cell merge into one plant and spend every planter's seed;
mixed-type commands cancel. Last-fruit and last-wood duplication are both
source-confirmed. Plant growth adds the per-species health delta and therefore
preserves accumulated damage; the health formulas previously inferred from
replays are now confirmed directly by `Constants` and `Plant`.

## The two A2 parity obligations

### 1. Equal-best movement uses referee RNG

`Board.getNextCell` chooses randomly among all in-range cells tied for minimum
remaining distance. Both maintained local engines choose the lexicographically
smallest cell. This is not merely a cosmetic random seed: the referee continues
using the same `Random` instance after map construction, while
`generate_official(seed)` currently returns only `GameState` and discards the
post-generation PRNG state.

A2-0b must therefore do one of the following before Phase 1 evidence is treated
as referee-parity evidence:

1. preserve the exact post-map SHA1PRNG state and consume it on every tied move,
   with differential traces against the Java referee; or
2. prove and gate that every evaluated controller trajectory avoids equal-best
   ties, including opponent commands.

The first route is the robust default.

### 2. Local command parsing is not the referee validator

The referee enforces syntax, action availability by league, skill bounds,
ownership, one-use-per-turn, and critical versus non-critical error behavior in
`Task.createTask`, `Task.parseUnit`, and each task constructor. The Python and
Rust parsers intentionally accept a simpler internal command language and do
not carry equivalent player-bound ownership validation.

A2-0b must either implement source-faithful validation/error semantics or place
a checked legal-controller boundary in front of the engine and prove zero
invalid direct commands over every parity and evaluation panel. Merely observing
that invalid commands are rare is insufficient.

## Effect on earlier evidence

- **No rerun is required solely for the starting bank.** Replay-derived states
  already contain the referee inventory, and the accepted official Rust
  generator contains all five draws. Audited locked post-D33 runners use that
  generator.
- Historical synthetic-generator results remain mechanism evidence only, never
  field evidence, under the existing D29–D33 constraint. X1 neither upgrades nor
  newly invalidates them.
- Paired local causal panels compare candidate and control under the same
  deterministic movement tie rule, so X1 does not automatically reverse their
  within-substrate deltas. They still do **not** establish absolute referee
  trajectory parity where tied moves occur.
- Affordability reports must state the initial endowment explicitly. Analyses
  decoded from replays or official generated states already included it
  numerically; prose that described a zero-bank start was incomplete.
- No resident source, experiment lock, consumed range, or Arena state was
  changed by X1.

## Validation

Validation completed:

- `python3 -m pytest -q tests/test_mechanics_rederivation.py` — **6 passed**.
- `python3 -m pytest -q tests/test_mechanics_rederivation.py
  tests/test_sim_engine.py tests/test_sim_mapgen.py tests/test_end_condition.py` —
  **37 passed**.
- Direct `rustc --test` harness over the unchanged `state.rs`, `engine.rs`, and
  `official_mapgen.rs` modules — **2 passed** (both available Rust module tests).
- `cargo test --manifest-path rust/Cargo.toml --lib game::` did not reach tests:
  crate compilation requires the historical compile-time include
  `data/analysis/live-agent-6553250/d105a-q6-expert-population.tsv`, which is
  absent from this isolated worktree. No replacement file or symlink was made.
- Audit CLI against the pinned referee clone — zero source, dynamic, or
  unexpected failures.
- Resident dev-copy SHA-256:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
