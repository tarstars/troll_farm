# V615 own-worker chop/payout pooling feasibility: impossible by referee invariant -- 2026-09-05

## Verdict

Two workers owned by the same player cannot pool chop damage or free carrying capacity on one
tree. The authoritative Java referee preserves unique same-player cell occupancy after every
movement phase, while chop damage and death-payout recipients are grouped by the tree's exact
cell. Consequently two own workers can never enter one chop group. The proposed V615--V617
rendezvous branches have an empty legal action set on every map and turn, so no candidate,
development panel, or platform publication was created.

Sequential cooperation does not recover the idea. A first worker can pre-damage a tree and leave,
but the Java `ChopTask` distributes wood only among the tasks in the fatal turn's current cell
group. The earlier worker contributes damage without contributing carrying capacity when the tree
dies. Circular swaps likewise preserve one own worker per cell rather than creating overlap.

Cross-player overlap is legal because movement collisions are resolved separately for each
player. That physically distinct “join an opponent's fatal chop” branch is not new evidence:
V422 already changed the exact observed anti-griefing case, then lost one adaptive-continuation
win and 268 total margin across 12 opponents. The current audit does not justify reopening it.

## Rule proof

The proof is the conjunction of four referee invariants.

1. Java `MoveTask.apply` first groups moves by player. For each group it marks every current unit
   cell occupied and admits a destination only when that destination is not occupied. Multiple
   movers selecting the same empty destination resolve to one winner; circular movement rotates
   occupants. Every branch therefore preserves an injective mapping from one player's units to
   cells.
2. Training cannot introduce a duplicate: a new worker appears at its shack only when that shack
   is unoccupied. Initial referee states also contain unique own-unit cells.
3. Java `ChopTask.apply` groups all current chop tasks by `getCell()`, applies the chop power of
   tasks in that group, and, on death, loops over only those same tasks when assigning wood to
   units with free capacity.
4. The Rust continued-referee engine mirrors both rules: `apply_resolved_moves` builds one
   occupied set inside a `for player in 0..2` loop and requires `!occupied.contains(destination)`;
   `apply_chop_on_existing_cells` groups unit IDs by current cell and awards wood only through
   the fatal cell's `choppers` vector.

By induction, no legal sequence can place two units of one player on the same cell. Since a plant
occupies one cell and `CHOP` operates only underfoot, no legal turn can contain two own choppers
for that plant. Their nominal combined carry three and chop three are therefore unavailable as a
single tree-felling resource.

V468 independently enforces the same constraint at planning time. Its pair compatibility maps
bank, cell, and tree targets to cells and accepts two cell-valued targets only when `a != b`.
Removing that planner guard would create blocked movement, not cooperative chopping.

## Reproducible source audit

A read-only assertion audit checked the exact source snapshots for these structures and passed
all six groups:

- Java movement: grouping by player, initial occupied marking, and the `!occupied` admission;
- Java chop: grouping by cell, per-task damage, and per-task free-capacity payout;
- Java task grouping: cell-keyed accumulation without a player partition;
- Rust movement: per-player loop, occupied set, and unoccupied-destination admission;
- Rust chop: cell-keyed chopper vector, damage loop, and payout loop over that vector;
- V468 assignment: cell projection and unequal-cell pair compatibility.

| authoritative source | SHA-256 |
|---|---|
| Java `MoveTask.java` | `7d4448f5833a1f758e716110669764d792a918f8e1994f7d05d73ba66f6e4745` |
| Java `ChopTask.java` | `5e3fed658a3aff9714f2176fc37cd3e494ec6e8c451354eeb95c3c084149aaab` |
| Java `Task.java` | `98da98706598e3a5424c6303f4fe25841acb5b60646742dc0eb85aae333d5b9f` |
| Rust `a2_referee_parity.rs` | `518c222881ac23f8548cc13c858bacc93577ea920ecfbdbf0fd0e588cad1bf83` |
| exact V468 development module | `f3e6442270fa289247167e017be89b31563a7543312216e04a508b3d7f989b59` |

No probabilistic game sample can weaken or strengthen this result: the action is prohibited by
the transition function for the entire state space. Building inactive candidates or spending the
192-game selector would provide no additional evidence.

## Consequence

The next iteration returns to a live, unclosed transaction defect. V600--V602 safely replaced
selected post-turn-100 producer wood actions with seed pickups, but V468 did not recognize the
injected cargo as an active plant job: of 207 producer picks, only 104 were followed by `PLANT`,
while 72 were followed by `DROP`. V601 still gained 2.71 wood despite this failure. A persistent
nearby seed-to-plant transaction can test the intended second crop lane while preserving inherited
`PICK`, `PLANT`, `HARVEST`, and `DROP` actions whenever no injected job is live. It is materially
different from own-worker pooling and directly repairs the measured missing transition.

## Integrity

- complete repository suite: 282 passed in 71.16 seconds;
- no gameplay or test source was changed;
- no candidate, runner, smoke, frozen panel, fresh panel, duel, packaging audit, production
  change, or platform publication ran;
- production remained `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372` and
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- the neighboring checkout was read only at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, retaining
  its pre-existing modified `data/processed/stats.json` and untracked
  `data/panels/top5-ab-20260902T115338Z.json`.
