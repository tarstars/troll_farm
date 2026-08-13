# Cross-review — `readable__no_orchard` oscillation analyses and corrected merged plan

- Reviewer: `chatgpt_1`
- Task: `20260809-oscillation-attack`
- Task record: `coordination/tasks/20260809-oscillation-attack.md`
- Candidate: `readable__no_orchard`
- Candidate SHA-256: `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Review mode: committed-blob/adversarial synthesis; no private-repository execution claimed
- Peer artifacts reviewed:
  - `local_claude_1/oscillation-attack-local_claude_1-2026-08-09.md`
    at `1c65c9fc4cc242e4e8ce9abca325bc38cd83abc5`
  - `local_claude_1/oscillation-attack-local_claude_1-amendment-2026-08-09.md`
    at `5d775ddbeb6cdf6eaaf17ccb4d491eb97509131e`
  - `claude_1/banana-restoration-r2/oscillation-attack-claude_1-2026-08-09.md`
    at `0ea02595d2f9b8b40196dba67ee36bfc82e0bfbd`
  - my independent answer,
    `chatgpt_1/oscillation-attack-independent-answer-2026-08-09.md`
    at `1e3ce1dcc7bc20ee0e4b90103f4a355d93ad199e`
- Source checked directly:
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Final synthesis disposition: **`MERGE_WITH_CORRECTIONS`**

## Executive conclusion

The three independent analyses now support one coherent account:

1. The shipped planner coordinates **semantic targets**, not executable occupation and route
   plans.
2. `WAIT` is represented as `Target::None`, so an idle unit is invisible to pair compatibility
   even though its cell remains a hard physical obstacle.
3. The resolver silently replaces a blocked planned move with a one-turn detour; that override is
   not reported to the planner, target scorer or persistent state.
4. Replanning from the next state can therefore reproduce the same incompatible plan forever.
5. A separate one-worker episode is not a resolver conflict at all: the endgame scorer values the
   same conversion plan discontinuously depending on whether the unit is already on a door.

This is more precise than the original shared label “same-tree contention.” There are at least
three mechanisms:

- **M1 — path/corridor block:** distinct targets, but a stationary peer occupies the only route;
- **M2 — unmodelled stationary occupation:** the moving unit targets the idle peer's cell and the
  pair survives because `Target::None` is universally compatible;
- **M3 — scorer/Bellman two-cycle:** one unit alternates between goals because the candidate value
  is inconsistent across adjacent states.

The correct architecture is not “remember the previous cell” and not “port the watchdog.” It is:

> **plan executable occupation jointly; make stationary occupation explicit; make the resolver a
> verifier/executor rather than an invisible replanner; and require an explicit progress-producing
> yield or retarget when a stationary peer blocks the only productive route.**

A period-2 memory guard remains useful as a safety net and observability hook, but it cannot be the
primary cure. A mover-only monotonicity change can make D-1 disappear while preserving the exact
194-turn no-op as a stationary stall.

## 1. Points of genuine convergence

### C1. Target exclusivity already exists

All three answers now agree that adding ordinary “distinct target” claiming is not a general fix.
`select()` enumerates two-worker candidate pairs and calls `compatible()`. The abstraction is the
problem: different target cells can still have incompatible first landings or routes.

### C2. `Target::None` is a real hole

The source establishes:

```rust
fn wait() -> Candidate {
    Candidate { command: "WAIT".to_string(), score: 0.0, target: Target::None }
}

