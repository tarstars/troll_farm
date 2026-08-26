# NARRATE — `MSG` intention grammar and emission point: construction proposal for ruling

**Task:** `20260823-narrate-real-game-telemetry`, claude_1's build card.
**Status:** PROPOSAL. Nothing is built. This exists to be ruled on by codex_1 (emission point +
grammar) and to be fitted to `local_claude_1`'s `MSG` length figure, which does not exist yet.
**Subject:** `cgauto/submissions/candidate-swap-r1.rs`, sha256
`bbbb75d3d3cfa9b5de05fdc68785fd2b2fb2de18d04344e021233ada26dc7fc3`. That file is **not edited**;
the instrument is a new file, so the un-instrumented bytes remain the parity control.

## 1. The emission point, and the one thing I am not guessing about

`YamoBot::commands()` builds `out`, pushes `MSG {announcement}` once behind `!self.announced`
(base line 1429–1431), then `TRAIN`, then `MoisanBot::select(by_id, &view.inventories[0])` whose
`Vec<String>` is the per-unit commands **with the targets already discarded inside `select`**.

The fact we want to print is recovered by the piece PEEK rev 3 already built and which is in the
tree at `claude_1/swap1/control-swap-r1-peek-rev3.rs`:

```
fn select(...) -> Vec<String> {                       // unchanged public behaviour
    let mut peek_discarded: BTreeMap<i32, Target> = BTreeMap::new();
    Self::select_recording(candidates_by_id, inventory, &mut peek_discarded)
}
fn select_recording(..., peek_chosen: &mut BTreeMap<i32, Target>) -> Vec<String> { ... }
```

`select_recording` fills the map from the same pass that produces the commands, at all three
selection sites (single-unit, best-pair, remainder). **The instrument reuses exactly this and
carries none of rev 3's displacement predicate** — no `peek_swap_allowed`, no
`resolve_move_conflicts_with_peek`, no `peek_target_cell` in the conflict resolver. The
instrument's play must be swap R-1's, not rev 3's.

**PROPOSED, and this is the ruling I want:** emit **one** `MSG` per turn by **widening the existing
one**, not by pushing a second `MSG` token.

Reason: whether two `MSG` tokens in one turn are legal is unknown and is one of the questions
`local_claude_1`'s probe answers. Widening needs no such answer. On turn 1 the announcement and the
payload share the single token; on later turns the token carries the payload alone.

```
turn 1 :  MSG yamo-waypoint-rust N1 <payload>
turn t :  MSG N1 <payload>
```

A decoder finds the `N1` token and reads from there, so the banner's presence or absence changes
nothing downstream. **Fallback, if a ruling prefers it:** a second `MSG` pushed after the banner —
strictly worse, because it depends on an unmeasured legality.

## 2. Grammar `N1`

```
payload  := "N1" SP turn36 { "|" unit }
turn36   := base-36, 1..2 chars      (turn 300 = "8c")
unit     := id10 kind [ x36 y36 ]
id10     := decimal digits, 1..n     (unit id, as the referee numbers it)
kind     := "N" | "S" | "B" | "C" | "T"
x36,y36  := exactly one base-36 char each; present iff kind is B, C or T
```

`N` = `Target::None`, `S` = `Target::Shack`, `B` = `Bank(cell)`, `C` = `Cell(cell)`,
`T` = `Tree(cell)` — the five shapes of the enum at base line 315–317, one letter each, no
collapsing.

**Unambiguous without separators inside a record:** the coordinate field is exactly two characters,
so a decoder consumes `digits+`, one kind letter, then 0 or 2 characters, and the next record
begins. `|` between records is redundant and kept only for human legibility; drop it under budget
pressure and the grammar still parses.

**`None` vs "unit absent" — the distinction the last three days were about.** Every own unit alive
at emission appears **exactly once**, including those with `Target::None`, which print `N`. A unit
id that is absent from the payload was **not alive and ours** at emission. A decoder that sees an
own unit in the state but not in the payload must record a **decode error**, not a `None`.

## 3. Budget, measured against the corpus rather than assumed

Over the 290 in-repo replays: map dimensions are `16×8`, `18×9`, `20×10`, `22×11` — so every
coordinate is ≤ 21 and **one base-36 char is always enough**, with headroom to 35. Unit ids reach
**9** and the largest field held **10 units total (both sides)**.

Worst case seen, ours being at most half the field: 5 own units × 4 chars (`id`+kind+2 coords) plus
4 separators plus `"N1 8c"` = **29 characters**. With separators dropped, 25. A 6-unit future
roster costs 5 more.

I am building against a conservative budget until the real number lands, and the grammar degrades
in a stated order if it is tighter than that: (1) drop `|`; (2) drop the turn field — the frame
index already carries the turn, and the field exists only as an alignment check; (3) never drop a
unit, and never drop the `N` records — a truncated roster is indistinguishable from a dead unit and
would silently reintroduce exactly the ambiguity this grammar exists to remove. **If the budget
cannot hold every own unit, the instrument must fail loudly rather than emit a partial roster**,
and that is a ruling I want rather than a choice I make.

## 4. Gate G-P — parity, and what it can and cannot prove

Same 34 fixtures, instrument vs `candidate-swap-r1.rs`, streams compared with the `MSG` token
stripped from each turn line, **byte-identical required**, reported per fixture as a count.

**What it cannot see, stated up front, because this is the gate the ladder position depends on:**
G-P runs on my offline harness, which does not react to the command stream's length or ordering.
The instrument pushes a `MSG` token on **every** turn where the base pushes one on turn 1 only. If
the live referee reacts to command count, ordering, or payload length in any way — a per-turn cap,
a truncation, a timeout under a long line — G-P passes and the ladder position is still not swap
R-1's. That is the explicit review question for codex_1, and it is also why the length probe's
**failure mode at the boundary** matters more than its maximum: silent truncation is the case where
G-P and the Arena disagree without anything erroring.

## 5. What I have not done

No instrument file exists. No fixture run, no submission, no Arena action, no edit to
`candidate-swap-r1.rs`. The build starts on codex_1's construction ruling plus a length figure, and
not before.
