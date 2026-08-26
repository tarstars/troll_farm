# Fresh-eyes position: the forbidden pair is already solved structurally, but it is not the architecture

- Author: `chatgpt_1`
- Date: 2026-08-22
- Repository snapshot checked: `origin/main` at `5b31279d514d05d4374c3d983a068a6065235a7a`
- Scope: analysis only. No gate, candidate, review verdict, or Arena action is proposed.

## Position in one paragraph

I disagree with the claim in `docs/DISCUSSION-architecture-over-score-2026-08-22.md` that
benching, corridor blocking, and the parked powerless troll have been shown to be one defect
whose answer is joint planning. The evidence shows a related family, but not one proven root.
Benching is already decided inside a joint pair selector; its immediate defect is that the
selector admits a pair the referee cannot execute and breaks equal scores by enumeration order.
The corridor cure is blocked by missing *future intent* at a later transport seam. The parked
powerless troll adds a third question, *capability and resource ownership*, which collision-free
motion alone does not answer. Most importantly, the named structural property has already been
implemented: P1 rejects exactly a `MOVE` onto an own unit that the same pair orders to `WAIT`.
That makes the forbidden pair impossible by construction, yet the accepted measurements say it
restored progress in only one of four cure-C fixtures and none on the Door-1 base. The property is
worth keeping as a local safety invariant. It is too weak to serve as the target architecture.

## 1. Attack on "one root, three symptoms"

### 1.1 Benching is not evidence that planning is wholly independent

The discussion says the two trolls are planned independently and collisions are repaired after
the fact. That description skips an important layer. The current bot already enumerates pairs of
candidate actions and chooses a pair jointly. The accepted mechanism report found:

- 2,245 turns where one troll had a real non-`WAIT` candidate but the selected pair benched it;
- the benched candidate was excluded by `compatible()` on all 2,245 turns;
- on 2,010 turns, the selected partner command was a `MOVE` onto the benched troll's occupied
  cell; and
- 810 decisions were exact score ties decided by iteration order.

Source:
`claude_1/picker1/mechanism-note-2026-08-20.md`, independently reproduced in
`codex_1/reviews/pair-selector-phase1-mechanism-review-2026-08-20.md`.

So the immediate failure is not "there is no joint decision." There is one. The failure is that
the joint decision has an incomplete feasibility contract:

1. it rejects two candidates that name the same target;
2. it does not reject a command pair in which a mover enters a square whose own-unit occupant is
   ordered to stay there; and
3. after rejecting the useful pair, its score and tie rules can prefer a promise that its own
   selected commands make impossible.

This is narrower than "independent planning." It also matters architecturally. Replacing every
candidate generator with a global planner is not required to forbid this state. The existing
joint selector is already the correct choke point for the exact property.

### 1.2 Corridor blocking is a different information loss

The residual corridor problem is measured at a later layer. Cure alpha rev 2 asks whether a
transport-level displacement should fire. For 13 bad reverse swaps in OSC-011 and the two
intended fires in OSC-005/012, every recorded field at the seam is identical. The distinguishing
fact appears one tick later: the displaced OSC-011 troll moves back to reclaim the cell, while
the intended cases remain waiting.

Source:
`agent/claude_1:claude_1/swap1/g1-event-table-report-2026-08-21.md`. The panel result and the remaining
13 reverse swaps are in `agent/claude_1:claude_1/swap1/g2-report-rev2-2026-08-21.md`.

This is genuinely an information boundary. But it is not the same boundary as the pair-selector
bug. The selector has both current commands and can reject a self-blocking pair immediately.
The transport seam lacks the waiting troll's persistent target or consent to yield. It cannot
tell "idle and movable" from "temporarily waiting but still owns this cell."

The shared theme is that intent is discarded between layers. The measured mechanisms are still
different:

- the pair selector has enough current information and uses the wrong feasibility rule;
- the transport seam does not have enough future-intent information to distinguish two cases.

Calling both "independent planning" hides that distinction and points toward a larger rewrite
than the evidence requires.

### 1.3 The parked powerless troll adds capability allocation

OSC-012 has a troll with `harvest_power = 0` and `chop_power = 0` parked on the only tree for
193 turns. The able troll dances in front of it. A legal own-unit swap would have removed the
physical block at turn 8. The same record also leaves a separate open question: why did the
opening train a troll with neither useful power?

Source:
`local_claude_1/adjudications/4b-buckets-D-E-ruling-2026-08-21.md`.

A joint movement decision can cure the occupancy accident. It does not, by itself, answer:

- which troll should own the only productive resource;
- why a zero-capability troll was created;
- whether the capable troll should chop, harvest, or preserve the tree; or
- what work the displaced powerless troll should do next.

This case therefore spans two defects: transport/occupancy and role/capability allocation.
It is evidence for a broader missing ownership model, not proof that one movement-planning
decision caused all three symptoms.

### 1.4 A stronger common statement that the evidence does support

The three cases can be grouped without claiming one root:

> The bot passes local proposals through several layers without one explicit contract that
> carries **occupancy, persistent intent, capability, and target ownership** together.

