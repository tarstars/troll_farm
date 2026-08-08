# Review — score-transparency manifest

- Reviewer: `chatgpt_1`
- Task: `20260809-score-transparency-manifest`
- Reviewed policy:
  `coordination/messages/local_claude_1/20260809T160000Z-20260809-score-transparency-manifest-policy.md`
- Reviewed manifest:
  `docs/MANIFEST-score-transparency-2026-08-09.md`
- Subject source:
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Source SHA-256:
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Review mode: committed readable-source analysis; no private-repository execution claimed
- Disposition: **`ACCEPT_DIRECTION — REVISE_PREMISE_BEFORE_SCHEDULING`**

No implementation, candidate, detector, gate, referee, host run, TestSession, submission, restore
or Arena action is authorized by this review.

## Executive conclusion

The owner's direction is correct: intention is not legible in the current bot, and this opacity
has already caused expensive disagreement about what the program does. The requested bridge,
debug tooling, situation library and priority audit are all justified.

The manifest's first premise is too narrow, however:

> The bot is not an action-weighting system. It is a hybrid decision pipeline in which scalar
> scores are only one stage.

The submitted source does all of the following before and after comparing scores:

1. selects a latent mode from persistent state and world state;
2. chooses one candidate generator and sometimes returns early, making whole classes of actions
   unavailable regardless of score;
3. filters candidates by capacity, reachability, time horizon, ownership and other predicates;
4. assigns scalar scores;
5. chooses a compatible two-unit pair by summing scores, or uses a different greedy algorithm for
   larger rosters;
6. injects or replaces candidates for door clearing;
7. rewrites selected MOVE commands in a separate conflict resolver;
8. updates persistent commitments from the rewritten command stream.

A bridge that maps only `intention -> number` would document one middle layer while leaving the
same planner/resolver and eligibility opacity that produced the oscillation diagnosis failures.
The bridge must cover the complete decision pipeline.

My answer to the prioritization question is therefore:

> **Build one code-generated per-turn Decision Packet first.** It is simultaneously the first
> useful bridge and the first useful debugger. The static bridge, oscillation library and hierarchy
> audit should be generated from or checked against these packets rather than maintained as
> separate prose systems.

## 1. Is “big steps encode intention” correct?

### Verdict: partly correct as an implementation pattern, not sufficient as a model

The source does contain conspicuous numeric tiers:

- `20_000` forced movement and door-unblocking actions;
- `10_000` a current-tree endgame override;
- `9_000` immediate planting;
- `8_000` immediate DROP or plant travel class;
- `7_500 - priority` seed PICK;
- roughly `7_000` banking travel;
- `6_500` train-time shack evacuation;
- `6_100` / `6_000` opening resource work;
- `750 / time` conversion choices;
- `1000 * wood / turns + denial bonus` ordinary chop work;
- `1 / trip` late idle harvest;
- `0` WAIT.

Those numbers are not historical noise in the weak sense: they clearly impose priorities inside
some candidate sets. But the source does not attach a band or an intention to a `Candidate`.
`Candidate` contains only:

```text
command, score, target
```

Consequently the same number can mean urgency, phase, task utility, a hard override, or merely a
caller-selected baseline. The same command verb can represent many intentions, and the same helper
can emit into different score regions depending on its caller.

More importantly, many intentions are encoded outside the score:

- `early_candidates`, `main_candidates` and `endgame_candidates` use early returns. A unit with
  cargo, a full unit, a committed regeneration worker, or an endgame worker may never receive the
  alternatives that another mode would score.
- `commands()` selects the candidate generator from `committed_regeneration`, `endgame`, `early`,
  training and other state. This control flow is part of the policy.
- `compatible()` and `stock_compatible()` remove candidate pairs after scoring.
- `force_unique_door_clear()` can replace a unit's candidate list with a forced action.
- `resolve_move_conflicts_with_priority_and_forbidden()` can replace the selected MOVE with a
  different landing or WAIT after scoring is finished.

Therefore the corrected premise should be:

> **Intent and priority are encoded by a mixture of mode selection, candidate availability,
> constraints, score bands, pair aggregation and post-selection rewriting.**

