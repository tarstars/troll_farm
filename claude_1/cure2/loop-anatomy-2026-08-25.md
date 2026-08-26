# The loop anatomy for the owner — and the clause-6 answer, measured at the predicate

- Task `20260825-dance-cure-candidate-2-swap`. This one artifact answers **both** the
  coordinator's `20260825T173045Z` **ruling 3** (the loop anatomy on the 4 panel games and the 2
  fixtures) and his `20260825T173324Z` **question** on clause 6, which asked for the answer folded
  in here rather than delivered separately.
- Written 2026-08-25 (stamp `20260825T175537Z` from `date -u`); worktree pin at writing
  `agent/claude_1@12198a8e6c7a176bcf9d198f827a6773e0dd65c0`.
- Evidence: `claude_1/cure2/results/loop-anatomy.json` (per-exchange rows and both arms' windows,
  from the wire and the referee trace) and `claude_1/cure2/results/swap-target-probe.json` (the
  `(chosen, T, L)` census over **all 66 exchanges of both corpora**). Drivers: `loop_anatomy.py`,
  `make_diagnostic_arm.py`, `swap_target_probe.py`.
- **No lock, no timer, no cooldown, no predicate change, no Arena action** — R-1a.

---

## 1. The clause-6 question, answered first because it changes a sentence of mine (not one of yours)

**The answer is none of (a), (b) or (c): the predicate's `T` and the wire's `chosen` are the same
value, and the transcript in `g1-interim-2026-08-25.md` §4.1 is mis-transcribed by me.** The wire
field order is `u<id>=<chosen>/<want>/r=<branch>/b=<n>`; the line I published as
`u0=TREE(2,3)/…/r=S` at OSC-006 t=3 has `chosen = TREE(2,2)` and `want = TREE(2,3)`. I printed the
second field in the position a reader takes for the first. The corrected line is:

```
t=3   u0=TREE(2,2)/TREE(2,3)/r=S   u2=TREE(2,3)/TREE(2,3)/r=X   sw=1   MOVE 0 2 3 ; MOVE 2 1 3
```

**Does this change the owner page's sentence?** No. `local_claude_1/cure2/owner-question-2026-08-25.md`
says the mover's goal must lie strictly beyond the partner's square, and that is **correct as
written and now measured**. What needs restating is not the clause but the *cause of the
reversal*, and that is §3 below.

### 1.1 What `target` is in `SWAP(M)`, with the code line

`hold_pass` builds, for every own unit whose **original** command parses as a `MOVE`:

```rust
let (_, target) = Self::move_command(&commands[*index])?;                       // cure2-swap-v5.rs:843
let landing = next_cell(&view.walkable, unit.cell, target, unit.stats.movement_speed);
```

So **`T` is the destination cell of that unit's own `MOVE` command**, parsed by `move_command`
(`:719`) out of the command `select_recording` emitted for it — not the `Target` enum, not the
pair's goal, not the partner's. Clause 6 compares that cell (`:941` `target==landing`, `:962`
`d_landing<d_here`).

That value and the wire's `chosen` coincide by construction, because **every candidate in this bot
whose command is a `MOVE x y` carries a `Target` whose cell is exactly `(x, y)`**. Every `Candidate` constructor in the file was read: `chop`/`fruit`/`idle-harvest` emit `MOVE plant.cell` with
`Target::Tree(plant.cell)`; `iron` emits `MOVE cell` with `Target::Cell(cell)`; `bank` emits
`MOVE cell` with `Target::Bank(cell)`; `forced_move`, the plant/pick conversions and the train
nudge emit `MOVE cell` with `Target::Cell(cell)`. **A chop goal is the tree's own cell, not an
adjacent one** — the troll stands on the plant and `CHOP`s (`:621`: `if plant.cell==unit.cell {
CHOP } else { MOVE unit.id plant.cell }`). The single cell-less case is `Target::Shack`, the
`bank_candidates` fallback (`:397`), where the wire prints `SHACK` and `T` is the shack cell
itself. `CHOP`/`HARVEST`/`DROP`/`PICK`/`MINE`/`PLANT`/`WAIT` are not `MOVE`s, so their units are
never movers; they can still be the *partner* whose command slot is rewritten.

Two structural consequences worth stating, because they close off the readings the question
offered: `select_recording` (`:694`) records **each unit's own** candidate's target
(`narrate_chosen.insert(ids[0], a_target)`, `insert(ids[1], b_target)`), so the wire never shows a
"pair goal"; and `compatible` (`:640`) forbids two own units holding the same target cell, so two
units can never both show `TREE(2,3)` — which is what should have told me the §4.1 line was
mis-transcribed.

### 1.2 The census the question asked for — all 66 exchanges, both corpora