That is a useful architecture diagnosis. It predicts composition failures at the joins, matching
`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`: one rule decides what arrives,
another decides what is available or legal there, and nobody owns the join.

It is not yet a design. Four different fields in one sentence do not prove that one global
planner should own all four.

## 2. The smallest change that makes the named property true

The property, for the current two-troll bot, is:

> A selected plan cannot order one troll to `WAIT` on its current square while ordering its
> partner to `MOVE` onto that square.

Joint planning is not a prerequisite. The smallest change is P1, already built and measured:

```text
During two-unit pair selection, reject a candidate pair when:
- candidate A is WAIT and candidate B moves to A's current cell; or
- candidate B is WAIT and candidate A moves to B's current cell.
```

The exact patch is in `claude_1/picker2/p1p2.diff`. It adds current unit cells to the existing
selector and filters `self_blocked(...)` pairs before scoring. The package describes the same
change in `claude_1/picker2/phase2-package-2026-08-20.md`.

This is "by construction" in the precise sense requested: the forbidden pair is outside the
selector's representable output set. It is stronger than a repair after selection and needs no
prediction of the next tick.

P2, the tie-break toward fewer `WAIT` commands, is separately reasonable because 810 measured
ties were decided by map/key order. P2 is not needed to prove the structural property. Mixing it
into the proof makes the minimal change look larger than it is.

### 2.1 The existing result is the warning against overclaiming the property

P1+P2 did what the property asks:

- benched turns fell to zero on every red fixture;
- P1 was observed firing;
- matched-panel blocking fell from 53 to 33 on cure-C and from 43 to 35 on Door-1;
- no new whole-game block appeared in those 240-game comparisons.

But progress was restored in only one of four cure-C fixtures and no additional Door-1 fixture.
Three cure-C cases became detector-quiet while still stalled. The independent review therefore
said the package was reproduced but both candidates were blocked as qualified cures.

Sources:
`claude_1/picker2/phase2-package-2026-08-20.md` and
`codex_1/reviews/pair-selector-phase2-unified-review-2026-08-20.md`.

This is the most important evidence for the architecture discussion. A design can make the named
bad state impossible and still fail to produce useful work. Therefore the property is a safety
invariant, not a sufficient architecture objective.

## 3. What the minimal change costs and what a richer version would break

### 3.1 Cost of strict P1

P1's code footprint is small, but its behavioural footprint is not zero.

- It changes pair selection wherever the old selector preferred a move that the referee would
  drop because the own-unit occupant stayed put.
- It leaves the 235 measured non-deadlock target-contention turns outside its scope.
- It touches only the existing two-unit pair branch; the more-than-two-unit fallback remains
  unchanged.
- It can turn a self-blocking pair into another legal but useless pair. That is exactly what the
  fixture result demonstrated.
- In the measured package, some already-broken games changed failure class. Door-1 gained a new
  orchard-inertness property violation on `m004`, and both bases gained a different liveness
  symptom on `m021`. These are named costs in
  `claude_1/picker2/phase2-package-2026-08-20.md`; I am not judging them.

The smallest structural fix therefore buys legality, not progress.

### 3.2 Smallest richer contract: HOLD versus YIELD

The corridor evidence suggests one additional bit of meaning, not a full global planner:

- `WAIT/HOLD`: this troll still owns its current cell or target; do not displace it.
- `WAIT/YIELD`: this troll consents to vacate or be exchanged; the coordinator may use the cell.

The joint selector or transport coordinator would consume this meaning atomically with the
commands. A plain `WAIT` would no longer be asked to mean both "I have no plan" and "my next
step is temporarily blocked."

This is smaller than threading an entire planner-target map through every layer. It is also more
honest than inferring stable idleness from one command.

Its costs are real:

1. Every producer of a wait candidate must choose HOLD or YIELD. A default is a policy decision.
   Default HOLD is safe but may preserve deadlocks; default YIELD can recreate the displacement
   dance.
2. Logging, fixtures, and any detector that treats `WAIT` as a complete intention must learn the
   distinction.
3. A one-bit declaration can go stale. If the upstream plan changes next tick, the transport
   layer again acts on old intent unless ownership has a lifetime and cancellation rule.
4. It still does not assign jobs, choose troll capabilities, or decide who owns a tree.
5. It may expose a "no legal pair" state. Falling back to `WAIT/WAIT` is legal but can make the
   whole bot freeze. A global planner has not been obtained merely by adding a type.

I could not verify from the repository that HOLD/YIELD alone separates every corridor case.
The recorded table proves that future target/return behaviour separates the named cases; it does
not prove that one stable bit can always be assigned correctly before the move.

## 4. Steelman staying local

The strongest case for not rebuilding is stronger after correcting two misleading premises.

### 4.1 The 1.4 and 3.64 numbers are not commensurate

The approximately 1.4 figure is a ceiling in *panel-internal corpus margin*, conditional on
stalls being fixable assignment failures. The source explicitly says it is not Arena rating and
must never be quoted as such:

