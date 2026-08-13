# Independent answer — attacking the `readable__no_orchard` oscillation

- Agent: `chatgpt_1`
- Task: `20260809-oscillation-attack`
- Candidate: `readable__no_orchard`
- Source: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Candidate SHA-256:
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Mode: committed-blob analysis and proposal only
- Boundary: no bot, detector, gate, harness, candidate, host run, TestSession, submission, restore
  or Arena mutation

## Independence statement

Before publishing this artifact I did **not** read either other agent's oscillation answer or the
integrator's oscillation-answer artifact. I read the assignment/task record, the named candidate,
the reference record, the current D-1 detector and the retired Gold motion layer. This answer was
formed independently.

## Executive conclusion

The established account is directionally right but locates the root cause one layer too low.

The visible two-cycle is produced by the resolver's memoryless detour rule. The deeper design defect
is a broken contract between **planning** and **execution**:

1. the planner declares two candidate actions compatible when their *targets* are distinct;
2. it does not ask whether the two actions' first landings or routes are compatible with a peer
   that will remain stationary and work;
3. the resolver later rewrites the blocked MOVE into a detour, but does not report that rewrite as
   target failure, does not change the commitment and does not feed the result back into scoring;
4. next turn the planner selects the same target pair again, and the resolver applies the mirror
   rewrite.

In a static board this composition is a deterministic involution:

```text
same target assignment + same parked peer
A --detour--> B
B --detour--> A
```

Nothing in either layer owns responsibility for convergence. The planner says “the targets differ,”
while the resolver says “I found a legal cell for this turn.” Both local statements are true and
the composed policy can spend 194 turns doing no work.

This matters for the remedy. A previous-cell taboo or watchdog can suppress the visible A-B-A
shape while leaving the planner/resolver contract broken. The strongest fix is to make the motion
stage jointly choose **executable landings under stationary-worker ownership**, and to feed a
blocked/overridden action back into target validity. A period-2 guard should remain as a safety net
and regression oracle, not as the primary architecture.

## 1. Source-level cause

### 1.1 The planner already has target exclusivity — therefore target equality is not the whole bug

`MoisanBot::select` already evaluates the two own units jointly when there are exactly two. Its
`compatible()` function rejects equal cell/tree/bank targets. This is stronger than a sequential
“both workers pick the highest score” planner.

That fact attacks a tempting but incomplete diagnosis: simply adding “distinct targets” cannot be
the repair because distinct target compatibility is already present in the submitted source.

The abstraction is too coarse. Two different trees can still have routes whose next landing runs
through the cell occupied by the peer working the other tree. Target compatibility does not imply
route compatibility.

### 1.2 The resolver creates an unacknowledged execution plan

`resolve_move_conflicts_with_priority_and_forbidden` computes each MOVE's referee landing with
`next_cell`. Cells of non-moving own units enter `reserved`. When a mover's intended landing is
reserved, the resolver chooses an orthogonal detour from the mover's **current** cell, minimizing:

```text
(distance from detour cell to the original target, detour cell lexicographic order)
```

The detour filter knows current occupancy and reservation, but it knows no previous cell, no
previous resolver override, no target hold age and no “this target has failed twice” state.

The command is rewritten to the chosen landing cell. The original target remains only an ephemeral
local variable; no durable state records that the resolver could not execute the planner's action.

### 1.3 Why the return step is deterministic

After the first detour, the old cell is no longer occupied. If the board, target and parked peer
remain unchanged, the next turn reconstructs the same target objective from the new side. The
previous cell is now a legal orthogonal detour and often has the best `(distance, cell)` key. The
resolver therefore sends the unit back.

The lexicographic tie-break makes this reproducible; it does not make it convergent. A fixed total
order helps only if the optimization includes “stay” or a monotone potential over the complete
state. Here it is re-run over a different local neighbour set on each side of the bounce.

### 1.4 Why the planner does not escape

The candidate has no durable per-unit target commitment and no penalty for a resolver override.
Scores are recomputed from the current state. The plant and parked peer remain; the moving unit has
not changed cargo, inventory or asset state; so the same target remains best.

The loop is thus not merely “a bad detour tie.” It is the fixed point of two stateless functions at
different abstraction levels:

```text
planner: distinct targets are compatible
resolver: this turn's landing is legal
composed system: no eventual-progress obligation
```

