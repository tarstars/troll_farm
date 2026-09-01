# Adversarial cross-review — clean-room champion package

- Reviewer: `chatgpt_1`
- Task: `20260901-cleanroom-champion`
- Review charter:
  `coordination/messages/local_claude_1/20260901T095136Z-20260901-cleanroom-champion-review-handoff.md`
- Package reviewed: `agent/local_claude_1@1286af7571c4f50bb10fe534fc2e9811bdd3a8b0`
- Owner-restructured behaviour document blob:
  `cleanroom/package/CHAMPION-BEHAVIOUR.md` at `6117eb98ea2e5d33204a3d220d3a93acbc75a423`
- Date: 2026-09-01 UTC
- Verdict: **`BLOCKED_PENDING_TARGETED_CORRECTIONS`**

## Executive verdict

This is a strong package. It is self-contained, unusually honest about uncertainty, materially
improved by the coordinator's execution review, and far closer to an implementable behavioural
specification than anything the project had before. The reference-path referee evidence is
credible: the coordinator reproduced the corpus measurements, replayed 40,458 recorded turns,
ran the package tests, and repaired seven concrete defects rather than explaining them away.

It is nevertheless **not ready to be shown to the fresh implementer**. Three findings block the
experiment:

1. Part I's most exact strategic claim — the early endgame trigger — is materially wrong. The
   package turns a necessary observation into a sufficient rule and omits the score condition
   used by the reference.
2. The clean-room boundary closes debug text and symbol names, but not the executable bytes or an
   unlimited black-box oracle. A stripped executable is still inspectable machine code, and the
   current process lets the implementer mine reference decisions before producing a first
   implementation.
3. `RULES.md` and the clean-room referee omit or misstate several legal-boundary semantics around
   `TRAIN` and invalid `PLANT`. Replay parity cannot catch these because the champion emits only
   valid commands.

Two additional issues are important for strength rather than purity: Part I omits observable
multi-worker coordination, and it calls several correlational or unmeasured properties
`ESSENTIAL` under a definition that claims causal evidence.

This is a **targeted-correction verdict**, not a rejection of the package. One disciplined repair
round should be enough. The card's stop should remain in force until that round is reviewed.

---

# Ranked findings

## P0-1 — the “fully determined” early endgame trigger is wrong

### Package claim

Part I principle 9 and Part II A5.2 say that conversion begins under either condition:

```text
living trees <= 4
OR
turn >= 251
```

The text calls the boundary “sharp and fully determined.” It then describes the bot as a
solitaire logger whose choices do not depend on the opponent.

### What the reference actually does

Before turn 251, the low-tree branch also requires the reference to be **behind in score**. In
behavioural terms, the condition is:

```text
turn >= 251
OR
(living trees <= 4 AND own score < opponent score)
```

This is not a cosmetic omission. A fresh implementation following Part I would start removing
already-banked fruit and recycling it through saplings whenever the map reached four trees,
even while comfortably ahead. That changes both risk and timing, and it can extend or alter the
ending clock.

### Why the cited measurement does not prove the package rule

`cleanroom/spec-work/measure.py` records only the first `PICK` in each game, then reports:

- every first pre-251 `PICK` happened with at most four trees alive;
- every other first `PICK` happened from turn 251 onward.

That proves a one-way statement:

```text
pre-251 conversion observed => trees <= 4
```

It does **not** prove:

```text
trees <= 4 => conversion starts
```

The measurement does not enumerate all pre-251 turns with at most four trees, does not split
those turns by score relation, and does not determine the first turn on which conversion was
otherwise feasible. The exact integer boundary is therefore suspiciously code-shaped relative
to the evidence: the data establishes a maximum, not a trigger.

### Required correction

Build a replay-only truth table over **every pre-251 turn with at most four living trees**. At
minimum record:

- own score minus opponent score;
- whether the shack contains plantable fruit;
- whether a worker has free capacity and can reach a valid door cell;
- remaining-turn feasibility of a complete conversion;
- command chosen that turn;
- first eligible turn and first conversion command.

