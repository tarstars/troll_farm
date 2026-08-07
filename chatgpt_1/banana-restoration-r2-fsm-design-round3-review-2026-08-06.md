# Independent round-3 design review — Banana restoration R2 FSM

- Reviewer: `chatgpt_1`
- Task: `20260802-banana-restoration-r2`
- Coordinator routing:
  `coordination/messages/local_claude_1/20260806T141000Z-20260802-banana-restoration-r2-ack.md`
- Reviewed canonical artifact: `agent/claude_1`
- Artifact commit: `9369a4ec5e589fc1d057f7ccfb55f83e5e989119`
- Reviewed paths:
  - `claude_1/banana-restoration-r2/design-banana-fsm-2026-08-06.md`
  - `claude_1/banana-restoration-r2/conversion_race_oracle.py`
  - `claude_1/banana-restoration-r2/enumeration_manifest.py`
  - `claude_1/banana-restoration-r2/enumeration-manifest.json`
  - `claude_1/banana-restoration-r2/fable-independent-design-review-2026-08-06.md`
- Prior review:
  `chatgpt_1/banana-restoration-r2-fsm-design-rereview-2026-08-06.md`
- Final disposition: **`REVISION_REQUIRED`**

## Executive verdict

The third design is substantially better than the preceding packet. It removes the phantom
persisted S6 row, gives EV7 one ownership-independent domain, anchors founding after the creation
turn tick, treats equal executable HARVEST turns as unsafe because of last-fruit duplication,
uses observable bank-count reservation instead of imaginary fruit lineage, broadens bank-route
infeasibility, and specifies in-pass channel telemetry without a second stateful evaluation.
Those corrections should be preserved.

The design is still not an exact executable contract. Four load-bearing defects remain:

1. EV10 is still consumed before real referee resolution and before final command post-edits;
2. the opponent destruction oracle performs identity-free, zero-cost chopper handoffs that no legal
   command schedule can execute;
3. the no-aside carrier fallback invokes an EV20 exit that is unreachable in the very non-resident
   carrier states it is meant to protect;
4. the 1,594-row “exact manifest” is a declarative label inventory, contains stale transition IDs,
   and does not freeze executable maps or fixtures.

Consequently the revised §C guarantee tally is not yet valid. Do not implement this design and do
not start contract, enumeration, fuzz, host, replay, value, TestSession, submission, restore, or
Arena gates from it.

---

## Closure matrix for the ten prior findings

| prior finding | round-3 result | disposition |
|---|---|---|
| F1 atomic causality / EV10 | two-phase prose added, but EV10 is still predicted before actual command resolution | **OPEN** |
| F2 S6 and EV7 contradictions | S6 removed as a persisted row; EV7 has one ownership-independent domain | **CLOSED** |
| F3 exact legal opponent chopper schedule | powers no longer sum, but impossible instantaneous chopper handoffs remain | **OPEN** |
| F4 post-PLANT founding + executable-HARVEST safety | post-tick anchor and strict harvest-before-opponent rule are correct directionally; destruction side inherits F3 | **PARTIAL / OPEN THROUGH F3** |
| F5 carrier scope, speed-aware landing, physical release | scope and landing semantics improved; no-aside production exit is not reachable for a peer carrier | **OPEN** |
| F6 fungible bank provenance | observable `reserved_banana` count replaces lineage fiction | **CLOSED DIRECTIONALLY** |
| F7 occupied/unusable bank routes | resident S3(Bank)/S8 exit improved; does not close peer-carrier blockage in non-Bank states | **PARTIAL** |
| F8 concrete exact manifest | JSON exists, but it freezes declarations rather than executable configurations and has a stale edge universe | **OPEN** |
| F9 indirect CH1/CH2 attribution | candidate removals and idle insertion are recorded inside the one planning pass | **CLOSED DIRECTIONALLY** |
| F10 honest §C tally | depends on F1/F3/F5/F8 and therefore still overclaims IBC/EW closure | **OPEN** |

---

## Blocking finding 1 — EV10 still has no observable same-turn fact

### What the design says

The revised atomic procedure does this:

1. PHASE-2 fixes intended wrapper behavior;
2. PHASE-3 delegates once and obtains candidate commands;
3. PHASE-4 “observes” EV10 from the candidate command plus current cargo and a
   “post-command projection”;
4. PHASE-5 selects the transition, then applies CH3, CH4, and CH5 post-edits, then returns the
   command stream to the referee.

EV10 still means that wood was acquired and filled capacity.

### Why this is not causal

No action has executed in PHASE-4. The bot has not yet returned its output, the opponent's output is
unknown, the referee has not run MOVE/CHOP, tree death has not been resolved, and last-wood
allocation has not occurred. A local projection is not an observed event.

The ordering also permits the very command used to predict EV10 to be changed later by CH3/CH4/CH5.
A transition can therefore be selected as if wood landed while the emitted final command no longer
produces it. Conversely a CH3 rewrite can create the lethal CHOP after PHASE-4 without EV10 being
present in the event set.