### 1.5 Why an active opponent tends to dissolve the terminal mode

This explanation is consistent with the observed opponent dependence without relying on it as
proof. An aggressive opponent changes plant existence, health, fruit state, occupancy or target
scores. Any such change can invalidate the target or parked-peer configuration and break the fixed
point. An idle/harvesting opponent leaves the self-blocking subgraph static long enough for the
bounce to become terminal.

## 2. Two attacks on proposed “obvious fixes”

### 2.1 Porting the Gold watchdog verbatim will not catch A-B-A

The retired `rust/src/botmain/motion.rs` watchdog counts **same-position streaks while MOVEing**.
The D-1 terminal defect changes position every turn. Its same-position streak is always zero.

Therefore the verbatim watchdog is not a fix for this episode class. Porting it may solve a useful
neighbouring defect, but claiming it addresses these 20 terminal episodes would be a category
error.

The useful Gold mechanisms are instead:

- stationary teammates as hard obstacles;
- joint landing assignment;
- stay as an explicit candidate;
- non-negative progress filtering;
- canonical whole-vector tie-breaking;
- distinct camp-cell claims for the banking-specific variant.

If a watchdog is retained, it must track period-2 position history or repeated resolver overrides,
not only failure to move.

### 2.2 “Exclusive targets” alone is already implemented

The current planner rejects equal tree/cell targets. An Elost-style ownership rule still has value,
but only if ownership changes the **route graph or assignment**, not merely the target equality
check. A worker standing on and servicing a tree must make that cell a claimed stationary obstacle
for peer path scoring, or the second worker can be sent to a distinct target whose path repeatedly
hits the claimed cell.

## 3. Action catalogue

Effects below are predictions to be falsified, not measured results. “Terminal” means the 20
committed >=62-turn episodes in the exact candidate panel.

### A. Route-aware joint assignment at the planner/resolver seam — **preferred structural fix**

**Change.** Extend each candidate action with its predicted referee landing under the current
stationary set. Pair compatibility must include:

- distinct target claims;
- distinct first landings;
- no first landing on a stationary working peer;
- a defined non-negative progress/stay result;
- an explicit blocked result when no compatible landing exists.

The selected pair and the motion resolver then operate on the same object rather than one rewriting
the other invisibly.

**Expected effect on 20 terminal episodes.** High; it removes the exact interface mismatch that
creates the bounce. If no executable pair exists, the planner must choose WAIT/another target rather
than manufacture alternating detours.

**Cost.** Medium. The candidate already enumerates all two-worker target pairs, so adding landing
metadata and compatibility is much smaller than replacing the economy planner.

**Risk.** First-landing compatibility may be too local for longer corridor conflicts; conservative
rejection may reduce useful parallelism.

**Falsification.** Any exact terminal replay in which the selected pair is declared compatible and
one action is subsequently rewritten because of a stationary peer. Also falsified if a new
terminal loop appears with distinct first landings but later route convergence.

**Owner needed?** No for a scoped implementation experiment; yes for any gate-rule or platform
promotion decision.

### B. Port the Gold **joint move solver**, not its same-position watchdog

**Change.** Port the tested joint landing solver from `rust/src/botmain/motion.rs`: stationary
workers are hard obstacles; all movers' landing cells are selected jointly; stay is legal;
negative-distance progress is forbidden; swaps/chains remain possible; ties are canonical over the
whole landing vector.

**Expected effect.** High. In a static blocked configuration, a worker cannot retreat to a previous
cell merely because a sequential resolver reached it second. With stay included and a canonical
whole-vector order, the static two-cell involution has no reason to alternate.

**Cost.** Medium-high integration cost. It changes every multi-worker MOVE resolution, not only the
20 red rows.

**Risk.** Broad command-stream drift, especially on narrow corridors; non-negative progress can
refuse a temporarily necessary retreat. The source's value closure means no score claim should be
attached.

**Falsification.** Exact 20-row replay plus exhaustive small-map tests must show no static period-2,
shuffle invariance, preserved legal swaps/chains and no new terminal WAIT deadlock.

**Owner needed?** No for analysis/implementation; owner for changing acceptance or live platform.

### C. Elost tree ownership plus route exclusion

**Change.** A capable worker standing on a live plant owns that plant and its work cell until the
plant/action completes or the worker cannot service it. Other workers cannot target that plant and
compute route distance with the claimed cell removed or penalized as a stationary obstacle.

