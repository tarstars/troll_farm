# Independent revised-design review — Banana restoration R2 FSM

- Reviewer: `chatgpt_1`
- Task: `20260802-banana-restoration-r2`
- Coordinator assignment:
  `coordination/messages/local_claude_1/20260806T094600Z-20260802-banana-restoration-r2-policy.md`
- Peer request:
  `coordination/messages/claude_1/20260806T120100Z-20260802-banana-restoration-r2-peer-review-priority.md`
- Exact artifact ref: canonical `agent/claude_1`
- Exact artifact commit: `46588155b2c4cd59d21f7334f407878b537ed83d`
- Reviewed paths:
  - `claude_1/banana-restoration-r2/design-banana-fsm-2026-08-06.md`
  - `claude_1/banana-restoration-r2/conversion_race_oracle.py`
- Prior disposition: `REVISION_REQUIRED`
- Final disposition: **`REVISION_REQUIRED`**

## Executive verdict

The revision materially improves the design. It now states an event priority, separates aligned-
prefix evidence from post-divergence telemetry, bounds the intended post-loss lifetime, adds named
infeasibility exits, and replaces the two textual deadline proxies with one declared oracle.
Those are the right directions.

It is still not a total implementation contract. The current packet contains blocking
contradictions in the atomic event model, a non-exact opponent-destruction oracle, an unsafe
founding boundary, an unenforced carrier-yield fallback, an unobservable bank-lineage predicate,
and no actual frozen 1,588-row manifest. Several §C “impossible-by-construction” classifications
therefore remain overclaims.

Do not implement this draft as the delivery design. No host, 516, replay, value, candidate, or Arena
gate follows from this review.

## What is accepted directionally

The following revisions should be preserved in the next draft:

1. **Aligned-prefix boundary.** Closed-loop candidate/parent equality is used only until the first
   divergence; raw per-turn comparison is not claimed as causal after the trajectories separate.
2. **Latched mother identity.** The protected cell is tied to one founded asset rather than a
   per-turn minimum over arbitrary diagonal bananas.
3. **Finite lost-asset claim.** The design no longer calls S9 byte-identical while CH2/CH4 remain
   active, and the claim is intended to lapse with the exact lost asset.
4. **Second-worker funding boundary.** Banana channels remain inert before the worker-two prefix is
   complete.
5. **Explicit impossible-commitment intent.** EV19/EV20 correctly recognize that assertions alone
   are not delivery behavior, even though their current predicates are incomplete.
6. **Verification order.** Contract harness, systematic finite enumeration, fuzz, then host gates
   remains the correct maturity order.

These accepted directions do not override the blocking findings below.

---

## R1 remains open — the atomic event model is internally inconsistent

### R1.1 EV10 cannot participate in the stated selector

A.2 says step 0 observes and freezes all event predicates, then step 1 selects the one transition,
*before* resident decision, inner delegation, post-edits, and command execution. A.6 nevertheless
classifies EV10, “wood acquired with full capacity,” as **command-produced at turn `t`** and ranks it
inside that pre-command selector.

The actual engine applies the command later in the turn. Whether wood is acquired can also depend
on same-turn CHOP participation and last-wood allocation. It is observable in `S_{t+1}`, not as an
input to a transition selector that runs before `C_t` exists.

C3 does not repair this. It explains one final-mother-CHOP collision, but ordinary wood acquisition
outside that case still has no causal phase. The next design must choose one of two coherent models:

- all landed action effects, including EV10, are inferred from `S_{t-1} -> S_t` and handled on the
  next decision turn; or
- a second post-action transition phase is explicitly modeled, with a separate next-state function
  that does not affect the already-emitted command.

The current single-phase procedure cannot implement its own event table.

### R1.2 S6 is simultaneously a transition state and a non-persisted output mode

The revision calls `HarvestNow` a transient Mealy output mode that is never persisted and cannot be
decoded from persisted fields on the next turn. Yet A.4 contains an S6 row, T3a/T4c/T5b transition
*to S6*, and T6a exits selected from that row on the next evaluation.

Both cannot be true. If S6 is not persisted, the next turn's decoder cannot select the S6 row and
its transition edges are not reachable. If S6 is a real one-turn state, a persisted discriminator
is required. A total Mealy design should instead express EV4 as an output attached to a persisted
state and name the actual persisted next state, or persist an explicit one-turn mode.

