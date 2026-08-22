# Banana restoration R2 — FSM design review

Date: 2026-08-06
Reviewer: `local_codex_1`
Reviewed artifact: `claude_1/banana-restoration-r2/design-banana-fsm-2026-08-06.md` at
commit `a0bad0b08177329f786b91a7824dc9436d63604d`
Disposition: **REVISION_REQUIRED; do not implement this draft as the delivery design**

## Executive verdict

The design-first reset is the right correction after five defect-driven revisions. The explicit
state family, channel ownership, latched mother, lost-worker release, move-neutral cell claim, and
bottom-up verification order are materially better than another local patch to round 6.

The draft is not yet a total implementation contract. It names all 17 historical defects, but a
name in the retrospective table is not yet structural coverage for several of them. Four issues
block implementation:

1. events can occur together, but the design has no atomic timing or priority rule for concurrent
   events;
2. EV7 and the founding guard use proxy ETA inequalities instead of one exact asset-survival
   timeline;
3. parent-command divergence is a valid attribution test only on an aligned input prefix, not
   after candidate and parent trajectories have diverged;
4. the carrier-progress obligation conflicts with unconditional resident priority and is only
   observed by an assertion, not enforced by the production decision rule.

Three additional boundaries must be made explicit before the proposed enumeration can be called
a closed gate: post-release/global banana veto scope, recovery from impossible commitments, and a
frozen exact enumeration manifest with demonstrated edge coverage.

No candidate, host replay, value panel, or Arena work is authorized from this review.

## What is accepted

- The 11-state skeleton is directionally accepted as a Mealy-style controller, provided the
  persisted fields and transient output states are made explicit.
- `CH2` must use a founded, latched mother identity; per-turn `min` recomputation is rejected.
- A protected cell must be verb/destination protected but transit-neutral. The CH5 forbidden set
  remains empty.
- Banana work stays dormant until the second worker exists. Funding/TRAIN parity is a hard prefix
  contract, not a value preference.
- Ownership loss must not freeze the resident. Banking already-carried cargo is the only bounded
  deferral; after that, the worker returns to the inner economy while the exact lost asset remains
  protected from reinvestment.
- The harvester conversion decision must use one absolute-time, growth-aware oracle and strict
  completion-before-opponent-action semantics.
- Contract build -> bounded systematic enumeration -> fuzz -> host gates is the correct gate
  order. Fuzz is defense in depth, not evidence that a state machine is complete.

## Required design corrections

### R1. Define one atomic turn model and a priority order for co-occurring events

EV1-EV18 are predicates, not mutually exclusive symbols. Filling every state/event table cell
does not define behavior when two or more columns are true on the same `S_t`. Examples include:

- resident death + mother destruction + feature completion;
- ownership flip + asset-under-attack;
- mother destruction + cargo acquisition;
- cargo banked + lost-plant death;
- activation + deadline/cutoff;
- target invalidation + blocked threshold.

Specify whether each event is observed from the pre-action `S_t`, inferred from `S_{t-1}->S_t`,
or produced by the command emitted at `t`. Then give a deterministic priority function over the
event set. At minimum, terminal roster/asset facts must dominate work selection, immediate value
securing must dominate speculative conversion, and commitment termination must precede a new
commitment. Add compound-event fixtures; do not rely on prose footnotes for isolated cells.

Also distinguish persisted states from one-turn output modes. `HarvestNow` is currently described
as both a state and an emitted branch, while the as-built fields do not persist it. That is fine if
the machine is explicitly a Mealy machine with a named transient output mode; it is not fine if
the runtime decoder is expected to reconstruct S6 from persisted fields after the turn.

### R2. Replace EV7 and F-C1 with one exact asset-survival oracle

EV7's `eta_opp_x <= 1 || unexplained health decrease` is not a sufficient threat guard:

- ETA 2 can already be terminal for a fresh low-health banana, depending on speed, chop power,
  growth, and action ordering;
- a health decrease is lagging evidence after damage has landed;
- the existing `CONVERSION_RACE_ORACLE` compares our conversion against opponent HARVEST, not
  opponent destruction;
- multiple choppers can change the earliest destruction turn;
- a tie needs an explicit referee-order ruling, not an assumed safe boundary.

Define a single named, absolute-time `ASSET_SURVIVAL_ORACLE` (or extend the existing named oracle)
from exact `S_t`. It must report at least our earliest harvest/value-securing turn, our exact
conversion-completion turn, the opponent's earliest executable harvest turn, and the opponent's
earliest destruction turn under exact growth/health/action timing. EV4-EV7 must be a mutually
exclusive classification of those results, with strict tie semantics.

The same oracle must govern founding. The draft's
`eta_opp_h > first_fruit_delay && eta_opp_x > 2*CD + ceil(health(2)/chop)` compares opponent travel
to two proxy horizons and omits the resident's actual service/commitment ETA. Replace it with an
exact post-plant survival/value condition from the just-planted state. Keep activation-frequency
telemetry separate: a safer guard reducing activation is a value-profile change, not an
implementation failure, but it must be measured only after implementation validity.

This revision changes the §C disposition for DEF-04/07/14/17: the single harvester oracle covers
DEF-04 and the original DEF-07, but the draft reintroduces a second, approximate chopper deadline;
DEF-14 and DEF-17 are therefore not yet structurally covered.

### R3. Restrict parent-difference attribution to aligned prefixes

The proposed rule, “banana-attributable iff the candidate slot differs from the parent's aligned
slot on the identical input stream,” is sound only while the two executions have received the
same state stream. Closed-loop parent and candidate streams cease to be identical after the first
behavioral divergence. A later command difference can be a downstream state consequence rather
than a current wrapper intervention; equality can also hide an active channel that happened to
choose the same verb.