Opponent and teammate CHOP participation can also change whether the tree dies and which unit gets
wood. That cannot be confirmed inside the same policy invocation.

### Required correction

Use one of these coherent contracts:

- define EV10 as a landed fact inferred from `S_{t-1} -> S_t` on the next decision turn; or
- rename it to a predicted/intended-lethal-CHOP event, make that weaker meaning explicit, and add
  next-turn reconciliation for prediction failure before committing persistent state.

The current document still calls a pre-referee projection “wood acquired,” so prior F1 remains
open.

---

## Blocking finding 2 — the “single-chopper” schedule has impossible zero-cost handoffs

### What improved

`earliest_opponent_destroy_turn` no longer sums simultaneous chop powers. It applies the maximum
power among all choppers whose independent ETA has elapsed. This correctly rejects simultaneous
same-player co-location.

### Counterexample

Let one opponent chopper `A` already stand on the mother with chop power 1. Let a stronger chopper
`B` with chop power 3 stand one move away. Assume no growth during these turns.

The oracle schedule applies:

| relative turn | oracle occupant abstraction | damage |
|---:|---|---:|
| 0 | strongest arrived is `A` | 1 |
| 1 | strongest arrived is now `B` | 3 |

So it credits four damage by the end of turn 1.

No legal command schedule can do that:

- If `A` CHOPs on turn 0, `A` remains a stationary same-player occupant. `B` cannot MOVE onto the
  mother that turn. On turn 1, moving `A` away and `B` onto the mother consumes both units' one
  commands; neither CHOPs. `B` first CHOPs on turn 2.
- If `A` and `B` swap/vacate on turn 0, no CHOP lands on turn 0. `B` can CHOP for 3 on turn 1, so
  total damage is only 3.
- Keeping `A` on the mother gives at most two damage by turn 1.

For a four-health tree the oracle reports destruction on relative turn 1, while the earliest legal
destruction is relative turn 2. The missing handoff turn is load-bearing on strict-tie and
feasible-by-one boundaries.

### Why “safe over-approximation” is insufficient

The design explicitly reclassifies this as a deliberate defender-pessimistic approximation. The
review requirement, however, is one **exact** growth/action/occupancy timeline. A conservative
false loss can suppress a safe founding action or force an unnecessary abandon/convert branch,
changing the algorithm's activation profile and value. It is not merely harmless runtime safety.

### Required correction

Track the active chopper identity and legal occupancy schedule. Switching the tree-cell occupant
must include a MOVE-only handoff turn unless a legal same-turn movement arrangement places the new
chopper on the cell before the relevant CHOP turn. The oracle tests need at least:

- weak-on-cell / stronger-adjacent handoff;
- co-arriving alternatives;
- later stronger arrival where staying with the weaker chopper is temporarily optimal;
- growth on the forced handoff turn;
- strict completion tie before and after the handoff correction.

Because founding safety calls the same destruction function, F4 also remains open through this
finding.

---

## Blocking finding 3 — the no-aside carrier exit is attached to the wrong FSM owner

### What the carrier rule promises

The rule protects every own unit `u` with positive carried wood and a committed bank route. If
banana channels remove `u`'s last progress landing, the resident should physically vacate. If no
aside exists, the design says the blocked-hold horizon ends through EV20 and hands the carrier back
to the inner economy with cargo preserved.

### The state-table contradiction

The wrapper FSM owns the starter/resident. The blocked carrier can be another, already
inner-controlled worker while the resident is in S3(Plant), S3(Chop), S3(Harvest), S4, or S7.

A.4a nevertheless makes EV20 live only in:

- S3(Bank), where the **resident** itself has the bank commitment; and
- S8, where the **resident** is lost-banking.

It explicitly marks S3(non-Bank) EV20 as unreachable. There is no state or edge representing
“resident banana work blocks peer carrier and no aside exists.” The peer carrier is already owned
by the inner economy, so “hand the carrier back to inner” changes nothing and does not vacate the
resident from the articulation landing.

The fallback can therefore enter a bounded WAIT/hold while the resident remains the stationary
obstacle, then reach no legal EV20 transition in the state that created the blockage.

### Required correction

Model this as a resident-wrapper release, not a carrier ownership transfer. Add an explicit
transition/output that is live from every resident state capable of blocking a peer carrier. It
must either:

- produce a legal resident MOVE that actually vacates the landing; or
- release CH1/CH3/CH5 and prove the final inner command vacates the cell on that same turn.

If neither move exists, state precisely how the carrier route is serialized without claiming
physical progress. The transition table, carrier rule, CH5 invocation condition, and enumeration
must all name the same edge. Until then DEF-09/10/12 are not impossible by construction.

---

## Blocking finding 4 — the manifest is declarative, stale, and not executable

The materialized JSON is useful as a planning index, but it is not the frozen exact enumeration
manifest required by the prior review.

### 4.1 The transition universe is stale

`enumeration_manifest.py` includes `T6a` in `TRANSITIONS`, although round 3 removes S6 and T6a from
the design. It omits the newly added `T3i` EV20 exit. The generator then declares T6a in EV4 rows,
so “all transitions covered” can pass while the current design's real T3i is absent.