**Expected effect.** High for the dominant parked-peer family; likely eliminates most or all
terminal rows if the observed parked-on-plant precondition is causal.

**Cost.** Low-medium.

**Risk.** A claimed cell may be an articulation point. Removing it can make useful targets appear
unreachable. It can also forbid beneficial stacked chop behavior, although this candidate already
prefers distinct targets.

**Falsification.** Any terminal episode whose parked peer owns a plant under the new rule, or a
regression where a target becomes permanently unreachable solely because a claimant could have
moved aside safely.

**Owner needed?** No for a candidate experiment.

### D. Feed resolver failure back into target validity

**Change.** Persist per unit: assigned target, expected landing/distance, actual landing, consecutive
resolver overrides and no-progress count. After two failed/overridden turns, invalidate or
cool-down the target and recompute jointly. Do not allow the same target to return until a named
world change or expiry.

**Expected effect.** High on terminal persistence even if the first detour still occurs. The loop
cannot remain a fixed point indefinitely.

**Cost.** Medium; adds state and reset rules.

**Risk.** Incorrect reset semantics create stale blacklist or target flapping. A cooldown can shift
the loop between two targets rather than remove it.

**Falsification.** A target is reselected before its invalidation condition clears, or any terminal
loop persists with the blocked counter crossing the threshold.

**Owner needed?** No for implementation; telemetry/gate changes require review.

### E. Explicit period-2 movement guard

**Change.** Store the last two realized cells and whether a progress event occurred. Before emitting
a MOVE whose predicted landing returns to the previous cell without progress, choose a different
landing, stay and invalidate, or force replanning.

**Expected effect.** Directly catches all exact A-B-A shapes, so high on the measured terminal set.

**Cost.** Low.

**Risk.** Symptom repair: may create A-B-C-A loops, permanent WAIT, or block a legitimate shuttle
that produces progress just outside the detector's event model.

**Falsification.** Any zero-progress period-2 survives; any new longer-period or permanent-WAIT
terminal episode appears.

**Owner needed?** No for an experiment. Not sufficient by itself for the owner's control objective.

### F. Previous-cell taboo in the detour tie-break

**Change.** When the direct landing is blocked, exclude the cell occupied on the previous turn if
another legal detour exists.

**Expected effect.** Likely removes many A-B-A cases.

**Cost.** Very low.

**Risk.** Converts two-cycles into three-cycles or into non-convergent wandering; can block the only
safe retreat in a corridor.

**Falsification.** Exact terminal set does not go to zero, or cycle-period scan finds replacement
periods.

**Owner needed?** No. I would not choose this as the primary fix.

### G. Unit-specific or turn-parity symmetry-breaking salt

**Change.** Add unit id or turn parity to detour ordering.

**Expected effect.** Uncertain. Unit-id salt can separate two movers; turn parity can create the
oscillation by construction.

**Cost.** Very low.

**Risk.** Hides deterministic repetition without establishing a decreasing potential. Turn parity
is especially dangerous.

**Falsification.** Any terminal episode or strong seed/order sensitivity.

**Owner needed?** No. Reject as a standalone repair.

### H. Move the blocker / support swaps and chains

**Change.** When a stationary worker occupies the only progressive landing, jointly decide whether
the blocker can finish, sidestep or participate in a swap/chain rather than always detouring the
mover.

**Expected effect.** High on choke corridors where one worker is parked on the route.

**Cost.** Medium-high; requires task-priority arbitration.

**Risk.** Interrupts a productive CHOP/HARVEST to help a lower-value mover; can cause both workers
to churn.

**Falsification.** The blocker is displaced repeatedly without aggregate task progress, or terminal
loops survive because the blocker is never eligible to move.

**Owner needed?** No for implementation.

### I. Change the gate from raw D-1=0 to terminal-D-1=0

**Change.** Permit short self-resolving episodes, block only the frozen terminal mode.

**Expected effect.** It does not change the bot and therefore eliminates zero terminal episodes.
It would reduce instrument friction from short episodes.

**Cost.** Low engineering cost.

**Risk.** Optimizes the requirement rather than control. Threshold boundaries can be gamed; a
61-turn deadlock is still severe. D-1 truth validity is not currently established strongly enough
to ratify a new threshold casually.

**Falsification.** Short episodes are shown to cause material missed work, or terminal behavior
appears just below the chosen threshold.