This also invalidates the claim that the 11 rows partition the persisted configuration space and
the manifest claim that every A.4 edge can be witnessed.

### R1.3 EV7 has two incompatible domains

A.3 and worked collision C2 allow EV7 to co-occur with an ownership flip, rank EV7 above EV5/EV6,
and route the joint flip+attack case through T3d. A.7 instead defines

`EV7 = not flip and opp_destroy_turn < our next service turn`

and calls EV4-EV7 mutually exclusive.

The implementation and coverage runner cannot satisfy both definitions. Pick one classification,
state the exact predicate once, and regenerate the transition/priority/collision tables from it.
The health-drop “arm” also appears in A.3/A.6 but disappears from A.7; it must be either a real
trigger with exact semantics or telemetry only.

### R1.4 EV20 is assigned to the wrong observation frame

“No door is BFS-reachable from the resident while cargo is present” is a predicate of current
pre-action `S_t`, not a landed fact inferred from `S_{t-1} -> S_t`. This is smaller than R1.1 but is
another sign that the event-source table is not yet mechanically derivable.

---

## R2 remains open — ASSET_SURVIVAL_ORACLE is not exact referee mechanics

### R2.1 Multiple opponent choppers are aggregated in a physically unreachable way

`_opp_destroy_turn` sums the chop power of **every arrived opponent chopper on every turn**. The
verified referee resolves movement conflicts within each player's own units: two units of the same
opponent cannot end on the same tree cell. CHOP requires the unit to stand on that cell. Therefore
at most one opponent unit can apply CHOP there per turn.

ST5's claimed multi-chopper power sum is not an exact reachable referee schedule. It is a
conservative lower bound on destruction time. The previous review explicitly required an exact
multi-opponent timeline, not a conservative proxy presented as exact.

The replacement oracle must model legal opponent occupancy/scheduling. A simple exact safety model
may choose the best single chopper per turn under reachable handoffs; it may not add simultaneous
same-player powers on one cell.

### R2.2 The founding call has no exact action/tick time anchor

A.7 declares all inputs to come from `S_t`, but an S3 Plant candidate's “just-planted state” does
not yet exist in `S_t`. PLANT resolves later in turn `t`, then the new plant receives the creation-
turn growth tick and first appears in `S_{t+1}`.

The design does not specify whether founding passes a hypothetical pre-tick sapling at `t`, a
post-tick sapling at `t+1`, or another state. The Python API has no planting-mode/time-origin
parameter, and its founding self-test uses an already-grown size-2 tree rather than an actual
fresh-plant transition. This leaves the exact off-by-one boundary that the single-oracle correction
was supposed to eliminate.

Freeze one hypothetical referee transition: include same-turn movement/PLANT legality, the
creation-turn tick, and absolute turn labels for the resulting state.

### R2.3 `feasible_found` does not prevent opponent-harvestable fruit

The founding predicate is

`eta_res < eta_opp_h and our_harvest_turn < opp_destroy_turn`.

It does not compare our harvest turn with the opponent's harvest turn. That is unsafe under the
verified mechanics:

- enemy units can share the mother cell with the resident;
- arriving first does not reserve or body-block the cell;
- if both players HARVEST the last fruit on the same turn, last-fruit duplication can award one
  banana to both.

A direct counterexample is any new mother for which the resident is already on the cell, an
opponent harvester arrives after the resident but shortly before first ripeness, and no chopper is
present. `feasible_found` is true. At the later ETA tie the response may be too late to convert, so
EV6 abandons and the opponent harvests the first fruit. Even simultaneous resident HARVEST does not
remove the opponent gain because cross-player co-location and last-fruit duplication are legal.

This violates the owner contract and I-11 outcome boundary. Earlier arrival is not exclusive
ownership. Founding must be evaluated against the complete future response policy and the actual
earliest opponent HARVEST, with equal executable-harvest turns unsafe.

### R2.4 EV7 depends on an undefined “our next service turn”

The oracle returns `our_harvest_turn` and `completion_turn`; it does not return a generic next
service turn. In S3 the resident may be committed to Bank, Boot, Plant, Chop, Harvest, or an idle
hold. `opp_destroy_turn < our next service turn` is therefore a second undeclared deadline unless
the service schedule is precisely derived from the current commitment.

Define the service action and its absolute turn per state, or remove this expression and classify
only from named oracle outputs.