Measured **at the predicate** by a print-only diagnostic arm (`arm-diagnostic.rs`: three
`eprintln!` lines over `arm-instrument.rs`, nothing else), gated so that "print-only" is proved
rather than asserted:

| gate | result |
|---|---|
| G-A print-only — diagnostic stdout byte-identical to the instrument arm's | **PASS** on 34 fixtures and 28 panel games |
| G-B row identity — each panel game reproduces its recorded `panel-swap-census.json` swap count | **PASS** on 28 games |
| G-C join — every `SWAPFIRE` matches an `S`/`X` pair on the same wire turn | **PASS** |

| quantity | count |
|---|---|
| standing-partner cases reached by the predicate | 761 |
| **exchanges granted** (46 panel + 20 fixture) | **66** |
| exchanges where `chosen == T` | **66 of 66** |
| exchanges where `chosen != T` | **0** (named list empty) |
| exchanges where **`chosen == L`** | **0** |
| exchanges where **`T == L`** | **0** |
| refused `so` (teammate on the goal, `T == L`) | 504 |
| refused `sn` (landing not adjacent) | 191 |
| refused `sf` (slot map) | **0** |
| reached clause 6's distance test and failed it (`d(L) ≥ d(c)`, charges nothing) | **0** |

So clause 6 never once fired on an exchange whose goal was the landing, and the `so` counter — 504
of the 761 cases here — is exactly the population where it did. Per-exchange rows
(`game, turn, mover, c, T, L, partner, chosen, want, d(L), d(c), outcome`) are in
`results/swap-target-probe.json`.

---

## 2. The anatomy — 12 exchanges on 6 games

Every exchange, with both units' chosen goals at `t-1`, `t`, `t+1`, read off the wire of the
instrument arm.

| game | t | mover `M` | `c` | `T` | `L` | partner `B` | `M` goal t−1 → t → t+1 | `B` goal t−1 → t → t+1 | goals traded? |
|---|---|---|---|---|---|---|---|---|---|
| OSC-006 | 3,5,7,9,11 | alternates u0/u2 | (1,3) | (2,2) | (2,3) | the other | `TREE(2,2)`→`TREE(2,2)`→**`TREE(2,3)`** | `TREE(2,3)`→`TREE(2,3)`→**`TREE(2,2)`** | **yes**, all 5 |
| m078:0 | 3,5,7,9,11 | alternates u0/u2 | (1,3) | (2,2) | (2,3) | the other | same as OSC-006 | same as OSC-006 | **yes**, all 5 |
| m090:0 | 3 | u2 | (3,5) | (1,5) | (2,5) | u0 | `BANK(1,5)`→`BANK(1,5)`→`BANK(1,5)` | `TREE(2,5)`→`TREE(2,5)`→`TREE(2,5)` | **no** — neither re-picked |
| m090:0 | 6,8,10,12 | alternates | (1,5) | (5,5) | (2,5) | the other | `TREE(5,5)`→`TREE(5,5)`→**`TREE(2,5)`** | `TREE(2,5)`→`TREE(2,5)`→**`TREE(5,5)`** | **yes**, all 4 |
| m090:1 | 12,15,18,21 | alternates | (6,5) | (2,5) | (5,5) | the other | `TREE(2,5)`→`TREE(2,5)`→**`TREE(5,5)`** | `TREE(5,5)`→`TREE(5,5)`→**`TREE(2,5)`** | **yes**, all 4 |
| OSC-007 | 8, 11 | alternates | (6,6) | (2,5) | (5,6) | the other | `TREE(2,5)`→`TREE(2,5)`→**`TREE(5,6)`** | `TREE(5,6)`→`TREE(5,6)`→`TREE(5,6)` / `NONE` | yes at t=8; at t=11 the partner goes `NONE` (the tree died) |
| m118:1 | 8, 11 | alternates | (6,6) | (2,5) | (5,6) | the other | `TREE(2,5)`→`TREE(2,5)`→**`TREE(5,6)`** | `TREE(5,6)`→`TREE(5,6)`→`TREE(5,6)` / `NONE` | yes at t=8; `NONE` at t=11 |

**Both units are choppers of the same two-tree cluster in 11 of the 12 exchanges** (the exception
is `m090:0` t=3, where the mover is carrying wood to the bank). In every looping game the mover's
cell `c`, its goal `T` and the partner's cell `L` are **identical at every exchange of the loop** —
the pair is not drifting, it is oscillating between two fixed cells with two fixed goals.

## 3. The mechanism in plain words

Take `m078:0`, which is the whole story in four turns:

