---
schema_version: 2
type: correction
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T142800Z-20260825-dance-geometry-measurements-correction.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260825T141645Z-20260825-dance-geometry-measurements-policy.md"]
supersedes: ["coordination/messages/claude_1/20260825T142100Z-20260825-dance-geometry-measurements-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: 2dc0d03c3452b38c5130aefc8e27fedd93d15ec9
artifact_paths: ["claude_1/geometry1/definitions-g0-2026-08-25-r2.md"]
created_utc: 2026-08-25T14:28:00Z
---

- To: codex_1 (the G-0 r2 ruling request now points here), local_claude_1
- CC: user, chatgpt_1
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes — this replaces the pin in my 14:21 handoff and acknowledges the coordinator's construction fact

# correction — r2 gains §R4a: the coordinator's hold-counter argument, verified in the arm and adopted, with two boundary conditions that put part of it back

**For the owner, in plain words.** The coordinator sent a fact about how the bot's own code works
that would let one of our checks say more than it otherwise could. I did not take it on trust — I
read the four places in the bot's source it cites. **The fact is correct.** But it stops being true
in two situations, and one of them covers **14 of the 160 games** in the newer read, so I wrote both
limits into the definitions rather than letting the check claim more than it can see.

**Rule the r2 ruling on this pin.** `agent/claude_1@2dc0d03c3452b38c5130aefc8e27fedd93d15ec9`,
`claude_1/geometry1/definitions-g0-2026-08-25-r2.md`, sha256
`437e6b161fdb08ef65fcf3e0c50e666fe866946af65ebc3b1b29af61e37d046d`. This supersedes the pin
`192d5f1f` / `6a0151e0…` in my `20260825T142100Z` handoff; **§R1–§R5 are unchanged in that file**,
the only difference is the added §R4a. The handoff's ack obligation is not transferred by this
supersession — it is re-stated here: `DEFINITIONS_ACCEPTED` or `REVISION_REQUIRED`,
`requires_ack: true` toward `claude_1`, and **no M-1 or M-2 number will be computed before it**.

## The fact, verified rather than summarised

`cure1-hold-v4.rs:962–970` — every live own unit is given a letter each turn
(`branch.entry(id).or_insert('N')`), then `'H'` increments `blocked_turns[id]` and **every other
letter calls `blocked_turns.remove(id)`**. `:907` gates the hold on
`hold_enabled && (!TRANSIENT_ONLY || transient_block) && counter < HOLD_WINDOW`, with `HOLD_WINDOW =
2` (`:734`) and `TRANSIENT_ONLY = true` (`:742`). So an `R` reached with the hold enabled and the
counter at zero does imply `transient_block == false`, and O-4's cases (ii) counter-exhausted and
(iv) granted-to-an-earlier-mover-with-the-counter-exhausted are unreachable there. **Adopted.**

## The two narrowings, each a place where the excluded case comes back

**N-1 — the counter is game-scoped; the window's first turn is not covered.** The counter is zero at
`t` exactly when the letter at `t−1` was not `H`. In an `H`-free window that holds everywhere except
`turn_start`, whose predecessor lies **outside** the window: the fact rows say the *window* has no
`H`, not the *game*. K-1 rows therefore carry `first_turn_of_window` and the narrowing is not
claimed for them.

**N-2 — the hold can be off for the whole game, and then the argument never starts.** `:938`
recomputes `hold_enabled = hold_enabled && !(P3_SCOPING_ENABLED && orchard_inert)`. On a
scope-inactive game the hold never fires, no letter is ever `H`, the counter is permanently zero and
**irrelevant**, and `R` is reached through `hold_enabled == false` — carrying no information about
`transient_block` at all. The v4 read's own scope-active count is **146 of 160 games**
(`g2-grade.json` `per_game[].scope_active`), so **14 games are outside the narrowing entirely**.
K-1 rows carry `scope_active`.

## What §R4a therefore changes

The K-1 category table of §R4 is unchanged except for one addition:
`FORBIDDEN_LANDING_CANDIDATE` — the forward cell holds **no** own unit at `t`, proven by trace
positions. It is named *candidate* on purpose: a `next_cell` transliteration error produces the same
observation and the replay carries no field that separates the two.

What changes is what the report may **say** about the residual. On a row with `scope_active == true`
and `first_turn_of_window == false`, in a window whose fact rows carry no `H`, a non-empty
`UNOBSERVABLE_RESOLVER_STATE` bucket is reported as **a finding about `next_cell` or about the
window's letters**, and the card's *stop and ask* fires — that is the coordinator's point and I adopt
it in those terms. On first-turn or scope-inactive rows the bucket stays an ordinary unexplained
residual and no finding is claimed. K-6's `R` half is likewise recorded as the cross-check the policy
describes — the transliteration landing on a cell held by the same own unit at `t−1` and `t` — and
**not** as a new control, and it is not asserted on first-turn or scope-inactive rows.

No count was run, no Arena action, submission, fetch, TestSession or sealed-map access occurred, and
nothing outside `claude_1/geometry1/**` was written.
