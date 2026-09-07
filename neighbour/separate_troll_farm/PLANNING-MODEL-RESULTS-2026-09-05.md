# A verified forward-model foundation, not yet a stronger planner

Follow-up: the model is now integrated experimentally with the stronger V439 policy in
`lookahead_search.rs`. See `LOOKAHEAD-DEVELOPMENT-PROTOCOL-2026-09-05.md` for implementation,
source/runtime gates and the still-unproven competitive hypothesis. The extraction findings
below record the completed foundation stage; production remains V439 without search.

`planning_model/` now contains a self-contained direct-endpoint forward model extracted from
the neighboring reference, with one independently established local correction. It is not wired
into either live V439 or the experimental controller's decisions. The strategic hypothesis in
`PLANNING-MODEL-DESIGN-2026-09-05.md` remains unproven until a planner is implemented and evaluated.

## Extraction and command domain

`planning_model_source.py` guards the three original source hashes and checks a deterministic
snapshot. The copied action application/parse ordering is from `a2_referee_parity::step`, not
the simpler historical `engine::step`. Public `parity::step_direct` rejects unsupported requests
before state or legality mutation. Use this entry point, not individual engine helpers.

Both players must use explicit reachable MOVE endpoints; non-direct moves depend on hidden
referee random state and are not silently assigned a fabricated seed or lexicographic outcome.
Numeric fruit aliases are also excluded from the initial domain. Physical player order and raw
IDs are retained. A future relative-seat controller bridge must handle simultaneous training-ID
allocation explicitly. `has_stalled` is included, but its persistent counter is caller-owned.

The bounded read-only Claude review completed with no permission denials (reported USD 0.883476).
Its ordering/RNG cautions were independently checked. Its suggestion to place tests in the neighbor
was rejected; every test and change is here. Its approximate 16k source-size estimate was not
adopted as a measurement. The original response is archived in working storage.

## The independent check found an inherited simulator defect

The initial extraction matched the full neighboring referee on **8,192 transitions**, including
full state, command legality, both physical players, all eight action types and end-condition
counter checks. This established extraction fidelity, not official correctness.

The next check used all **3,449 recorded transitions from twelve archived official games** in the
baseline-restoration confirmation. It rejected 560 outside the direct-move domain, matched 2,887,
and found **two plant-order differences**. They occur in game **901544252**, turns **207 and 269**:

- Turn 207: simultaneous planting at `(8,4)` and `(7,5)`; official creation order is `(8,4)` first.
- Turn 269: simultaneous planting at `(14,5)` and `(13,6)`; official creation order is `(14,5)` first.

All plant attributes, units, inventories and scores match; the append order alone differs.
The Java source confirms the cause: `engine/task/Task.java:115` groups cells and sorts by cell ID,
while `engine/Cell.java:34` defines that ID as `x + (y << 16)`. This is row-major. The Rust helper
used a `(x,y)` BTreeMap iteration, which is column-major. Creation order can affect later bot
tie-breaking and therefore must not be normalized away in an exact prediction.

Only the local planning extraction is repaired: new plants append in `(y,x)` order. The neighbor
and frozen historical panel executables are unchanged. Minimal fixtures reproduce both official
cases. Post-repair differential checks retain complete state equality, with **one explicit oracle
adjustment**: the reference's newly-created suffix is put in the independently verified Java order.
The old prefix is never sorted. Every such adjustment is counted, rather than hidden as equality
with an unchanged oracle.
The final differential run records 74 such adjustments across its fixtures and generated sequence.

Re-running the independent official check gives **2,889 matches, 560 explicit unsupported cases,
zero differences**. These are single-step checks in twelve games, not proof of all possible rules
or a claim that the model predicts unknown opponents. Rejected transitions remain in the report.
Raw commands are used; no opponent moves are replaced with observed future endpoints.

## Verification and usable budget

- Executable cases cover own swaps/blocked chains/contested destinations; egress plus TRAIN;
  PICK invalidating a training bill; DROP not funding a parsed TRAIN; simultaneous harvest/wood
  duplication; merged/conflicting planting; newborn-tree protection; and rejection before mutation.
- All **471 project tests pass** (164.60 seconds), including extraction provenance, standalone
  compilation, combined-source compilation and the 8,192-transition differential harness.
- Measured model size: **27,944 UTF-16 units**. Combined with the corrected experimental two-worker
  controller: **65,624 units**, independently compiled. The unused model does not itself improve
  that controller; this only establishes space for a future planner under the 100,000-unit limit.
- On the supported official-state workload, a direct model step averaged **101.2 microseconds**,
  median 97.1, p95 201.6, maximum 382.5 on this machine. This excludes bot decision generation,
  tree/worker evaluation, process startup and most state construction. It is not a platform timing
  guarantee or evidence that an arbitrary beam size will fit the move budget.

Evidence root: `/data/separate_troll_farm-working/planning/2026-09-05/`, including the Claude
prompt/response, retained pre-fix disagreements, full official input/status records, source
comparison scripts, compiled test executables, timing and differential logs. No new platform
games were requested for this work, and live V439 was not changed.

Next concrete step: a bounded joint-action planner with measured full-turn runtime and executable
fixtures showing a better selected sequence than the greedy controller. Define its root choices,
continuation/opponent policy, horizon, terminal evaluation and fallback before a competitive run.
Include replenishment and worker funding in the comparison, not merely immediate banked score;
then freeze a real-opponent development screen and a separate prospective confirmation.
The smaller experimental controller is not a mandatory ancestor: V439 remains the measured
stronger policy. The combined-size proof is not a decision to discard that stronger continuation.
V439's core already selects compatible immediate action pairs; the new hypothesis is multi-turn
sequence evaluation. A root-action override must also reconcile any stateful controller's cached
goals and pending transactions, rather than leaving memory for an action that was never executed.