fn compatible(a: Target, b: Target) -> bool {
    if a == Target::None || b == Target::None { return true; }
    ...
}
```

Thus a stationary unit has no claimed target in the planner while retaining a claimed physical
cell in the world. This source-level finding is accepted. It explains how the M2 same-cell goal can
survive a pairwise compatibility rule that otherwise rejects equal cell targets.

### C3. The memoryless detour is a symptom of a planner/executor contract failure

The resolver's detour is a pure current-turn transformation. It does not persist the original
plan's failure, cool down the target or make the planner reconsider pair compatibility. The
planner can therefore reissue the same incompatible assignment next turn.

### C4. The Gold same-position watchdog is not the D-1 fix

The retired watchdog increments only while a worker remains in the same cell. An A-B-A unit moves
every turn. Porting the watchdog verbatim would not trigger on this population.

The useful Gold concepts are the joint landing solver, stationary obstacles, explicit stay,
whole-vector deterministic choice and swap/chain tests.

### C5. A motion-only fix is insufficient

This is the most important correction to both `local_claude_1`'s original recommendation and my own
independent answer.

- A previous-cell taboo can turn A-B-A into A-WAIT-WAIT.
- A monotone-or-hold landing rule can turn a forced retreat into a permanent hold.
- A joint solver with “stay” but no stationary-peer policy can correctly conclude that the mover
  has no progressive landing and then leave the world unchanged forever.

Removing the visible cycle is not evidence of restored control. Every red fixture must check
resource/task progress in addition to D-1.

### C6. The one-worker goal cycle needs a separate scorer fix

The source confirms the structural asymmetry in `endgame_candidates`: when already adjacent to the
shack, the unit prices only its current door; otherwise it evaluates all door cells. That can make
one plan more valuable after stepping away from the state in which it should have been easiest.

This is not a movement-conflict problem. It must have its own fixture and local scoring repair.

## 2. Corrections required before the analyses are merged as project truth

### X1. The load-bearing new measurements are not committed

`claude_1` labels the 21/13/1 mechanism split, the 20/20 idle-blocker result, the
ADVANCE/RETREAT counts and the proposed invariant coverage as MEASURED, but the instrumented source,
logs, classification scripts and machine-readable outputs remain under scratch paths. Hashes and a
prose restatement are not enough for independent review.

Before those counts become a frozen premise, commit a read-only evidence packet containing:

- the exact instrumentation patch or generated source;
- the byte-equality control result against the unmodified candidate;
- the episode table with map, seat, unit, turns, cells, goals, resolver branch and peer action;
- scripts that classify M1/M2/M3 and terminal/short mode;
- the per-step potential table used for the monotone-or-hold claim;
- output hashes and a single reproduction entry point.

The source-level existence of M1, M2 and M3 is accepted. Their exact corpus counts remain
**provisional** until that packet is committed and independently reproduced.

### X2. The new 35-episode corpus uses a referee revision that is not accepted

The `fuzz-panel/2-train` implementation exposed the useful `m040-s1` episode, but my acceptance
review rejected that referee for engine-conformance defects. Therefore:

- the original committed 20 terminal episodes remain valid red identities for this task;
- source-level analysis of the old episodes remains useful;
- the `m040-s1` interaction is a valuable provisional regression;
- corpus-wide c2 counts must not be treated as final calibration until referee revision 2 is
  accepted.

The merged plan may include `m040-s1`, but it must label the row provisional and rerun it under the
accepted referee before freezing final expected bytes.

### X3. “Standing on a plant” does not mean “working”

`local_claude_1`'s original answer inferred that the parked peer was working because 30/34 peers
stood on plants. `claude_1`'s new analysis says the terminal blockers are overwhelmingly idle.
These statements are not compatible.

The source-level lesson is clear even before the exact 20/20 count is reproduced: **occupation and
activity are separate state.** A tree-ownership rule keyed only on “capable worker on live tree” is
not sufficient. The planner needs an explicit stationary occupation/intent model:

- working and committed;
- idle but occupying;
- yielding/parking;
- moving with a predicted landing.

A cell occupied by an idle worker must not disappear from compatibility merely because its semantic
target is `None`.

### X4. D176a is not a causal estimate of a proper root-cause repair

The original local analysis argued that D176a's `+0.045` effect should dominate the much larger
observational margin gap. That is too strong.

D176a reduced detector-visible oscillation but left the worst long run and fragmented episodes. The
new synthesis shows why: a mover-only intervention can suppress motion while leaving the blocked
condition and lack of progress intact. Such an intervention is not a successful treatment of the
root cause.

The scientifically correct statement is:

- do not claim score gain for this work;
- do not use `+0.045` as an upper bound on the value of a route/occupation/yield repair either;
- treat value as outside the present objective and measure it separately only after control is
  established.

### X5. Per-unit monotonicity is too broad as a universal movement contract

`claude_1` proposes freezing:

```text
d_goal(landing) <= d_goal(current)
```

for every unit. This is a useful diagnostic for the measured A-B-A traces, but it is not yet a safe
global architecture rule. A coordinated corridor handoff, swap or yield can require one unit to
move temporarily away from its own semantic goal so the **system** makes progress.

Freeze the narrower invariant instead:

> A resolver may not silently replace a selected action with an unplanned retreat. Any retreat
> must be part of an explicit jointly selected plan with a named system-level potential and a
> bounded completion condition.

The Gold swap/chain controls should remain legal. The implementation may use non-negative
per-unit progress as a first experiment, but the test contract must not outlaw every deliberate
coordinated retreat before that design is evaluated.

### X6. Closing `Target::None` is not a one-expression cure

`wait()` has no unit parameter, so it cannot simply return `Target::Cell(unit.cell)` without
changing the candidate representation or selection API. More importantly, marking the idle cell as
owned only causes the other worker's current target pair to be rejected. It does not tell the idle
unit where to go and can convert M2 into a two-worker WAIT equilibrium.

The correct abstraction is broader:

```text
PlannedAction {
    unit_id,
    command,
    semantic_target,
    predicted_landing,
    occupied_cell_if_stationary,
    progress_potential,
    commitment/invalidation metadata
}
```

`WAIT` then has an explicit stationary landing equal to the current cell. Compatibility is checked
over occupation and executable landing, not only over semantic targets.

### X7. The proposed idle-yield rule is under-specified on articulation corridors

“Move the idle blocker to the nearest cell off the partner's shortest path” is not always defined.
In a width-one corridor there may be no off-path neighbour. The blocker may need to move through or
past the resource goal, and its first landing can conflict with the mover's planned landing.

Therefore idle-yield must be solved jointly with the mover, not applied as a local post-processing
rule. The plan needs:

- a destination/landing pair for both workers;
- a system-level decreasing potential;
- a bounded yield commitment;
- a rule for who yields based on task value and capability;
- an anti-thrash release condition.

### X8. The R-6a “banana must be chopped” clause overfits one policy

The literal `m110-s1` fixture is the right red identity, and it must check D-1 plus liveness. But a
correct controller may harvest the ripe banana, bank fruit, explicitly abandon it for a higher
value reachable task or perform another progress-producing action. Requiring that exact plant's
health or size be reduced can reject a controlled and productive retarget.

Replace the clause with a **task-disposition oracle**:

- within a bounded number of turns, either the selected resource task produces a real state
  transition; or
- the target is explicitly invalidated with a machine-readable reason and an alternative selected
  task produces progress within its own bound.

For this literal map, a stricter expected-job fixture may still be useful as one test, but it must
not be the universal definition of control.

### X9. Generic goal commitment can mask the localized scorer defect

For M3, a broad “keep the previous goal unless a rival wins by epsilon” rule can suppress the
alternation while preserving the inconsistent value function. The root fix is simpler and more
explainable: enumerate and price the same door alternatives in both adjacent states.

Test local Bellman consistency first. Goal commitment may then remain as a safety net, not as the
primary repair.

### X10. Diagnostic-task acceptance and final gate acceptance are different

The oscillation task says a proposed fix must eliminate all 20 terminal episodes and restore
control. The standing gate separately requires raw D-1 zero.

Keep both results in every report:

- **control acceptance:** terminal population zero; liveness/task disposition restored; no
  replacement WAIT or longer cycle;
- **gate acceptance:** all D-1 episodes zero under an accepted instrument.

A working-blocker control may legitimately show a bounded hold or handoff while the partner
finishes. It must not be called final gate-compliant if D-1 still fires.

## 3. Corrected unified mechanism contract

The current system splits one decision across incompatible representations:

```text
planner:       semantic target pair
resolver:      one-turn landing rewrite
persistent FSM: no record of rewrite/failure
```

The corrected contract should be:

```text
planner: jointly selects executable PlannedAction objects
resolver: verifies and serializes the selected landings; no hidden replan
feedback: any mismatch is a typed failure that invalidates/replans the target
liveness: stationary occupation has an explicit yield/park policy
```

### M1 — path/corridor block

Two semantic targets may be distinct while one route crosses a stationary occupied cell. The
planner must see predicted landings/occupation, and the stationary worker must either remain under
an explicit higher-priority commitment or receive a coordinated yield plan.

### M2 — stationary peer on the goal

`WAIT` must claim its current occupation. A moving action targeting that cell is incompatible
unless the same joint plan also moves the stationary unit away first.

### M3 — goal/scorer cycle

Candidate values for the same plan must be consistent across adjacent states. The door branch must
consider the same alternative set whether the unit is on a door or one step away.

## 4. Corrected merged implementation plan

## Phase 0 — commit evidence before touching behavior

Owner: analysis author plus independent execution reviewer.

1. Commit the M1/M2/M3 episode-classification packet described in X1.
2. Freeze literal state/command fixtures for:
   - `m110-s1`: terminal corridor/path block;
   - `m014-s1`: stationary peer on semantic goal / `Target::None` hole;
   - `m085-s0`: one-worker scorer cycle;
   - `m040-s1`: working-blocker anti-overfit control, provisional until referee acceptance.
3. Freeze the exact source SHA and map/state bytes. Do not call the generator from the regression.
4. Add a mutation/control per fixture so each oracle is known to bite.

No bot change starts before the red fixtures and evidence packet are reviewable.

## Phase 1 — red tests that measure control, not only D-1

### R1. Executable-plan compatibility

For each two-worker fixture, assert that a pair labelled compatible has:

- explicit predicted landing for each moving unit;
- explicit occupied cell for each stationary unit;
- no unexplained landing/occupation conflict;
- no resolver rewrite outside the selected plan.

### R2. Bounded task disposition

For every blocked fixture, within a frozen bound:

- inventory/carry/plant/task state changes; or
- the target is explicitly invalidated and a replacement task changes state.

This catches oscillation-to-WAIT and abandon-without-replan fakes.

### R3. Period and liveness scan

Assert:

- no zero-progress period 2;
- no replacement period 3..N in a bounded scan;
- no permanent WAIT/no-command run while live work remains;
- terminal population zero.

### R4. M3 scorer continuity

On the two adjacent `m085` states, enumerate the same door-plan alternatives and assert a consistent
ranking/value calculation. The current exclusive on-door branch must fail this test.

### R5. Anti-overfit motion controls

Preserve:

- working-blocker completion (`m040`);
- legal swaps/chains;
- shuffle invariance;
- open-field parallel movement;
- no new stationary-peer displacement loop.

## Phase 2 — minimal structural repair for M1/M2

1. Replace target-only pair compatibility with `PlannedAction` compatibility over semantic target,
   predicted landing and stationary occupation.
2. Represent `WAIT` as an explicit stay/occupation action.
3. Jointly choose mover and idler landings. If the only productive route is blocked, choose one of:
   - retain the stationary commitment because it has higher bounded value and explicitly retarget
     the mover; or
   - issue a bounded yield/park commitment to the blocker and preserve the mover's task.
4. Make the resolver verify the selected landings. It may not silently invent a detour. A mismatch
   becomes typed feedback and target invalidation.
5. Add repeated-override/period-2 telemetry as a fail-safe. The counter must remain zero on the
   frozen corpus; it may never silently absorb a new defect.

The Gold joint landing solver is a useful implementation source, but it must be integrated with
stationary occupation and yield/retarget policy. Porting it alone is insufficient.

## Phase 3 — local M3 repair

1. Remove the mutually exclusive “current door only” versus “all doors” candidate universe.
2. Enumerate all legal door plans in both states using one scoring function.
3. Keep a small target-commitment guard only after the value discontinuity is removed.
4. Run the M3 fixture and an anti-overfit set where changing door choice is genuinely correct.

## Phase 4 — acceptance sequence

1. Red fixtures demonstrate all three mechanisms on exact source bytes.
2. Unit/microstate tests pass.
3. Original 20 terminal rows: 20/20 eliminated with task disposition/liveness restored.
4. All D-1 rows: raw zero under the accepted referee if this work is to unblock the gate.
5. No new P4, permanent WAIT, longer-period cycle or target-flapping population.
6. `m040` and swap/chain controls pass.
7. Full accepted 240-row corpus rerun, with episode-length and resolver-feedback telemetry.
8. Separate value measurement only if the owner later considers promotion. No score claim is part
   of this task.

## 5. Disposition of each independent answer

### `local_claude_1`

**Keep:** source-level memoryless-detour account, warning that the same-position watchdog is a
non-fix, diagnostic use of the bad games, and the amendment withdrawing gate-only/reference-only
workarounds.

**Revise:** previous-cell memory is not sufficient; the capable-worker Elost rule does not cover an
idle incapable blocker; standing on a plant is not evidence of work; D176a does not bound a proper
root-cause repair.

### `claude_1`

**Keep:** M1/M2/M3 split; `Target::None` hole; M3 localization; working-versus-idle blocker
distinction; explicit warning that monotone motion alone becomes a stall; literal fixtures and
mutation controls.

**Keep with conditions:** exact counts and invariant coverage only after committing and reproducing
the evidence packet; `m040` only after accepted-referee rerun.

**Revise:** do not freeze universal per-unit monotonicity; specify idle-yield jointly; replace exact
banana-chop as the universal progress oracle; fix scorer continuity before generic commitment.

### `chatgpt_1` — amendment to my own independent answer

My planner/resolver seam diagnosis stands. My preferred joint landing solver was incomplete: I did
not make explicit that a correct solver can return a permanent stay unless stationary occupation
has a yield/retarget policy and task-progress oracle. The corrected recommendation is the full
`PlannedAction + occupation + typed feedback + bounded yield/retarget` contract above.

## Final recommendation to the integrator

Merge the three analyses into the Phase-0/Phase-4 plan above, preserving the disagreements and the
provisional-evidence labels.

Do **not** start by editing the tie-break. Start by committing the four literal red fixtures and the
machine-readable classification packet. Then implement one coherent planner/executor contract for
M1/M2 and one local scorer repair for M3. A previous-cell guard may be included only as telemetry
and defence-in-depth.

This cross-review authorizes no bot edit, candidate, detector/gate change, host value run,
TestSession, submission, restore or Arena action.