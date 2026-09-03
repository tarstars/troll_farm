# Task 20260903-owner-live-observations — three things the owner saw the bot do on the platform

- Born: 2026-09-03 13:5xZ, from the owner's own watching of the live ladder games of submission `41236483`
  (the opening dispatcher, stage 2A, up at the owner's word 13:10:07Z).
- Owner: claude_1 reads; the coordinator verifies every number by execution.
- Kind: **a read, not a build.** No build, no ladder hour, no platform action is authorized by this card.
- Done when: each of the three observations has a number attached — how often it happens, what it costs in points,
  and whether it is a defect in a rule or a consequence of a rule that is right.
- Dead when: an observation is measured at a cost below the field panel's resolution (about ±5 points a game) —
  then it is recorded as seen-and-small, and no build follows.
- Budget: one read, two days (to 2026-09-05 14:00Z). One design round afterwards only on the owner's word.

## The owner's words

> "I can see that trolls switches a lot and waste time on switches. Also endgame misses chopping tree left and
> chopping down plants which were planted by enemy"

Three separate claims, to be measured separately:

1. **Switching.** Trolls change target often and lose turns to the change.
2. **Trees left standing.** At the end of the game, trees are left uncut.
3. **Enemy-planted trees.** Trees the opponent planted are not cut down.

## What the coordinator established before chartering, by reading the source (leads, not conclusions)

**On (3), what the platform allows.** The champion's `Plant` structure — which is exactly what the referee sends us —
carries `kind`, `cell`, `size`, `health`, `fruits`, `cooldown` and **nothing about who planted it**. There is no owner
field in the protocol, so "a tree the enemy planted" is not something the bot can be told; it can only be *inferred*,
by remembering that a plant appeared on a cell that was empty and that an opponent troll was standing there. So
observation (3) is not a missing filter — it would be a new piece of bookkeeping. Any design round must cost that
inference before proposing a rule that uses it.

**On (2) and (3), the mechanism most likely responsible — one rule, in `chop_candidates`.** A tree is dropped from
consideration entirely unless the troll can reach it, fell it, **and carry the wood back to the shack** before the last
turn:

```rust
let turns = (travel_turns + chop_turns + return_turns + 1).max(1);
if turns > TOTAL_TURNS - view.turn + 1 { continue; }
let wood = final_size.min(unit.free_capacity());
if wood <= 0 { continue; }
```

and, before the loop runs at all, `if unit.stats.chop_power <= 0 || unit.free_capacity() <= 0 { return out; }` — a troll
with full hands has no chop candidates whatever is standing next to it.

This is **correct as written** if wood only scores from inside the shack: cutting wood you cannot bank earns nothing.
But it also means that in the last stretch of the game the candidate list empties while trees are still standing, and
the trolls stop — which is exactly what the owner saw. It also reconciles the owner's eyes with Track E's read of
2026-09-02, which found a fifth of our late troll-turns carrying no command and 84 % of those "terminal waits with
nothing reachable to fell or bank". **Both are right: the trees are there, and the bot has ruled them out.**

What the read must therefore settle is not "is there a bug" but **what the unbanked cut is worth**: felling a tree we
cannot carry home still takes the tree away from an opponent who could have harvested or felled it, and a partly
chopped tree is worth less to them. That value is unmeasured. Note the standing evidence points the other way for
*mid-game* denial: the champion of record is the *denial-off* bot (its plum/lemon denial bonus was removed on 08-27 and
the simpler bot read no worse, 21.2), and `rust/src/planner.rs`'s own comment records "against a replanter, denial is
self-defeating". The endgame case is a different question and has never been measured.

**On (1), what is already known.** Target thrash has a history on this project: Track D's dancing-troll programme
(candidates 1, 2, 3, 3b) all died, and the 2026-08-25 instrumented read found the dancer's path runs through a working
teammate's cell. Separately, stage 2A's own opening dispatcher hit a two-cell dance during its build and claude_1
fixed it with a 5 % hold on last turn's target plus position-free distance references. **The owner is reporting
switching in the live games of the build that contains that fix**, so the fix is either incomplete or the switching the
owner sees is in the champion's own play after the third troll, not in the dispatcher's opening. The read must say
**which phase the switching lives in** before anyone proposes a cure.

## The read, as chartered

Measure on real games, not on hand-picked examples. Two populations are already collected and need no new play:
the champion of record's 160 ladder games (`local_claude_1/ladder-queue/games-41234663/`) and the opening dispatcher's
160 games from the hour running now (`games-41236483/`, collected ~14:12Z). `local_claude_1/apple-farm/ladder_read.py`
is the decoding pattern; Track E's `claude_1/endgame-gap/` and `claude_1/h2h-panel/endgame_sig.py` are the instruments
nearest this question.

1. **Switching.** Per troll, per turn: how often the target cell changes while the previous target is still valid and
   reachable; the turns lost to it (steps walked away from a target later returned to); the distribution by phase
   (turns 1–70, the dispatcher's window in the new bot, and 71–300, the champion's own play). Report the two bots
   side by side — the champion's own games are the control, and they say whether this is new or ancient.
2. **Trees left standing.** At the last turn: how many trees stand, their size and health, their distance from our
   shack, and **how many of them a troll could have felled and banked in time** (the same arithmetic
   `chop_candidates` does) versus how many were ruled out by the carry-home test. Split the second group by what
   blocked it: too far to return, hands full, chop unfinishable, unreachable.
3. **Enemy-planted trees.** Reconstruct provenance from the recorded turns (an appearing plant plus an adjacent
   opponent troll the turn before) and report: how many trees the opponent plants a game, how many we fell, how many
   are still standing at the end, and the fruit the opponent harvested from the ones we left. State plainly how
   reliable the inference is and how many plants it cannot attribute.

Report one number per observation and one sentence on whether a rule change could plausibly recover points, with the
size. **No design, no build in this card.**

## Log

- 2026-09-03 13:5xZ born from the owner's live watching; the coordinator's source reading above; chartered to claude_1
  ack-required. The three observations are the owner's, the two mechanisms named are the coordinator's leads and are to
  be confirmed or refuted by measurement, not assumed. — coordinator