```
t=2   u0@(1,3) TREE(2,2) r=W   (blocked)        u2@(2,3) TREE(2,3) r=N   CHOP 2
t=3   u0@(1,3) TREE(2,2) r=S   MOVE 0 2 3       u2@(2,3) TREE(2,3) r=X   MOVE 2 1 3     sw=1
t=4   u0@(2,3) TREE(2,3) r=N   CHOP 0           u2@(1,3) TREE(2,2) r=W   (blocked)
t=5   u0@(2,3) TREE(2,3) r=X   MOVE 0 1 3       u2@(1,3) TREE(2,2) r=S   MOVE 2 2 3     sw=1
```

The exchange puts `u0` on (2,3) — but `u0` never goes on to (2,2). The moment it stands on the
tree at (2,3) the selector gives it `TREE(2,3)` (chopping the tree under your feet outscores
walking to the next one), and hands `TREE(2,2)` to the troll now standing at (1,3). **The goals do
not travel with the trolls; they stay attached to the cells.** The pair swaps places, the selector
swaps the goals back to match, and the same standing-partner block re-forms in the opposite
direction — so the predicate fires again two turns later, entirely legally.

That is the precise sense in which "the planner re-picks the worker's goal past its old square" is
true: it is true of *both* units at once, and the re-pick is not churn — it is the pair selector
choosing the same optimal assignment for the new positions. **Theorem 1 is untouched** (C-6 = 0
over 48,000 panel turns; the reversal is always at least two turns later) and **Theorem 2 is
untouched** (a reversal does require a goal change, and there is one — measured, on both sides).
What the wire adds is *why* the goal change happens: the exchange causes it, deterministically,
whenever both units are choppers of the same cluster and the landing is itself a work square.

The loop therefore has a sharp signature the owner can rule on: **it happens exactly when the
landing `L` is a cell the partner is working (a tree it stands on), so that the mover, on arrival,
prefers the partner's job to its own.** In the 12 exchanges above, 11 land on a live tree cell.

## 4. One sentence per game: what a troll that kept its goal would have done

Read from the wire, not from a rerun — no counterfactual arm was built.

- **m078:0** — `u0` would have stepped (2,3)→(2,2) at t=4 and chopped `TREE(2,2)` while `u2`, back
  at (1,3) with `TREE(2,3)`, stepped straight back onto its tree: one exchange, both trolls
  working from t=4, no second exchange possible. Instead the tree at (2,3) is chopped on t=4, 6,
  8, 10 and 12 only — **five chops in ten turns against the rule-off arm's six in six** (rule-off
  fells it at t=8, the instrument arm at t=13) — and the game ends 21 against 26.
- **OSC-006** — the same map fragment as a frozen fixture, the same five exchanges, the same
  answer; the fixture's named cost is −5.
- **m090:0** — after the t=6 exchange `u2` would have carried on from (2,5) to `TREE(5,5)`, three
  more steps east, while `u0` chopped `TREE(2,5)` from (2,5)'s neighbour; instead they trade (2,5)
  and (1,5) four times over turns 6–12. Score **unchanged**, 26 both arms: the loop cost the pair
  turns it did not need.
- **m090:1** — `u2` would have continued west from (5,5) to `TREE(2,5)` (three steps) while `u0`
  kept chopping `TREE(5,5)` where it stood; instead the two trade (5,5) and (6,5) four times over
  turns 12–21, with `u0` bouncing east to (7,5) and back on the `R` branch each cycle. Score
  **unchanged**, 26 both arms.
- **m118:1** and **OSC-007** — identical shape one cell over: `u2` would have walked on west to
  `TREE(2,5)` while `u0` finished `TREE(5,6)`; instead they trade twice, and the second reversal
  ends only because `TREE(5,6)` dies. Score **unchanged**, 17 both arms.

**The loop's measured price on the panel is −5 points, on one game of 240.** It is not free — it
is turns spent trading places instead of chopping — but on three of the four panel games the score
is identical to the rule-off arm's, and the reason it looks worse than it costs is that it is
*visible*: five `S`/`X` pairs in ten turns is a striking thing to see on the wire.

## 5. What the owner is being asked to rule on, restated with these numbers

1. The loop exists, is legal under every clause, and is **caused by the exchange plus a positional
   goal reassignment**, not by churn or by a missing lock. It costs **5 points on 1 of 240 games**
   and 0 on the other three.
2. It is entirely absent when the landing is not a work square (`m090:0` t=3, the one exchange in
   the set with no trade and no re-pick).
3. The remedies that would remove it are all in the **planner** — a troll that keeps its goal, or a
   selector that does not re-assign on arrival (the Candidate 3 shape G-0 §4.4 guessed at). None of
   them is mine to build, and I have built none.
4. The tick-budget breach (`m078:0`, `m090:0`: 5 exchanges in 200 turns against a bar of ≤1 per 50)
   is the same phenomenon counted differently and travels with this ruling.

No Arena action is authorised, taken or proposed here.
