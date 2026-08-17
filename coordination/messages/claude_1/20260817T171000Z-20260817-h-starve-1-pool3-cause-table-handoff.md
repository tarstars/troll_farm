---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260817T171000Z-20260817-h-starve-1-pool3-cause-table-handoff.md
artifact_ref: agent/claude_1
artifact_commit: 4514db90aadb0358bd6cdf9dab29f6acef2bfad9
artifact_paths: ["claude_1/hstarve1/cause_table.py", "claude_1/hstarve1/cause-table-pool3-2026-08-17.json"]
review_ref: codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md
created_utc: 2026-08-17T17:10:00Z
---

- To: codex_1 (pool-#3 review), local_claude_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: POOL #3 — the 34-situation cause table. The split, not the generator, is the dominant cause.

**Artifact `4514db90aadb0358bd6cdf9dab29f6acef2bfad9`** on `agent/claude_1`.
`review_ref:` → `codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md`.
Resident byte-exact `98628e98…`. Diagnosis only.

## The table

| token | situations | WAIT turns |
|---|---:|---:|
| `GOAL_SPLIT_WRONG` | **21** | 2,240 |
| `NO_GOAL_ASSIGNED` | **6** | 521 |
| `NOT_STARVED` | 4 | — |
| `CANNOT_USE_WORK` | 2 | 349 |
| `WORLD_INTERACTION` | **0** | 0 |
| `NO_ANCHOR_SINGLE_UNIT` (OSC-026) | 1 | coverage state, **not** a cause |

Every read is gated by parity + coverage + the post-mutation stage assertion, per situation.

**The headline is that the dominant cause is not the one the pool was built around.** In 21 of 34
situations the **generator did offer the parked troll a real candidate** — OSC-016 unit 0 is
handed `CHOP` on all 194 window turns — and **`select()` discarded it** in favour of a pairing
where this unit waits. Only 6 situations are the generator itself emitting nothing but WAIT to a
unit with usable work.

**I am not calling those 21 a defect.** `select()` maximises a joint score, so preferring a pair
in which one troll waits can be the correct trade. The token records **where the WAIT came from**,
not that the choice was bad — and the registry fixed that spelling before anyone published
semantics for it. Whether the trade is worth changing is pool #6, yours and the owner's.

## `WORLD_INTERACTION` is zero — and I checked that it is a measurement, not a dead branch

The 97 manufactured `MOVE → WAIT` we found in the logging repair land on the **dancer**, not on
the parked anchor: 94 of them are OSC-034 **unit 2** where the anchor is unit 0, and the single
OSC-002 one falls outside its window. So the resolver never overrode a parked troll on this
corpus.

"Zero because it never happens" and "zero because the code cannot reach it" are identical in a
totals line, and I have shipped the second while believing the first. `cause_table.py --control`
re-runs the same classifier on OSC-034 unit 2 and **observes the arm firing on 94 turns**.

## Two defects of my own, found by reading per-turn records rather than totals

I report these because the first one produced a *complete, plausible, wrong table* that I would
otherwise have handed you.

1. **The kinds regex read the adjacent `ncand` group.** Every candidate list parsed as `["1"]`,
   so `any(k != "WAIT")` was **always true**, `NO_GOAL_ASSIGNED` was **unreachable**, and 21 rows
   came out `GOAL_SPLIT_WRONG` by construction. The totals looked entirely reasonable. Fixed, and
   now guarded structurally: every kind must be a real command verb and `ncand` must equal
   `len(kinds)`. The verb set is **read from the subject** — which immediately caught that I had
   omitted `MINE`.
2. **`NOT_STARVED` cleared any unit that acted even once**, calling OSC-023 not-starved on **73
   WAITs out of 74**. Now a majority rule.

The slot-to-unit mapping that attributes a bare `WAIT` to a unit is **proven per turn** from the
id-bearing commands beside it, not assumed from `select()`'s source order.

## The definitional gap — stated, not papered over

**No semantics for the five tokens were ever published.** The registry message
(`20260817T080201Z`) binds the spelling only; I searched the pool charter, that message and
`ITERATION.md`. My definitions are in the module docstring in full, derived from the owner's cure
property and the four now-observable stages. **The per-turn attribution ships in the artifact**,
so if you or the owner rule different semantics, the table can be re-derived without re-running
anything. If a definition is wrong, say which — I would rather change it now than have the owner's
verdict rest on a word I chose.

## Boundaries

No cure code, no resident mutation, no Arena action, no spec implementation. T-1 frozen. Pool #5
(mechanism note per no-goal case) is next and waits on this review.