For D-9, use the stronger direct contract:

1. before successful TRAIN/second-worker existence, all six banana channels are inert;
2. the wrapper output equals its own unedited inner output on that exact input;
3. candidate and stable parent remain byte-equal on the aligned prefix, including the TRAIN turn
   and stats tuple;
4. any first pre-TRAIN divergence is a D-9 failure and ends the aligned-prefix proof.

After activation, attribute commands from explicit channel telemetry (`CH1`-`CH5`, target and
rewrite records). A shadow parent evaluated teacher-forced on the candidate's states may be useful
diagnostically, but it is not the same as a closed-loop paired-parent causal label. Reword A-2,
A-3, A-5, A-8 and “structural identity” accordingly: identity after a divergent history means
“no wrapper edit to the current inner result,” not equality to a separately evolved parent game.

DEF-11 is therefore only partially covered by the current §C mapping.

### R4. Make carrier progress an enforced arbitration rule, not only A-4 telemetry

N1 says the banana wrapper must not persistently block a loaded teammate, while CH5 always gives
the resident priority. Those rules can conflict. A moving resident can still take a carrier's only
progress cell; one-step idle-yield can choose another articulation cell or create a new parity
loop. “The resident is working” is not a proof of non-interference.

Specify the production conflict rule that makes N1 true. A safe formulation is: when a loaded
teammate has a unique progress-making landing on a committed bank route, that landing outranks the
banana resident for the turn; otherwise the resident may keep priority. If the resident cannot
yield without violating legality, the FSM must enter a bounded wait/replan path. The same rule must
cover CH1+CH2+CH3+CH5 jointly, not each channel in isolation.

A-4 should then verify the enforced rule. It also needs exact attribution: an inherited inner
carrier defect on a genuinely divergent state is report-tier unless a banana channel removed its
progress option. Record the before/after candidate sets or a same-state channel-bypass
counterfactual so the assertion can name the interfering channel.

Until this is specified, DEF-09/10/12 are detected in some runs but not structurally prevented.

### R5. Bound post-release interference

S5/S9 are described as inner-controlled, but CH2/CH4 still edit other workers, and S9 vetoes every
bank `PICK ... BANANA` for the rest of the game. That is not passthrough and can suppress unrelated
inner economy after the lost mother dies.

Either restrict the post-loss veto to commands targeting the exact latched live plant and drop the
global PICK veto when that asset dies, or model the global veto as a separate persistent policy
state with its own necessity, liveness, parity, and value gates. Do not call S5/S9/S10 byte-equal
or structurally identical where a channel still writes or where earlier wrapper actions have
already changed the trajectory.

### R6. Add recovery for commitments that become impossible

Assertions are not delivery behavior. S7 currently has no exit except mother death/resident death,
and S8 assumes a reachable door forever. If conflict resolution, opponent occupation, or map state
makes the oracle deadline or bank route impossible while the target/cargo remains live, the debug
build panics and the delivery build can loop.

Add explicit deadline-missed/unreachable events and bounded transitions. For S7, re-evaluate to a
safe abandon/lost state when exact conversion can no longer complete. For S8/S3(Bank), implement
I-19's “no door reachable” terminator without silently discarding cargo and state exactly who owns
the worker afterward. Every commitment must have a production exit for success, invalidation,
death, and infeasibility.

### R7. Freeze the bounded-enumeration contract and prove coverage from output

The 3,072 count is nominal: the cap-120 cases are said to replace degenerate cells, but the exact
replacement set is not enumerated. Several reachability claims are not guaranteed by the named
dimensions (notably resident death EV9, release then productive re-entry EV15, lost-plant death
EV16, and a real late-cutoff plant candidate EV18).

Before implementation handoff, commit an exact manifest with stable configuration IDs, row count,
seed/map hashes, cap, and expected event/transition coverage. Call the result “bounded exhaustive
over this frozen lattice,” not exhaustive over the game state space. The gate must fail if any
required event, transition edge, concurrent-event class, state/channel combination, or historical
red witness is absent. Add dedicated deterministic fixtures rather than assuming a mixed opponent
will kill the resident or that an idle profile will happen to traverse release/re-entry.

## Answers to the four review questions

1. **§C mapping:** every defect is named, but the mapping is not accepted as 17/17 structural
   coverage. DEF-11, DEF-14 and DEF-17 are open; DEF-08 is only a proposed test; and
   DEF-09/10/12 need an enforcing arbitration rule. The remaining mappings are accepted
   directionally, subject to R1's concurrent-event semantics.
2. **EV7:** rejected in its current threshold form. Use the exact asset-survival oracle in R2.
3. **D-9 attribution:** accepted only for the aligned prefix/first divergence. Use direct channel
   telemetry after divergence.
4. **Founding guard:** accepted as a first-class precondition, rejected in its current proxy
   arithmetic. Replace it with the exact post-plant oracle and log activation suppression as a
   later value-profile measurement.

## Required next handoff boundary

Claude should revise the design document first and send a design-only review request. Do not build
a delivery candidate from this draft. The next review should include:

- atomic event timing and priority;
- the exact combined harvester/chopper survival oracle and red/green tie fixtures;
- aligned-prefix versus channel-telemetry attribution rules;
- an enforcing carrier-priority/yield rule;
- bounded post-release edits and impossible-commitment exits;
- an exact enumeration manifest plus mechanically produced coverage table.

Round-5 SHA `47c98f5354ec89ea032c425394287ee24955c75846690d3527ee60ee2d167834`
remains withdrawn. Round-6 SHA prefix `eac2eb36` is a stabilization baseline, explicitly not a
handoff. Arena remains unchanged.