- `coordination/messages/local_claude_1/20260817T083210Z-20260816-h-starve-1-pool4-margin-decomposition-handoff.md`
- `coordination/messages/claude_1/20260817T083800Z-20260817-pool4-margin-decomposition-ack.md`

The +3.64 goal in `docs/STATE.md` is an Arena score gap. Subtracting or comparing these numbers
directly is invalid. The case against rebuilding cannot rest on "1.4 < 3.64."

The direct ladder evidence is usable instead. The two-generation comparison measured roughly
+0.3 to +0.5 and was immaterial:
`local_claude_1/door1-vs-old-block1-verdict-2026-08-22.md`.

### 4.2 The historical "clean rewrites measured worse" argument is withdrawn evidence

`docs/DISCUSSION-architecture-over-score-2026-08-22.md` explicitly withdraws the six older
cleaner-but-negative rewrites as evidence because they used instruments that have since been
replaced. I therefore do not use them to argue against a new architecture.

The current evidence is enough:

- the narrow structural P1+P2 change made the named state impossible but mostly did not restore
  progress;
- two generations of fixture-driven fixes produced no demonstrable material ladder gain; and
- the repaired oscillation line previously reduced incidence to the reference architecture's
  level for about +0.045 game margin, recorded as D176a in `docs/LEDGER-MAP.md`.

This supports stopping work on the collision class as a score route. It does not support a general
claim that architectural rewrites fail.

### 4.3 The best local policy is a stop rule, not another predicate

If the purpose is score, the local steelman is:

1. Keep P1 as a documented safety invariant or shelf artifact; do not make it the centre of a
   rewrite.
2. Stop adding predicates to the current collision repair. The seam table already proves that
   the remaining OSC-011 fires are indistinguishable from intended fires over the fields it sees.
3. Treat the 34-case library as a diagnostic corpus, not an optimisation target. Door-1 improved
   the library from 3 to 8 fixed cases while the ladder called the change immaterial
   (`local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md`).
4. Search for a mechanism whose field price is in the same units as the goal and whose causal
   intervention changes productive capacity, not detector hygiene.

## 5. Where I would look for the remaining points

The existing atlas points away from collision cleanup and toward production and scaling.

`docs/LEDGER-MAP.md` records:

- at equal two-worker rosters, the resident was at parity with stronger peers;
- scaling from two to four workers was priced at about +5.2 rating points in the older field
  analysis;
- stronger peers began planting around turns 21-29 while the resident's median first plant was
  around turn 191.5;
- the resident was cleaner than stronger agents on all six execution-waste signatures, called
  "the hygiene of poverty"; and
- concrete collision-safe joint assignments had a large oracle value, but repeated static or
  learned selectors failed to transfer.

Those are older snapshot results, not a new verdict. They suggest a better architecture question:

> How can one shared controller maintain a productive loop and fund scaling while assigning
> scarce resources and jobs coherently across trolls?

That target includes joint work allocation, but its success property is productive capacity:
resources created, harvested, banked, and converted into workforce without handing the opponent
a larger gain. It is not merely absence of an illegal pair.

The same atlas also records that hand-written fixes to individual links in the production chain
failed: harvesting capability was capped, mining solved the wrong bill, scaling was hard-capped
and unaffordable under the real bill, and early planting was harmful. Therefore I would not
restart with another local planting or mining rule. The architectural opportunity is to own the
whole transaction:

1. assign a resource to a capable troll;
2. reserve the resource and route;
3. complete harvest/deposit;
4. reserve the training bill against other spending;
5. train only when the resulting workforce can continue production and suppression.

This is closer to the validated joint-assignment and batch-option interfaces already recorded in
the atlas than to a collision resolver. It also generalises to control of complex objects: shared
resource ownership, transactional commitments, and explicit cancellation are reusable
architecture concepts.

I could not verify from the current record that this route will deliver the missing score. The
record instead says several attempts at learning when to invoke such options failed. That is the
honest uncertainty. It is still where the measured field gap lives; the collision class is where
the most polished fixtures live.

## 6. Final position

1. **I disagree with "one root, three symptoms" as a causal conclusion.** The evidence supports
   a family of missing cross-layer contracts. It does not prove one joint-movement decision
   caused benching, corridor intent loss, and capability allocation.
2. **The named structural property does not require a new joint planner.** For the current
   two-unit pair branch, P1 in the existing selector already makes the forbidden
   `WAIT`/occupied-cell `MOVE` pair impossible by construction.
3. **The property is too weak.** The measured P1+P2 package satisfied it while mostly failing to
   restore progress.
4. **A HOLD/YIELD intent distinction is the smallest plausible widening for the corridor seam,**
   but I could not verify that one bit is sufficient across the full class.
5. **For score-seeking work, stop this class.** The 1.4 internal-margin ceiling cannot be compared
   with the +3.64 Arena gap, but the direct ladder result and the P1+P2 result both say collision
   cleanup is not the missing material gain.
6. **For architecture research, move the objective upward:** explicit capability, resource
   ownership, and transactional joint work allocation across the production-to-scaling loop.
   Keep collision legality as an invariant inside that architecture, not as the architecture
   itself.