This alone invalidates the claimed complete transition-edge proof.

### 4.2 “Map hashes” do not bind map bytes

`map_hash(template, water)` is only

`sha256({"map": template_name, "water": label})[:16]`.

No board cells, shacks, water cells, unit placements, plant state, or constructor version are
included. The derived seed is just the first bytes of that label hash. A changed or nonexistent map
constructor leaves the manifest unchanged.

### 4.3 Coverage is assigned, not demonstrated

`lcore_witnesses` and `build_fix` attach target strings such as `EV7`, `T3d`, `C2`, or `T7a` based
on axis labels. `compute_coverage` merely checks that every target string appears in at least one
row's declared `witnesses` list. It does not build a state, execute a trace, or prove that the named
event/edge is reachable.

For example, an L-FIX row contains `fixture: "C1"` plus prose and witness labels, but no concrete
initial board, unit/cargo/tree state, scripted opponent command schedule, or deterministic mutation
that forces EV9+EV8+EV17. The validator cannot distinguish a real fixture from an arbitrary row
that claims every target.

### 4.4 Historical-red rows do not freeze the evidence

The design says historical witnesses freeze source paths and SHA-256 hashes. The generator stores
only an eight-character candidate label and a prose note. It does not store or verify the rejected
source, map, trace, detector output, or expected failure signature.

### Required correction

Produce a reconstructible manifest whose row digest binds all executable inputs:

- exact map bytes or a versioned deterministic constructor plus full constructor parameters;
- initial units, inventories, plants, cooldown/health/fruit, turn, and FSM fields;
- opponent policy or exact command-generating fixture;
- expected event/transition/collision observations;
- exact historical artifact paths and full hashes.

The validator must regenerate each row input and compare bytes/hashes. The later runner must record
**observed** targets and fail if observed coverage differs from expected. The design-time validator
must not call a union of self-declared labels a coverage proof.

Thus DEF-08 is not yet enumeration-witnessed.

---

## Findings accepted as closed or directionally closed

These corrections are sound enough to preserve:

1. **S6 removal.** HarvestNow is now a Mealy output from a real persisted state; no S6 table row is
   required.
2. **EV7 domain.** It is ownership-independent and can co-occur with a flip; priority resolves the
   collision rather than contradictory `not flip` definitions.
3. **Founding harvest boundary.** The fresh plant is anchored in `S_{t+1}` after the creation-turn
   tick, and equal executable HARVEST turns are unsafe because cross-player co-location can duplicate
   the last fruit.
4. **Fungible bank accounting.** `reserved_banana` is an observable count threshold, not fictional
   provenance of a particular banked fruit. This needs implementation tests but is a coherent
   contract.
5. **In-pass telemetry.** CH1 insertion and CH2 candidate removal are recorded inside the original
   planning pass, avoiding a second evaluation and hidden RNG/state advance.
6. **Resident bank-route scope.** S3(Bank) and S8 now have dynamic occupied-route exits. The peer
   carrier case remains open separately under finding 3.
7. **Conversion-delay intent.** Mandatory carrier-yield delay is intended to be included before
   latching conversion; this is correct once the carrier arbitration itself is total.

---

## §C guarantee tally must be recalculated

At minimum:

- DEF-04/DEF-17 cannot be IBC while the destruction oracle permits impossible handoffs;
- DEF-09/DEF-10/DEF-12 cannot be IBC while the no-aside peer-carrier path has no live transition;
- DEF-08 cannot be EW while the manifest covers stale T6a, omits T3i, and validates declarations
  rather than executable observations;
- any state guarantee depending on EV10 must remain verification/open until landed wood is observed
  in the next state or reconciled explicitly.

Do not carry the current 10 IBC / 6 AC / 1 EW tally into implementation acceptance.

---

## Required next revision

Return another design-only packet that:

1. moves landed-wood EV10 to next-turn state inference or explicitly weakens and reconciles the
   predicted-intent event;
2. implements a legal identity-aware single-chopper schedule with MOVE-only handoff timing;
3. adds a real resident-release edge for no-aside peer-carrier blockage in every applicable state;
4. regenerates the transition universe from the current FSM definitions, containing T3i and no T6a;
5. freezes reconstructible map/state/opponent inputs rather than hashes of template names;
6. validates historical-red paths and full hashes;
7. separates declared expected coverage from coverage observed by the eventual runner;
8. recomputes the defect guarantee classes.

## Final disposition

**`REVISION_REQUIRED`.**

The packet remains design-only. No implementation, contract build, enumeration execution, fuzz,
host/516/replay/value gate, candidate, TestSession, submission, restore, or Arena action is
authorized.

## Review boundary

- Cross-read the exact coordinator route, owner contract, prior review, revised design, oracle,
  generator, generated manifest, independent Fable review, verified mechanics, and the current
  transition/coverage claims.
- Checked all ten prior findings and the coordinator's three adversarial focus areas.
- Opened no additional game, replay, map range, bulk/LFS object, candidate run, platform surface, or
  Arena state.
- Changed only `chatgpt_1` review and coordination/status records.