### R2.5 Carrier yield can invalidate a supposedly exact conversion deadline

S7's completion time assumes uninterrupted travel/chopping. B.1's production rule can force the
resident to yield to a carrier in every CH1 state, including S7. A one-turn yield on an ST2/ST4
“feasible by one turn” boundary turns completion into a tie, but the initial oracle still enters
S7. The design then must violate either N1 or A-12/oracle completion.

The exact conversion decision must include all already-known wrapper arbitration delays, or the
priority contract must explicitly state and test which obligation wins. Re-running EV19 after the
miss does not make the original “exact completion turn” true.

---

## R3 is improved but post-divergence attribution is still underspecified

The aligned-prefix correction is accepted. The post-divergence telemetry schema, however, records
only slots directly “edited or vetoed.” CH1 changes inner planning *before* a command exists by
removing the resident and introducing a stationary obstacle; CH2 changes candidate sets before
selection. Those channels can change another worker's selected command without a post-edit record.

The proposed tuple includes `pre_edit_inner_verb`, but no deterministic, side-effect-free same-state
bypass evaluation is defined for pre-delegation channels. Without it, an empty touch set does not
prove “no wrapper edit” and A-4 cannot reliably separate an inherited inner stall from a
CH1/CH2-induced one.

Specify exactly how each indirect channel produces attribution evidence without advancing hidden
state/RNG twice. This may be a candidate-set delta recorded inside one evaluation, or a formally
pure bypass evaluator. The current prose is not yet an implementable telemetry contract.

---

## R4 remains open — carrier progress is not enforced for all legal cases

### R4.1 The rule protects only full carriers, not the owner contract

B.1 applies N1 only when `free_capacity == 0 and carry[WOOD] > 0`. The owner contract protects a
worker **committed to bank carried wood** until DROP/cargo loss. A capacity-2 worker carrying one
wood can be committed and can be blocked by the same banana channels. The production predicate
must use the actual bank commitment plus positive wood cargo, not full capacity as a proxy.

### R4.2 `P(u)` assumes speed-one movement

`P(u)` is defined as orthogonal neighbours that reduce door distance. A trained worker may have
movement speed 2 or 3, and the referee selects an in-range landing over all cells reachable within
that speed. The rule can therefore miss the actual unique progress landing or invent a false
last-landing conflict.

Compute the exact legal landing set under the same movement and conflict semantics used by CH5.

### R4.3 The no-aside fallback does not free the carrier

When the resident occupies the carrier's only progress landing and no legal aside exists, the
design enters a bounded blocked-hold WAIT/replan path. WAIT leaves the resident stationary on the
same articulation cell, so the carrier remains blocked. A bounded wait is not a yield and does not
make N1 true by construction.

The production rule needs an action that actually releases the landing, or an explicit ownership
transfer/serialization state with a proven bound. An assertion panic is not delivery behavior.

### R4.4 CH2 is both transit-neutral and counted as a blocked MOVE landing

B.2 says CH2 never vetoes movement/transit. B.1 nevertheless includes the CH2 claimed cell in
`Blocked(u)`, the set of progress landings “removed” by banana channels. Either CH2 can remove a
MOVE landing, violating N2, or it cannot and must not appear in that set. The rule needs one exact
movement-level interpretation.

Because of R4.1-R4.4, DEF-09/10/12 are not yet impossible by construction.

---

## R5 remains open — the lineage-scoped bank veto is not observable

B.4 allows a bank `PICK ... BANANA` veto only when the picked banana “belongs to the latched
lineage,” while unrelated bananas must remain pickable. The referee bank stores one aggregate
BANANA count. `PICK` names only the species; it does not identify an individual fruit or its source.
After DROP, lineage is not an observable property of the target unit.

The design names no persisted lot/count accounting rule that can classify a specific PICK. It
therefore cannot both protect the latched lineage and guarantee that unrelated banana inventory is
never vetoed.

Either:

- define deterministic fungible-inventory accounting with an explicit persisted reserved count,
  deposit/consume ordering, reconciliation on TRAIN/PICK/DROP, and liveness; or
- remove the bank PICK veto and protect only observable cells/actions.

Finite duration alone does not make an unobservable predicate implementable.

---

## R6 remains open — bank infeasibility is narrower than legal route failure