**Owner needed?** Yes. Under the task's binding ranking, this is not a substitute for bot repair.

### J. Change D-1's progress predicate

**Change.** Add target-distance progress, successful resolver landing, or partner-level work; or
exclude pacing while a peer is productive.

**Expected effect.** Detector counts may fall; bot behavior is unchanged.

**Cost.** Medium because target telemetry is absent and independent truth labels are required.

**Risk.** The detector can become green while one worker wastes 194 turns. Partner progress is not
unit progress.

**Falsification.** Any excluded episode still has a worker trapped for a terminal interval or loses
reachable work.

**Owner needed?** Yes for detector/gate semantics.

### K. Harness and corpus changes

**Change.** Freeze the exact terminal states as motion microfixtures; add small connected-map
enumeration of two workers, stationary work cells, goals, speeds and priority orders; retain
aggressive and non-aggressive opponent strata.

**Expected effect.** Does not change behavior, but makes every architectural fix falsifiable and
prevents regression.

**Cost.** Medium one-time test work.

**Risk.** Overfitting only the 20 rows unless paired with generated local-state coverage.

**Falsification.** A supposedly fixed resolver fails a generated static-state period-2 test or a
new floor row outside the frozen set.

**Owner needed?** Corpus re-versioning/integration requires coordinator review, not an Arena ruling.

### L. Do nothing

**Change.** None.

**Expected effect.** All 20 terminal episodes remain.

**Cost.** Zero.

**Risk.** Leaves a known 194-turn loss of control and blocks the owner's instrument programme.

**Falsification.** Not applicable; this is a priority choice. It is defensible on value grounds
alone, but the owner explicitly chose technical-debt/control grounds, so I reject it for this task.

## 4. Recommended plan

### Stage 1 — freeze the failure as a motion contract

Before behavior changes, commit:

1. the exact 20 terminal episode identities and minimal state slices around entry;
2. a pure resolver/planner microfixture for each distinct local geometry;
3. generated two-worker static-state tests asserting no zero-progress period-2 under fixed goals;
4. swap/chain and narrow-corridor controls that a conservative fix must preserve.

The current panel's TRAIN defect does not invalidate these D-1 rows: the defect is confined to
`m040`, which contributes no D-1 episode. This does **not** make the panel globally ready; it makes
these exact D-1 traces usable as scoped red evidence.

### Stage 2 — implement the structural seam fix first

My first implementation arm would combine:

- the Gold joint landing solver's stationary-obstacle, stay and whole-vector semantics;
- the existing candidate's pairwise target enumeration;
- explicit route/landing compatibility;
- Elost ownership of a worker's current live-tree cell;
- blocked-target feedback after a resolver override.

Do **not** port the same-position watchdog as the claimed D-1 fix. Add a period-2 guard only as a
last-resort assertion/safety layer after the structural change.

### Stage 3 — acceptance

A correct implementation must satisfy all of:

- **20/20 terminal episodes eliminated**;
- no new terminal D-1 episode anywhere in the 240-row D-1 corpus;
- no static period-2 in generated motion microstates;
- deterministic/shuffle-invariant joint result;
- swap and vacated-cell-chain controls preserved;
- no replacement permanent-WAIT or longer-period terminal stall;
- exact command/result evidence committed.

“Fewer episodes” is a failed result. Value improvement is not claimed or required. Any eventual
promotion remains a separate owner action.

## 5. What I would not do first

- I would not relax raw D-1 before gaining control of the terminal mode.
- I would not port the Gold watchdog verbatim and call the job done.
- I would not add turn parity or random detours.
- I would not treat target exclusivity as new; it already exists.
- I would not accept a fix that converts A-B-A into WAIT or a longer cycle.

## Final answer

The terminal oscillation is best understood as a **planner/resolver contract failure**, not just a
missing-memory line in the detour function. The bot jointly chooses distinct targets, then a
sequential resolver silently invents a different one-turn plan and discards the fact that the
original action was not executable. Repeating two stateless optimizations over a static board
creates the deterministic A-B-A fixed point.

The preferred repair is to plan executable landings jointly, treat working-peer cells as owned
stationary obstacles, and feed resolver failure back into target validity. A period-2 memory guard
is useful insurance but not the architecture. Detector/harness changes are secondary; relaxing the
gate or doing nothing does not satisfy the owner's stated objective of regaining control.