“Big steps encode intention” should remain a hypothesis about one layer until the owner ratifies
specific bands and the reachable decision traces confirm how they are used.

## 2. The current band table is evidence for an audit, not proof of a crossing

The manifest correctly notices that additive terms can reach values outside an intuitively named
local range. The `3900` chop example is a valid reason to investigate.

It is not by itself proof that one intention outranks another incorrectly. Two globally visible
score formulas may never coexist in the same reachable candidate set because an earlier mode or
return removes one of them. The audit must operate on **co-reachable alternatives in concrete
states**, not only on a global list of numeric literals.

There is a second aggregation risk that the manifest should add. With exactly two own workers,
`select()` maximizes:

```text
score(candidate_a) + score(candidate_b)
```

subject to target and stock compatibility. A hierarchy designed per unit is not automatically a
hierarchy for the team. A lower-priority compatible pair can beat a pair containing one
higher-priority action if the other worker's compatible alternative changes enough. Conversely, a
high action can become unavailable because its target conflicts while a lower pair remains legal.
The `Target::None` hole is an example of compatibility changing the meaning of the score sum.

The hierarchy audit therefore needs at least three levels:

1. **within-action composition:** can score terms cross their declared local range?
2. **within-unit comparison:** which differently intended candidates are reachable together?
3. **team comparison:** can pair sums and compatibility trade away an intention that was meant to
   be lexicographically mandatory?

If the owner truly intends a hierarchy rather than a soft trade-off, numeric gaps are the wrong
primitive. The future design should use an explicit lexicographic priority or hard constraint,
with scalar utility only inside one priority class. That is a design recommendation, not an
authorized implementation.

## 3. Why a manually maintained bridge would be unsafe

A prose table mapping call sites to intentions would be useful for one review and dangerous after
the next edit. The project already has examples of a document and implementation agreeing with
each other while both encode a retired or incorrect predicate. A static bridge can fail in the
same way.

A maintainable bridge must be executable and generated from the same structures the bot uses.
Conceptually, every candidate needs machine-readable metadata such as:

```text
candidate_id / source_site
mode and generator
intent
semantic target
planned landing or stationary occupation
priority class
score terms: [(term_id, value, rationale)]
final scalar utility
eligibility facts
```

The selector then needs to report:

```text
candidate rejections and reasons
pair compatibility matrix
stock constraints
chosen pair and runner-up
score margin
```

The resolver needs to report:

```text
planned command and landing
emitted command and landing
rewrite reason
whether the planner was notified / target invalidated
```

The execution layer, once an accepted referee exists, needs to report:

```text
accepted or rejected command
realized next state
progress / task outcome
```

The generated documentation can then list bands and intentions, but the code-generated packet is
the authority. A build/check should fail if a candidate is created without an intent and score
breakdown, or if a new score term is absent from the generated registry.

Even this metadata is only the implementation's **claim** about its intention. It must not be used
as its own truth oracle. The independently judged situation library supplies the external answer
to “was that intention and action correct?”

## 4. The single first deliverable

### Recommendation: a versioned per-turn **Decision Packet**

This should be the first scheduled deliverable because it is the dependency of the other three.
For one frozen state, the packet must explain the entire route from world state to emitted command:

1. source SHA and decision-schema version;
2. turn, unit state and persistent bot mode;
3. candidate generators entered and branches/early returns taken;
4. candidates generated, with intent, semantic target, predicted landing, band and score terms;
5. actions not generated, with the predicate that excluded them where practical;
6. compatibility and stock rejection reasons for candidate pairs;
7. selected pair and nearest alternatives;
8. command before and after conflict resolution, with a typed rewrite reason;
9. expected and realized post-state when a trusted execution instrument is available;
10. task/progress outcome.

This one artifact would have exposed most of the oscillation confusion immediately:

- M1: the packet would show distinct semantic targets but a predicted landing through a stationary
  peer, followed by an unreported resolver detour.
- M2: the packet would show that WAIT carries `Target::None`, claims no occupation in the planner,
  and is therefore universally compatible with a peer targeting the occupied cell.
- M3: two adjacent packets would show that the candidate universe itself changes — only the
  current door is priced while on a door, all doors one step away — rather than merely showing two
  mysterious final numbers.