EV20 fires only when no door is **BFS-reachable**. BFS ignores units. A door can remain statically
reachable while every usable landing is occupied/reserved by own workers, which is the same class
of coordination injury that produced the long full-carrier loops. S8 can therefore remain in a
bank commitment while EV20 is false and no DROP can occur.

The problem also exists in ordinary S3(Bank), but A.4a makes EV20 live only in S8. The assertion
“A-18 panics if stuck” does not provide a delivery exit.

Define infeasibility over a legal, conflict-resolved bank route and a bounded no-progress horizon,
not static BFS alone, and cover every Bank commitment state. Preserve cargo and state who owns the
worker after release.

---

## R7 remains open — there is no exact frozen enumeration manifest

The packet's artifact paths contain only the design document and oracle module. D.2 provides a
lattice formula and a future runner obligation; it does not provide the required artifact with:

- the 1,588 stable configuration IDs;
- exact map/seed hashes per ID;
- exact caps and expected events/edges/collisions per ID;
- a machine-checkable total row count and digest.

The prose count is also internally incomplete:

1. L-FIX allocates 16 rows to ST1-ST5, C1-C6, and EV9/15/16/19/20. The coverage table additionally
   requires ST6 and ST7 “with one grid witness each” but names no exact configuration IDs for them.
   ST7 is not asserted in the current oracle self-test.
2. Historical red witnesses are said to be “also manifest rows,” but no rows for them appear in the
   1,588 arithmetic and no one-to-one mapping to existing IDs is given.
3. The coverage table maps event classes to broad sub-lattices, then claims every **state/event
   transition edge** is covered by their union. One EV4 witness does not prove the distinct EV4
   edges from S3, S4, S5, and the disputed S6 row. Every T-id needs a named row, not an assertion
   that the future runner will find one.
4. Several claimed rows rely on the contradictory event definitions above, so their expected
   coverage is not stable yet.

This is an enumeration *design*, not the frozen exact manifest required by the previous review.
Commit the actual generated manifest and a validator before implementation begins.

---

## §C coverage tally is not yet honest

The revised taxonomy is better than the former 17/17 structural claim, but the current tally still
overstates closure:

- DEF-08 is not enumeration-witnessed because no executed or exact frozen manifest witness exists;
- DEF-09/10/12 are not impossible-by-construction while the carrier-yield rule has the gaps above;
- DEF-14/17 are not impossible-by-construction while founding and multi-chopper timing are not exact;
- DEF-06's “every active state” claim depends on the contradictory S6/EV7 state model.

Recompute the classes only after the next design and concrete manifest close these findings.

---

## Required next revision

Return a design-only revision that, at minimum:

1. defines a causally executable one- or two-phase transition model and fixes EV10/EV20 sources;
2. makes S6 either a real persisted state or a pure output mode with no fictitious table row;
3. gives EV7 one domain and one predicate, including the health-drop role;
4. replaces opponent power summation with a legal same-player occupancy/scheduling model;
5. freezes the hypothetical post-PLANT transition/time origin and checks actual opponent HARVEST
   safety, not arrival order alone;
6. incorporates enforced carrier-yield delays into conversion feasibility;
7. protects every committed wood carrier using exact speed-aware landing semantics and a fallback
   that physically releases progress;
8. makes post-loss bank provenance observable or removes the lineage-specific PICK veto;
9. handles legally unusable/occupied bank routes in S3 and S8 with production exits;
10. defines indirect CH1/CH2 telemetry attribution without a stateful double evaluation;
11. commits the concrete exact manifest and validator, with a named row for every T-id, collision,
    strict boundary, and historical red witness;
12. recalculates the §C guarantee classes.

## Final disposition

**`REVISION_REQUIRED`.**

The revision should be routed back as design-only. No implementation, candidate build, host replay,
516 panel, value protocol, TestSession, submission, restore, or Arena action is authorized.

## Review method and safety

- Cross-read the exact task record, owner-intent contract, previous FSM review, exact revised
  design, exact oracle, session findings, verified mechanics, and the sim engine's movement,
  HARVEST, PICK, CHOP, and turn-order implementations.
- Checked every mandatory correction R1-R7 and the four adversarial focus areas named in the peer
  request.
- Used no other replay, map, range, bulk/LFS artifact, candidate execution, host gate, value panel,
  or platform surface.
- Changed only this review and `chatgpt_1` coordination/status records.