Then state only the rule supported by those observations. Part I, A5.2, A6, and the “solitaire”
paragraph must agree. Until the replay table exists, mark the exact early trigger
`NOT DETERMINED`; do not call it fully determined.

This one correction is independently sufficient to keep the implementer stopped.

## P0-2 — the third leakage channel is the executable itself, amplified by an unlimited oracle

The package correctly closed two obvious channels:

- the reference bot's `MSG` diagnostics;
- its symbol table.

But stripping names does not turn an executable into behaviour-only evidence. The shipped
`harness/reference-bot` still contains its constants, branches, tables and control flow. A
capable fresh agent can run `strings`, disassemble it, attach a debugger, instrument it, compare
patched executions, or otherwise recover implementation structure. `EXCLUDED.md` currently
forbids reading outside the package, but it does not forbid inspecting the binary that is inside
it.

There is a second form of the same leak. The harness exposes the reference as an unrestricted
policy oracle: an implementer can generate states, run the binary, and collect exact actions and
full traces before writing version 0. At that point the experiment no longer asks whether the
written description is sufficient. It asks whether an agent can reverse-engineer the policy
from executable code and unlimited queries.

### Required process correction

Use a staged release:

1. Give the fresh implementer the documents, map samples and physics/referee, **without the
   reference executable**.
2. Require a complete first implementation and freeze its source hash.
3. Only then expose the reference through the pre-registered refinement protocol.
4. Prefer an execute-only runner outside the package. If that is impractical, add an explicit
   prohibition on static or dynamic binary inspection (`strings`, disassembly, debugging,
   decompilation, patching and byte analysis).
5. Freeze the comparison maps, query budget, emitted traces and number of refinement rounds;
   archive every oracle query.

The existing one-refinement-loop idea is good, but it is not enforced by package delivery. The
v0-before-oracle split is what makes the description itself testable.

## P1-3 — `RULES.md` and `referee.py` are incomplete at invalid-command boundaries

The coordinator's replay proof is load-bearing for normal play, but recorded champion commands
cannot exercise invalid or adversarial inputs. Several discrepancies remain.

### A. Legal `TRAIN` talent ranges are absent and unenforced

The platform validates:

```text
movement speed: 1 .. width*height
carry capacity: 0 .. 1000
harvest power:  0 .. 3
chop power:     0 .. 20
```

An out-of-range bundle is a non-fatal `invalid_skill` rejection. `RULES.md` gives no ranges, and
the clean-room referee accepts arbitrary integers before applying the cost formula. It can
therefore create a unit the platform would reject.

### B. More than one successful `TRAIN` per player per turn is not possible

`RULES.md` says multiple `TRAIN`s are applied sequentially and that the second is “rarely
affordable.” The stronger constraint is occupancy: the first successful purchase creates a
worker on the shack, so every later purchase by that player in the same turn is blocked. Multiple
commands may be printed, and a later command can succeed if earlier ones fail, but **at most one
can succeed**.

The nearby parenthetical is also wrong: a troll can occupy the shack not only on turn 1, but
after every successful `TRAIN`, until it moves on a later turn.

### C. Invalid `PLANT` item types do not match the platform

The shared item parser accepts `IRON` and `WOOD` for both `PICK` and `PLANT`. The clean-room
referee then indexes the fruit-health table with that value and can crash. The platform rejects
`PLANT IRON`/`PLANT WOOD` non-fatally. `PICK` may use any stocked item; `PLANT` may use only the
four fruits.

### Required correction

Add explicit rules and adversarial unit tests for talent bounds, sequential training, shack
occupancy after training, numeric item forms, invalid plant types, and non-fatal rejection.
Re-run the existing reference parity after the patch. These are physics tests, not champion
behaviour tests.

## P1-4 — Part I omits worker coordination, while overstating tree commitment

Part I is intended to be sufficient for a compact implementation. It explains the economy,
workforce size, tree preference, banking and conversion, but not how the two workers avoid
wasting each other's trips.

A competent literal implementation can send both workers to the same nearest tree, repeatedly
choose an occupied target, block a teammate at a door, or duplicate a journey while another
mature tree is free. These choices are often more consequential than the current principles
about one-turn MOVE endpoints or the tie between two equal-health seed species.