- The Gold watchdog proposal would be falsified by the realized position history: the unit moves
  every turn, so a same-position streak never starts.
- The original TRAIN defect would become visible once execution is connected: repeated emitted
  TRAIN with no spawn event and no worker-count change is an explicit planned-vs-realized mismatch,
  not a clean game.

The Decision Packet should be the bridge, not merely a tool beside the bridge. A human-readable
score/intent document should be generated from the same metadata.

## 5. Is the oscillation situation library worth starting while the panel is `GATE_UNREADY`?

### Verdict: yes, with a strict trust boundary

The library does not need to begin as a corpus of accepted game outcomes. It can begin as literal,
source-pinned decision states and expected-action reviews. Candidate generation, score comparison,
compatibility and resolver behavior can be studied without claiming that an unaccepted referee
produced a valid full game.

Each situation should carry separate provenance states:

- `source_exact`: source SHA and literal pre-decision state are pinned;
- `decision_trace_exact`: the Decision Packet reproduces from the pinned source;
- `execution_provisional`: the next state came from an unaccepted instrument;
- `execution_accepted`: the next state came from an accepted, hash-pinned referee;
- `expected_action_reviewed`: independent reviewers have recorded an acceptable action set and
  rationale.

The first library should contain at least:

- `m110-s1`: route/corridor block;
- `m014-s1`: stationary `Target::None` occupation;
- `m085-s0`: one-worker scorer cycle;
- `m040-s1`: provisional working-blocker case, not accepted until referee revision 2 passes.

The independent judgment should usually be a set of acceptable actions or constraints, not one
exact command. For example, “restore progress without crossing the stationary commitment or
abandoning a still valuable job” is more robust than hard-coding one coordinate.

The library must not quote global episode counts or game outcomes from the unaccepted referee as
settled truth. It can preserve them as versioned provisional evidence.

## 6. Proposed order after the first deliverable

1. **Decision Packet and generated intent/score registry.** This is the executable bridge and the
   debugging substrate.
2. **Small situation library.** Freeze the three source-trusted mechanisms plus provisional
   `m040`, and record independent acceptable-action constraints.
3. **Reachable hierarchy audit.** Run the packet generator over the library and a broader state
   sample; enumerate actual co-reachable comparisons, pair-sum trades and resolver overrides.
4. **Architecture decision.** Where the owner intends strict hierarchy, replace numeric-gap
   conventions conceptually with typed/lexicographic priority and scalar within-band utility.
5. **Broader tooling and corpus expansion.** Only after the schema proves useful and does not drift.

This order avoids building four independent systems. The bridge, debugger, situation library and
hierarchy audit become different views over one versioned decision record.

## 7. Required corrections to the manifest before scheduling

1. Replace “the bot's logic is defined by assigning weights to actions” with the hybrid-pipeline
   description. Scores are one stage, not the algorithm.
2. Mark “big steps encode intention” as a hypothesis to ratify per band, not an established global
   fact.
3. Require the bridge to cover eligibility, modes, pair constraints and resolver rewrites in
   addition to score arithmetic.
4. Require code-generated metadata and drift checks; reject a separately maintained intent table
   as the authority.
5. Distinguish declared intent, implemented mechanism, observed effect and independently expected
   action. None may stand in for another.
6. Audit reachable candidate sets and team-level pair aggregation, not only global score ranges.
7. Permit the situation library to start now under source-level provenance, while forbidding
   unaccepted referee outcomes from becoming calibration truth.
8. Name the first deliverable as the Decision Packet above.

## Final answer to the owner's question

The single deliverable most likely to have prevented the most wasted effort this week is:

> **A code-generated, versioned Decision Packet that explains every candidate, exclusion, score
> term, compatibility decision, selected pair, resolver rewrite and realized outcome for one
> turn.**

A static band table would not have revealed `Target::None`, early-return candidate suppression or
the silent detour. A library without the packet would preserve symptoms without explaining why
the bot chose them. A hierarchy audit without reachable decision packets would compare numbers
that may never compete.

The Decision Packet makes the current program inspectable first. The bridge, situation library and
hierarchy audit can then be built as checked projections over that one source of evidence.