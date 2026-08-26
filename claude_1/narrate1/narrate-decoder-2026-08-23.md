# The NARRATE v2 decoder — built, swept over 149 real ladder games, 12 controls fired

**Card:** `local_claude_1` `20260823T103000Z` (`20260823-narrate-real-game-telemetry`),
`coordination/GOAL.md` item 2. **Status:** delivered, awaiting codex_1's independent re-run.

**Artifacts**

| path | what |
|---|---|
| `claude_1/narrate1/narrate_decode.py` | the decoder: replay → our seat's per-turn intention, joined to the accepted replay→`Trace` adapter |
| `claude_1/narrate1/narrate_controls.py` | 12 controls on a real replay; each corrupts exactly one guarded thing |
| `claude_1/narrate1/run_narrate_panel.py` | sweep + controls in one gate; PASS only if both hold |
| `claude_1/narrate1/results/narrate-decode-panel-2026-08-23.json` | the panel result |
| `claude_1/narrate1/results/narrate-join-sample-900089738.json` | the first 400 join rows of one game, so the output shape is readable without re-running |

**Corpus (supplied, not fetched — this host has no platform session credential):**
149 replays of agent `6652424` at `agent/local_claude_1@ac65523b:local_claude_1/narrate/games`,
digest `sha256:a319f02c…d323ac7c` over `(basename, sha256)` of all 149 files. Extracted with
`git archive` to `~/.cache/troll-farm/narrate-games` — **local scratch, outside the repo**, and
the games directory is a parameter. `data/raw/games/` is neither read nor written (protocol §7).

## Result

```
python3 claude_1/narrate1/run_narrate_panel.py --games-dir ~/.cache/troll-farm/narrate-games
```

| | |
|---|---|
| games decoded end to end | **149 / 149**, 0 refused |
| traced turns | **38,869** |
| join rows (turn × own unit alive) | **76,305** |
| telemetry on the opponent's seat | **0**, over all 149 |
| seats played | 61 as seat 0, 88 as seat 1 |
| unit-id sets | `0,2` `0,3` `1,2` `1,3` **`1,4`** |
| controls fired | **12 / 12** |
| panel | **PASS** |

`1,4` is a fifth unit-id set the coordinator's 20-game identity check did not reach; the decoder
takes the roster from the state rather than from any assumed id pair, so it needed no change.

## Requirement 1 — a mis-joined seat is not merely unlikely, it is unspellable

The decoder has **no seat parameter and never will**. The only identity it accepts is `agent_id`,
resolved by `replay_to_trace.resolve_seat` against the replay's own `agents` array — the entry whose
`agentId` is ours carries `index`, and that index is the frame `agentId`. The battle listing's
`position` is never consulted because this module never sees a battle listing.

That alone would still be a design argument, so it is also **measured per game**: our telemetry must
be present on our seat every traced turn and **absent** on the other, or the game is refused.
Control 2 spends the opponent's agent id on a real replay and gets

> `NARRATE telemetry appears on the opponent's seat (262 turns of seat 0)` — refused.

Control 3 injects one `MSG NARRATE` line into the opponent's stdout on an otherwise clean game and
is refused on the same check with a count of 1. The inverted join produces a **refusal**, not
numbers.

## Requirement 2 — refuse, never partially decode

Every defect raises `NarrateError` with a reason and the whole game is dropped; nothing returns a
short or patched row set. Guarded: an `AdapterError` from the replay itself; a turn with zero or
more than one `NARRATE` segment; a version token that is not `v2`; `t=` disagreeing with the aligned
turn index; a malformed unit token, target shape or coordinate; a unit id repeated in one payload;
a roster that is not exactly the own units alive in that turn's state; telemetry on the wrong seat.

**Roster completeness is enforced against the state, not against the payload.** A unit alive in
`S_t` and absent from the payload is a decode error, never a `NONE` — absence is never readable as
an intention, which is the load-bearing rule of the grammar spec.

## Requirement 3 — the grammar is frozen at v2

Read starts at the `NARRATE` token, so turn 1's banner (`MSG yamo-…-rust NARRATE v2 t=1 …`) and the
bare turn-*t* form parse through the same path with no special case; both occur in the corpus.
`NONE`/`SHACK` take no cell, `BANK`/`CELL`/`TREE` require one. An unrecognised version is refused
rather than guessed (control 6).

## Requirement 4 — the controls

All twelve fire, on the real replay `900089738`, and the baseline is first because otherwise the
other eleven prove nothing:

| # | control | refusal it produced |
|---|---|---|
| 1 | clean case (baseline) | accepted: 502 rows / 262 turns, seat 0, leak 0 |
| 2 | wrong seat — the opponent's agent id | telemetry on the opponent's seat, 262 turns |
| 3 | the opponent's `MSG` mistaken for ours | telemetry on the opponent's seat, 1 turn |
| 4 | dropped turn | turn 41 carries 0 NARRATE segments |
| 5 | two segments in one turn | turn 42 carries 2 NARRATE segments |
| 6 | corrupted grammar — version `v3` | unrecognised grammar version |
| 7 | corrupted grammar — `x0=` unit token | malformed unit token |
| 8 | corrupted grammar — `FIELD(…)` target | target kind is not one of BANK/CELL/TREE |
| 9 | corrupted grammar — a unit id twice | unit 0 appears twice in one payload |
| 10 | turn misalignment — `t=` shifted by one | payload says t=22 on traced turn 21 |
| 11 | roster incompleteness — a live unit dropped | payload `[0]`, state `[0, 2]` |
| 12 | unknown agent id | adapter refused: agent 1 appears 0 times in the agent table |

## What the join shows, descriptively — and three shapes a reviewer should see named

Intentions over 76,305 rows: `TREE` 47,307, `BANK` 21,843, `CELL` 3,640, `NONE` 3,515, **`SHACK` 0**.

**`SHACK` never occurs in 149 real games.** The parser handles it and the grammar keeps it, but the
live corpus exercises four of five shapes. Said here rather than left for a reviewer to find.

Intention against the verb actually issued (top rows):
`TREE|CHOP` 25,096 · `TREE|MOVE` 21,959 · `BANK|MOVE` 17,100 · `BANK|DROP` 4,738 ·
`NONE|(none)` 3,504 · `CELL|PICK` 1,480 · `CELL|PLANT` 1,479 · `CELL|MOVE` 548 ·
`TREE|HARVEST` 148 · `TREE|(none)` 104 · `CELL|MINE` 101 · `CELL|DROP` 32 · `NONE|MOVE` 11 ·
`BANK|(none)` 5.

Three shapes are worth naming, and **none of them is a decode error** — the decoder refuses those:

- **`(none)` = a bare `WAIT`.** `WAIT` carries no unit id, so `trace.cmd_of(uid, t)` is `None` for
  every unit that turn. 3,613 of 76,305 rows.
- **`TREE|(none)` 104 and `BANK|(none)` 5** — a unit whose selection recorded a real target, on a
  turn whose emitted command was `WAIT` (e.g. `900089741` t=4: `MSG … u1=TREE(16,3);WAIT`).
- **`NONE|MOVE` 11** — the converse: `Target::None` recorded, a `MOVE` issued for that unit
  (`900089904` t=240: `… u3=NONE;MOVE 3 11 10`).

The last two are the same structural fact and it is the reason the join is worth having: **the
telemetry records the intention at selection time, and the command can be rewritten after
`select_recording` has filled the map** — conflict resolution and the door-unblocking/idle-harvest
injections both emit commands the selection pass did not record a target for. I am *naming the
mechanism as the candidate explanation, not asserting it*: 120 rows is a small enough set to
adjudicate exactly, and it is not this card's scope to do so. What is established is that
intention ≠ command is **observable** and lands on 120 of 76,305 rows.

## Scope — what I did not do

No grading of dancing, blocking or idleness. No prevalence number and no treatment of these 149
games as a prevalence base — the coordinator flagged that my prevalence card lists a NARRATE corpus
as an unblock signal and that this corpus is not one: single agent, mid-maturation, and the card's
question names resident `6561795`, a different lineage. **That card stays parked and I am not
discharging it here.** No cure claim. No Arena action, no fetch, no submission, no edit to
`cgauto/submissions/`, and no write anywhere near `data/raw/games/`.

## For codex_1

The ruling most wanted, per the card, is that a mis-joined seat is impossible to express. The
attack surface is small and I would point it at three places: `decode_game`'s refusal to accept
anything but `agent_id`; `opponent_narrate_count`, which is the control that caught the
coordinator's inverted join in the first place; and the roster equality against
`trace.state(t).own_units()`, since it is what stops a wrong seat from being absorbed as a `NONE`.
One residual worth ruling on rather than leaving implicit: if an opponent ever runs our instrument,
the leak check refuses the game rather than decoding ours — fail-closed, and stated in the refusal
message, but it is a policy choice and not the only defensible one.
