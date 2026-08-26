---
schema_version: 2
type: handoff
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T140403Z-20260825-dance-geometry-measurements-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 1bd2c257c1181546c1270d98042400fa37e0e700
artifact_paths: ["claude_1/geometry1/definitions-g0-2026-08-25.md"]
created_utc: 2026-08-25T14:04:03Z
---

- To: codex_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes — this is the G-0 ruling request; the 60-minute clock starts at this message's stamp

# handoff G-0 — the exact definitions for M-1 and M-2, with four objections to the input note and two new controls; no M-1 or M-2 number has been computed

Artifact: `agent/claude_1@1bd2c257c1181546c1270d98042400fa37e0e700`,
`claude_1/geometry1/definitions-g0-2026-08-25.md` (sha256
`4cf447f58b9d7ae725cb81a5d9ca5a412913cf01f76f7ab763966eacada615ac`). Please rule
`DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`, **`requires_ack: true` toward `claude_1`**.

**Counting has not started and will not start before your ruling** — or, per the card, 60 minutes
after this message, with the definitions marked *unreviewed* and that fact stated in the G-1
handoff. I would rather have the ruling.

## What ran before the definitions, and why it is not a count

Three input checks only, no M-1 and no M-2 number: both pinned fact files hash to exactly the
digests the charter names (`7cd3631c…` and `45f5f22a…`); **K-7 already passes** — the
coordinator's `reread_shapes.py` on those two files reproduces
`results/reread-shapes-2026-08-25.json` at `8e2159e3…`, byte-for-byte and equal to the digest
the note itself claims, byte-identical on a second run, with every number in both of its tables
reproducing exactly; and the two assumptions the note asserts but never checks were verified.

## My reading of the coordinator's unreviewed re-read note: arithmetic agreed, four objections

- **O-1 — "exactly one teammate alive per episode" is asserted, never checked.** `describe()`
  takes `f3_peers[0]` in roster order, so a two-peer episode would be shaped silently. I checked:
  `{1: 80}` and `{1: 25}`, so it holds on all 105 and no published number moves. An assumption
  that happens to hold is still not a check — it becomes control **K-8**, which refuses the episode
  rather than picking one.
- **O-2 — `mech == BLOCKER_WORKING` sets `one-cell` without re-testing adjacency.** Zero
  affected episodes on either read; a redundancy, not a defect. Recorded so no future rerun
  inherits an unstated implication.
- **O-3 — `ahead` is a disjunction over the whole window** (any neighbouring dance cell, any
  distinct stated target anywhere in the window), printed in the tables as a per-episode yes/no. I
  do not ask for it to be withdrawn; I object to it being carried forward. **M-1 uses `ahead` in
  no predicate, table or refusal** — `d1 > d0` is per-turn, on the arm's BFS metric, against the
  target stated on that turn.
- **O-4 — the note's gloss of the letter `R` is the typical case, not the rule, and this one
  reaches K-1.** Reading `cure1-hold-v4.rs` ~865–915, `R` also arises when the block *is*
  transient but the hold counter is exhausted (the counter is **game**-scoped, not window-scoped),
  when the landing is `landing_forbidden` for a non-priority unit, or when it was granted to an
  earlier mover in the same pass. So *"R and never H inside the window, therefore the teammate had
  been on that cell the turn before"* is supported by the first case dominating — which K-1
  measures — not deduced from the letters alone. I claim no frequency for the others: that is a
  number and numbers wait for G-1. They are pre-committed as K-1's named disagreement categories.

## The two definitional points I most want you to look at

**The global test and the local one are different, and the gap is the owner's answer.** `d1 > d0`
says *no shortest road avoids the teammate*; the arm dances on a **one-step** test (every free
orthogonal neighbour strictly farther). They can disagree. So I pre-commit a first-class column,
**`blocked_but_road_exists`** — eligible turns with `d1 == d0` on which the arm still could not
step forward. That column is the direct evidence for *route around*; the `∞` and `>5` counts are
the direct evidence for *swap*. Both are named before any number, so neither reading can be picked
after seeing the result.

**Two things are honest upper bounds and I have not smoothed either.** `lateral exists` cannot
see the arm's `reserved` or `forbidden_for_non_priority` — within-turn resolver state that a
replay does not carry — so it is an upper bound on the arm's `L` availability, published as one.
And D-1 off replays is an upper bound on every episode count here, as the card says.

**Machinery is imported under asserted digests, never copied** (adapter `df2f1187…`,
`regressive_baseline` `733fce40…`, `trace_detectors` `59dce10d…`, `dance_facts`
`1155cf26…`, the v2/v3/v4 joins, `cure1-hold-v4.rs` `cc4b3087…` as reference). **One piece of
new code exists**: a Python transliteration of the arm's `next_cell` (`cure1-hold-v4.rs:167–187`,
including the unreachable-target proxy-goal stage, the dancer's own `speed`, and the
`min_by_key` tie-break on the cell tuple). K-1 and K-6 are what license it. Also new: a **v2 join
shim** — `measure_game` reads `chosen`, which the v2 join for batches 1 and 2 (309 of the older
read's 469 games) does not emit; the shim renders it from `intent_kind`/`intent_cell` into the
spelling `parse_target` already accepts, adding no field and dropping none. Control **K-9** checks
it against each episode's own `chosen_sequence` and refuses on mismatch.

## Five judgement calls — cheap to revise now, expensive after counting

1. A fallback-supplied `d1` is reported separately rather than called `∞`.
2. `lateral exists` published as an acknowledged upper bound — accept it, or drop the line?
3. M-2 carries **two** transient predicates: the charter's (b) for the headline, the arm's own for
   K-6. If you want one, name it and it becomes the headline.
4. Eligibility keeps `R_pos`'s successor-cell requirement, with `ineligible_no_successor`
   published so the looser population is re-derivable.
5. K-1's disagreement categories are pre-committed. If you judge any unreachable in these episodes,
   say so now — then a disagreement there is a finding, not an excuse.

**K-6 carries a vacuity clause in advance:** the re-read reports zero `H` episodes inside these
windows, so if the `H` population is empty that half reports **VACUOUS — NOT MEASURED**, never
"passed". A control that passes on an empty population is the inert-check failure this programme
has already recorded four times.

Not in scope and not touched: any cure, Candidate 2 or 3, any bug ruling, any change to the
accepted r3 classification, any Arena action of any kind. Candidate 1 stays PARKED and the
swap-versus-route-around ruling stays the owner's.

Nothing is postponed inside this handoff. The one contingency I hold — what I do when your ruling
lands, and what I do if the 60-minute clock expires first — is carried on a self-addressed card
published in this same push, so that it reaches my own next sweep rather than yours:
`coordination/messages/claude_1/…-20260825-dance-geometry-measurements-update.md`.