The package also says the reference “takes each tree all the way down.” A4.1 does not measure
that. It counts the size of the tree under each `CHOP`; 94.2% at size 4 establishes mature-tree
preference, not persistence after the first chop. A worker can leave and return, change targets,
or hand the tree to its teammate while producing the same count.

### Required observation packet

From replays, measure and cite:

- when both workers have at least two viable trees, how often they choose distinct targets;
- how often they co-target or co-chop the same tree;
- how often one worker's destination is occupied or blocked by its teammate;
- after the first chop on a tree, whether the same worker remains until death, leaves and
  returns, or abandons it;
- target changes and direction reversals around those events.

If a stable rule exists, worker coordination belongs in the top ten and should replace a
low-value habit. If it does not, mark it explicitly `NOT DETERMINED`. Rewrite principle 4 as
“prefer mature trees” unless lifecycle evidence supports the stronger commitment claim.

## P1-5 — `ESSENTIAL` is defined causally but applied to observational claims

The marks are useful and do not, by themselves, reveal code structure. The problem is their
contract:

> ESSENTIAL — drop it and you have a weaker bot.

Several marks do not have that evidence:

- Principle 2 establishes an observed purchase invariant and field correlation, while the direct
  ladder intervention “wait for at least 2/2/0/2” lost. The exact talent rule is not causally
  validated as a unit.
- Principle 4's mature-tree preference has score arithmetic behind it, but the added
  “all the way down” commitment is unmeasured.
- Principle 9's conversion mechanism has sound arithmetic; its exact timing rule is wrong and
  was not causally tested.

These marks therefore transmit project judgement that a spectator could not derive from the
cited observations alone. That is not source-code leakage, but it is still an unlabelled advice
channel.

Use evidence-shaped labels instead, for example:

```text
SCORE MECHANISM       arithmetic or referee rule establishes value
OBSERVED INVARIANT    held on the 160-game reference corpus
LADDER-TESTED         changed and measured on the ladder
HABIT                 observed, no strength claim
OPEN                  not recovered
```

Alternatively keep `ESSENTIAL`, but require a direct ablation, a dominance proof, or an explicit
cross-player result for every use.

## P2-6 — exact wording contains several contradictions and false absolutes

These are individually small but dangerous in a document that tells the implementer to build
from Part I.

1. **Harvest timing.** Part I says all 130 harvests are in the opening; Part II says one late
   exception. Say “129 of 130” or “all but one.”
2. **Plant location.** Part I says every plant is distance 1 and A6 says it never plants out on
   the map; the evidence says 1,621 of 1,622, with one distance-2 exception. Use “almost always.”
3. **Four-turn conversion.** `PICK -> PLANT -> CHOP -> DROP` is four commands only when one chop
   kills the size-1 sapling. Plum, lemon and apple, or a weak chopper, need extra chop turns.
   The +3 final conversion is valid; the cadence is species- and talent-dependent.
4. **Seed-order rationale.** Size-1 plum and lemon both have health 6. A single “cheapest to fell”
   key cannot produce plum before lemon; the order between them is a tie-break habit. State
   low-health-first, with an observed but non-economic plum/lemon tie-break.
5. **Solitaire claim.** “No positional response detected” is supportable. “Nothing it does
   depends on the opponent” is not: the early conversion decision depends on relative score.
6. **DOMAIN §1.2 wording.** “Never weaker than 2/2/0/2” conflicts immediately with “one player
   was 5% below it.” The underlying result appears to be six leaders never below and one leader
   below in 5% of purchases; say that.
7. **DOMAIN §1.2 internal consistency.** It says the reference “buys the best it can afford early
   rather than waiting,” while Part II correctly shows it often waits with weaker bundles already
   affordable. Say: when it finally buys, it chooses the best then-affordable bundle; it often
   accepts a bundle below 2/2/0/2 by its deadline.
8. **DOMAIN §1.4 scope.** Counting chops on opponent-planted coordinates tests one interference
   mode. It does not establish that strong players never block, race, harvest, occupy or otherwise
   suppress. Narrow the heading and conclusion to destructive chopping of opponent plantings.

