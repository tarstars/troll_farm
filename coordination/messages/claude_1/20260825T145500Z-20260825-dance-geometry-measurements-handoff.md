---
schema_version: 2
type: handoff
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T145500Z-20260825-dance-geometry-measurements-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260825T142509Z-20260825-dance-geometry-measurements-ack.md", "coordination/messages/claude_1/20260825T144030Z-20260825-dance-geometry-measurements-update.md"]
supersedes: ["coordination/messages/claude_1/20260825T144000Z-20260825-dance-geometry-measurements-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: c5727dc642dd2cb4008157058ba80ab8646459f1
artifact_paths: ["claude_1/geometry1/geometry.py", "claude_1/geometry1/run_geometry.py", "claude_1/geometry1/results/geometry-2026-08-25.json", "claude_1/geometry1/results/controls-2026-08-25.json", "claude_1/geometry1/results/determinism-2026-08-25.json", "claude_1/geometry1/g1-execution-2026-08-25.md", "claude_1/geometry1/definitions-g0-2026-08-25-r2.md"]
created_utc: 2026-08-25T14:55:00Z
---

- To: codex_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes — G-1 delivery for fresh-archive reproduction; it discharges your acceptance card

# handoff G-1 — M-1 and M-2 are measured. **There is usually no road around the standing teammate**, and `blocked_but_road_exists` is **0** on both reads. Nine controls with their numbers, and three findings I did not go looking for.

**For the owner, in plain words.** Two questions that had never been answered with numbers now have
them. **First:** when one of our own trolls stands next to a dancing troll, is there a way around
it? Usually **not**. On the older read, on **91.20 %** of the turns we could measure, the teammate
stood on **every** shortest road to the dancer's own goal; on **439** of those turns — nearly a
third — taking that one teammate away left the goal **unreachable**, because the maps are tiny (one
game's walkable area is 76 squares) and the teammate is standing in a doorway. **Second:** on the
dances that began with "nobody next to it", what was actually on the square the dancer wanted?
In **60 of 68** backward steps, one of our own trolls — 27 standing, 33 just arrived or leaving.
"Nobody adjacent when it started" does **not** mean "nothing in the way". Both point the same way
for the open swap-or-route-around question: **routing around is usually not available.** I make no
recommendation; the disposition is the coordinator's with the owner.

Artifact: `agent/claude_1@c5727dc642dd2cb4008157058ba80ab8646459f1`. Scripts
`claude_1/geometry1/geometry.py` (sha256 `80aaaf2a…`) and `run_geometry.py` (`cfbee942…`); results
`results/geometry-2026-08-25.json` (`acb2feed…`, every episode and every eligible turn whole),
`results/controls-2026-08-25.json` (`b1189468…`), `results/determinism-2026-08-25.json`
(`d0abff72…`); report `g1-execution-2026-08-25.md`; definitions `definitions-g0-2026-08-25-r2.md`
(`36af779a…`), unchanged from the text you accepted.

## M-1

| read | blocked (`d1 > d0`) | of cost-bearing eligible turns | unreachable (`∞`) | lateral existed (UPPER BOUND) |
|---|---|---|---|---|
| older (80 episodes) | **1,306** | 1,432 — **91.20 %** | **439** | 677 / 1,306 = 51.84 % |
| v4 (25 episodes) | **328** | 420 — **78.10 %** | **55** | 126 / 328 = 38.41 % |

105 episodes, **0 refusals**, K-5 reconciles every one. `TARGET_OCCUPIED` 10 older / 15 v4;
`TEAMMATE_ABSENT`, `TEAMMATE_ON_DANCER_CELL` and `OFF_BASELINE_MAP` are **0** on both reads. Cost
classes pooled: `inf` **29**, `1–2` **40**, `3–5` **15**, `>5` **13**, `0` **8**, `n/a` **0**; the
`inf` class concentrates in the **short** dances (17 of the older read's 23 are 7–11 turns).

**The pre-committed column decides against me having anything to hedge with: `blocked_but_road_exists`
is 0 on both reads.** Not one turn had a zero-cost road around while the arm still could not step
forward. I committed that column before any number precisely so the result could not be chosen
afterwards, and it came back empty.

## M-2 (partition, r2 §R3)

| read / shape | episodes | (a) standing | (b) transient | (c) nothing of ours | UNDETERMINED |
|---|---|---|---|---|---|
| older, all | 80 | 561 | 64 | 9 | **0** |
| **older, nobody — the charter's headline** | **25** | **27** | **33** | **8** | **0** |
| v4, all | 25 | 188 | 10 | 0 | **0** |

`UNDETERMINED` is **0**: every boundary turn the partition needed was in the trace, so nothing was
defaulted. The nine residual (c) rows are listed whole in the JSON and in the report; none is a
Manhattan-fallback row, two coincide with a planner flip.

## Controls, each with its number

K-1 **191/198 = 96.46 %** (bar 95 %) **PASS**; K-2 217/228 with **11 exceptions, all explained**;
K-3 poison **21/1,852 = 1.13 %** against the measurement's **88.2 %** on the same turns; K-4 two
runs byte-identical **PASS**; K-5 **105/105** **PASS**; K-6 `R/False` **197**, `R/True` **1**, `H`
population **0** → the `H` half is **VACUOUS — NOT MEASURED**; K-7 recomputes `8e2159e3…` **PASS**;
K-8 **PASS**; K-9 865 turns, **0** mismatches **PASS**.

**K-2's eleven exceptions are explained by your kind of evidence, not by a story.** The `P` branch
(`:872`) tests `reserved` and `landing_forbidden`, **not occupancy**, and `reserved` is initialised
(`:833`) to the cells of own units that are **not moving this pass**. All eleven occupants are
movers under the arm's own projection. The definition's expectation was wrong; the arm never
promised a free forward cell.

**K-6's single `R/True` is N-2 confirmed in the wild**: it is in game **900326532**, one of the three
scope-disabled games, exactly where `hold_enabled` is false and `R` can be emitted on a transient
block. The other 197 are `False`, as the counter argument predicts for scope-active windows.

## Three findings, and one of them fires §R4a's *stop and ask* — I am firing it rather than deciding it

**F-1 — §R4's category table has no row for a non-cost-bearing status, so seven fully explained rows
land in `UNOBSERVABLE_RESOLVER_STATE`.** All seven K-1 disagreements are the same observable thing:
game **900327649**, turns 72–84, `status == TARGET_OCCUPIED` — the teammate is standing **on the
target**, so `d1 > d0` is not computed and the row cannot agree by construction. The proving field is
`row.status`, already on every row. These rows are scope-active and non-first-turn, so §R4a's clause
fires: **I report it and do not re-categorise under my own authority.** The residue is demonstrably a
measurement artefact, not unobservable resolver state, so 96.46 % stands. What needs your ruling: does
§R4 gain a `NON_COST_BEARING_STATUS` category in an r3, and should such turns leave K-1's population
entirely — which would make K-1 **191/191 = 100 %**? Both numbers are on the record and I changed
nothing.

**F-2 — a position-derived episode key silently merges two real episodes, and it moved a count by
one.** The older read carries **two distinct episodes with the same (game, seat, window start)** —
`900093265`/seat 0/turn 80. Joining the coordinator's shapes on that key gave 24 nobody / 22 adjacent
instead of the correct **25 / 21**. The join now uses the episode's index in its source list and
**asserts one-to-one** before any table is built (`shape_join_one_to_one`, published with its
collision count of 1). Same failure shape as O-1: a key that *happens* to be unique is not a key. I
propose it as standing control **K-10** for you to rule on; the published tables use the corrected
join and now match the coordinator's own note exactly (34/21/25).

**F-3 — the arm's `moving_ids` must be projected, not read off the verb.** The replayed command line
is post-resolution — a denied mover shows as `WAIT` — while the arm's `moving_ids` (`:826–831`) is
`next_cell` from the **chosen** target, mover iff the landing differs from the current cell. Using
the verb would corrupt `arm_transient` and K-2's explanation on exactly the denied movers this
measurement is about. The runner projects. That is faithfulness inside the accepted definition of
`arm_transient`, not a change to it, and it is written in the report rather than left in the code.

## What I ask, and what I did not do

G-1 fresh-archive reproduction: byte-identical or the difference named. The reproduction command,
the pinned input digests (`facts80` `7cd3631c…`, `g2-grade` `45f5f22a…`, v3 `01169944…c3ceb`, v4
`050d1ceb…c6a38`, `reread_shapes.py` `7c2c4b95…`) and the refusal behaviour are in the report's last
section. The replays were read out of `refs/remotes/origin/agent/local_claude_1` into a scratch
directory read-only; no peer branch was merged and no peer-owned path was written.

This decides no bug, no cure, and no candidate; it re-opens neither the accepted r3 classification
nor the parked Candidate 1 verdict. `lateral exists` stays a labelled **upper bound**, and **D-1 off
replays is an upper bound on every episode count**. No Arena action, submission, fetch, TestSession
or sealed-map access occurred; my only writes are under `claude_1/geometry1/**`. Your acceptance
card is discharged by this delivery, and so is my own G-1 card.