---

# Citation-integrity spot checks

I checked the package at its pinned commit, not the moving branch.

### Joins that agree

- Game `900571119`, turn 16: `champion-purchases.json` contains the stated inventory trajectory,
  purchase turn and `1/2/0/2` bundle.
- Game `900571126`, turn 1: the purchase record agrees with the cited opening purchase.
- The cited drops, seed picks and door plants for game `900571119` agree with
  `cleanroom/spec-work/observations.json` and the extraction logic in `measure.py`.
- Aggregate counts in Part II map to named counters in `measure.py`; I found no arithmetic drift
  in the sampled joins.

### Where citation integrity is insufficient despite correct rows

The endgame problem is not a false row. The cited examples occurred. The failure is inference:
a collection of positive examples plus a maximum does not prove the converse or an exact
trigger. The same caution applies to “all the way down” and “no opponent dependence”: their
current extractors do not measure the claimed conditional behavior.

### Scope of this review

The 6.5 MB compressed raw-corpus file was not directly streamable through the repository
connector in this session. I therefore spot-checked the derived records and extraction code and
used the coordinator's independently executed 40,458-turn replay as the full-corpus execution
proof. My findings above do not depend on trusting an unexecuted aggregate: the main trigger
error is confirmed independently, and the rules/harness issues are boundary semantics absent
from the replay population.

---

# Are these the right ten principles?

The one-page restructuring is a clear improvement. The following belong near the top:

- wood-first economy;
- one additional non-harvesting worker;
- early funding of that worker;
- mature-tree logging;
- a target-choice rule explicitly marked open;
- load-and-bank behavior;
- endgame fruit-to-wood conversion, once corrected.

The current top ten spend two scarce slots on low-level habits:

- naming one-turn-reachable MOVE endpoints;
- the plum/lemon seed tie-break.

At least one of those slots should be used for **coordination between the two workers**, after it
is measured. If coordination is genuinely not recoverable, that absence itself must be in Part I
because a fresh implementer must make the choice.

The document is also candid that the training target and tree target are not recovered. Those are
probably the two largest parity ceilings. That does not make the experiment invalid, but the
Done criterion should not silently assume Part I is already sufficient for exact imitation. The
experiment can still succeed by producing a leaner policy of equal strength; it should report
which open choices the implementer had to invent.

---

# Minimum correction gate before the implementer

The package may advance after all of the following are pinned and reviewed:

1. **Endgame truth table:** every pre-251 low-tree state classified by score relation and action;
   Part I/A5/A6 corrected.
2. **Clean-room delivery protocol:** v0 frozen before reference-oracle access; binary inspection
   explicitly forbidden or technically prevented; query/refinement budget recorded.
3. **Physics boundary patch:** legal talent ranges, at-most-one successful TRAIN, post-TRAIN
   shack occupancy, PLANT item validation and non-fatal rejection tested.
4. **Coordination/commitment evidence:** measured packet added, or both questions explicitly
   marked open and the overclaim removed.
5. **Wording repair:** the eight P2 contradictions corrected and causal labels made evidence-
   shaped.
6. **Regression proof:** existing package tests and reference-vs-reference checks pass; the
   coordinator repeats the replay extraction; new invalid-command tests pass.
7. **New immutable package pin:** owner and `chatgpt_1` review the corrected pin before any fresh
   implementer receives it.

No second broad research cycle is needed. The high-value work is narrow: fix the incorrect
predicate, close the experimental channel, harden physics boundaries, and measure the one major
behavioural omission.

## Final verdict

```text
DOCUMENT QUALITY:          STRONG
REFERENCE-PATH PHYSICS:    REPRODUCED WITH DOCUMENTED LIMITS
BEHAVIOURAL SUFFICIENCY:   NOT YET
CLEAN-ROOM PURITY:         NOT YET ENFORCED
IMPLEMENTER RELEASE:       BLOCKED
NEXT ACTION:               TARGETED CORRECTION ROUND
```

The clean-room idea remains worth doing. The package should survive these corrections and become
more informative because of them. No implementation, experiment, submission, ladder read or
platform action was performed in this review.