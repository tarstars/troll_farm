# RULES — the game, completely, as physics

This document describes what the referee does. It contains no advice, no strategy and no
architecture: every sentence here is a law of the world you are playing in. If a sentence looks
like a hint about how to build a bot, read it again — it is a fact about the referee.

Primary source: the game's referee (the Java program that runs every match on the platform),
re-audited against real match recordings. Where a rule was recovered from recordings rather than
read from the referee, the sentence says so.

---

## 1. The shape of a match

Two players. Each starts with **one shack** and **one troll**. A troll is a worker you command;
a shack is your home, your bank and your spawn point.

The match runs for **300 turns**, unless it ends earlier under §11. On each turn both players
print their commands, and the referee applies them all together (§10).

**You score points.** At the end, your score is the contents of your shack:

    score = plums + lemons + apples + bananas + 4 x wood

Fruit is worth **1 point each**, wood is worth **4 points each**. Iron is worth **nothing** —
it is only a currency (§8). Anything a troll is still *carrying* when the match ends scores
zero. Only what is in the shack counts.

Higher score wins. Equal scores is a draw. You also lose immediately if you print an
unrecognised command or answer too slowly (§12).

---

## 2. The map

- A rectangle, **height** cells tall and **width = 2 x height** cells wide.
  **height is drawn uniformly from 8..11**, so the map is 16x8, 18x9, 20x10 or 22x11.
- The map is **point-symmetric**: rotate it 180 degrees about the centre and it maps onto
  itself with the two players exchanged. Your half is `x < width/2`; your shack is in it.
- Cell types, and the character each is printed as:

  | char | cell    | walkable | notes |
  |------|---------|----------|-------|
  | `.`  | GRASS   | yes      | the only walkable cell |
  | `~`  | WATER   | no       | speeds up trees planted orthogonally next to it (§6) |
  | `#`  | ROCK    | no       | blocks nothing but movement |
  | `+`  | IRON    | no       | mined from an orthogonally adjacent cell (§8) |
  | `0`  | your shack     | **no** | you cannot stand on it |
  | `1`  | opponent shack | **no** | |

- **Only GRASS is walkable.** A shack cell is not walkable, so a troll can never stand on its
  own shack; it banks from an orthogonally adjacent cell (§5).
- Trees stand on GRASS cells and the cell stays GRASS. You stand **on** a tree's cell to work it.

---

## 3. Trolls

A troll has an **id** (an integer, never reused), an owner, a position, and four fixed talents
that never change once it exists:

- **movementSpeed** — how many cells it may move in one turn;
- **carryCapacity** — how many items in total it may hold;
- **harvestPower** — how many fruits it may take from a tree in one turn;
- **chopPower** — how much damage it deals to a tree in one turn, and how much iron it mines.

Your starting troll is **(speed 1, carry 1, harvest 1, chop 1)**. Both players start identical.
New trolls are bought with TRAIN (§8) and you choose their talents when you buy them.

A troll carries items in six slots: plum, lemon, apple, banana, iron, wood. The **total** of all
six is what carryCapacity limits.

**A troll spawns on its own shack cell** even though that cell is not walkable. Distances are
measured from where it stands, so this works — but a program that refuses to compute from a
non-walkable cell will see "nowhere to go" on turn 1 and freeze there for the whole match.

---

## 4. Movement

`MOVE id x y` asks troll `id` to move toward cell `(x, y)`.

- Distance is **breadth-first search over GRASS cells**, four-neighbour (up/down/left/right).
  Diagonals do not exist. **Other trolls do not block distances** — pathfinding ignores them.
- If `(x, y)` is reachable within `movementSpeed` steps, the troll ends the turn exactly there.
- Otherwise it moves to the cell, among all cells reachable within `movementSpeed`, that has the
  smallest BFS distance to the target. With speed 1 this is one step along a shortest path.
- If `(x, y)` is not reachable at all (it is water, rock, or a shack, or walled off), the troll
  routes toward the reachable cell with the smallest **Manhattan** distance to the target. This
  is how a troll parks next to an unwalkable shack: aim at the shack cell itself.
- **The referee breaks equal-best ties randomly.** Two shortest paths of the same length are not
  distinguishable to you; do not build anything that depends on which one is taken.

### Collisions

Collisions are resolved **within each player separately**.

- Two of **your** trolls may not end the turn on the same cell. The contested cell goes to the
  **higher id**.
- **Circular swaps are legal**: if A steps onto B's cell while B steps onto A's, both moves
  happen. Cycles of any length resolve.
- If a troll cannot move it stays where it is; this is a non-fatal error, the turn continues.
- **An opponent troll never blocks you.** Your troll and an opponent troll may share a cell.
  There is at most one troll per team per cell, so at most two trolls on a cell.

---

## 5. Banking, and taking back out

`DROP id` — if troll `id` is **orthogonally adjacent to its own shack** (Manhattan distance
exactly 1, or 0, which cannot happen after turn 1), everything it carries moves into the shack
inventory. All six slots at once. Not adjacent: nothing happens.

`PICK id TYPE` — the reverse: a troll adjacent to its own shack with free capacity takes **one**
item of `TYPE` out of the shack inventory into its carry, if the shack has one. `TYPE` is one of
`PLUM LEMON APPLE BANANA IRON WOOD`.

Items in the shack are your score (§1) and your currency (§8) at the same time. Taking one out
lowers your score until it comes back.

---

## 6. Trees

A tree has a **type** (`PLUM`, `LEMON`, `APPLE`, `BANANA`), a **size** 0..4, a **health**, a
**fruit count** 0..3, and a **cooldown**.

**Growth.** At the end of every turn each tree's cooldown drops by one. When a living tree's
cooldown reaches 0:

- if `size < 4`: it **grows one size** — and its health rises by its type's slope (see below),
  which means accumulated chop damage is preserved, not healed;
- else if `fruits < 3`: it **produces one fruit**;
- else nothing (a full grown tree with 3 fruits idles at cooldown 0 and produces the moment a
  fruit is taken).

Then the cooldown resets to its base value:

| type   | base cooldown | cooldown next to water | health = base + slope x size | max health (size 4) |
|--------|---------------|------------------------|------------------------------|---------------------|
| PLUM   | 8             | 3                      | 4 + 2 x size                 | 12 |
| LEMON  | 8             | 3                      | 4 + 2 x size                 | 12 |
| APPLE  | 9             | 2                      | 8 + 3 x size                 | 20 |
| BANANA | 6             | 4                      | 2 + 1 x size                 | 6  |

"Next to water" means orthogonally adjacent to a WATER cell. The health formula was recovered
from match recordings (ten independent observations, exact fit) and confirmed against the
referee's constants.

**At the start of the match** the trees on the map are randomly "aged" — each has been ticked a
random number of times between 1 and `base_cooldown x 7` — so they begin at assorted sizes,
fruit counts and cooldowns.

---

## 7. Working a tree

`HARVEST id` — the troll must be standing **on** the tree's cell, the tree must have at least
one fruit, and the troll must have free capacity and harvestPower > 0.

Resolution runs in rounds i = 1, 2, 3 over all trolls standing on that cell — **both players'
trolls together**. In round i, every troll with `harvestPower >= i` and free capacity gains one
fruit of the tree's type, and *then* the tree's fruit count is decremented, but never below 0.

The consequence is the **last-fruit duplication**: a tree with one fruit and two trolls on it
(one of each player, at most) gives a fruit to *both*. At most one extra fruit can be created
this way per tree per turn.

A troll cannot MOVE and HARVEST in the same turn — one command per troll per turn (§10).

`CHOP id` — the troll must be standing **on** the tree's cell and have chopPower > 0. Every
chopper on the cell subtracts its chopPower from the tree's health; **both players' damage is
applied before death is checked**, so a tree can be felled by the two of you jointly.

If health reaches 0 the tree **dies and is removed**, and its **size** in wood is handed out to
the choppers on its cell, one at a time, cycling over them while any has free capacity. Because
a chopper is offered wood before the remaining count is checked again, the **last wood can
duplicate** the same way the last fruit can.

Wood is worth 4 points in the shack (§1). A size-4 apple therefore pays 16 points to fell, and
costs 20 health of chopping to do it; a size-4 banana pays 16 for 6 health. **A dead tree never
comes back** — the cell is empty until somebody plants there.

`PLANT id TYPE` — the troll plants one carried fruit of `TYPE` as a new tree on **the cell it is
standing on**. The cell must be walkable and must not already have a tree. The seed is consumed.
The new tree starts at **size 0, cooldown 0, health = its type's base**, and it **ticks on the
turn it is created**, so it grows to size 1 immediately.

If two trolls PLANT the **same** type on the same cell in the same turn, one tree appears and
**both** seeds are spent. If they plant **different** types on the same cell, **nothing is
planted and no seed is spent**.

---

## 8. Buying trolls, and iron

`TRAIN ms cc hp chop` buys one new troll with those talents. You do not name it; the referee
assigns the next free id.

With `n` trolls of yours already alive, the cost is:

    PLUM   = n + ms   x ms
    LEMON  = n + cc   x cc
    APPLE  = n + hp   x hp
    IRON   = n + chop x chop
    (BANANA and WOOD cost nothing)

All four must be affordable **from the shack inventory** simultaneously. Note that the cost
rises with the size of your workforce: the same troll costs more the more you already have.
If the map has no iron cells at all, the iron part of the cost is waived.

Two further conditions, both checked **at the moment the command is applied**, not when you
print it:

- you must still be able to afford it after everything earlier in the turn order (§10) has
  happened — in particular after PICK, which spends shack inventory, and before DROP, which
  refills it. **A DROP in the same turn does not pay for a TRAIN in that turn.**
- **your shack cell must be empty of trolls** — a troll standing on it (only possible on turn 1,
  before it has left) blocks training.

The new troll appears **on your shack cell** and may act from the next turn.

TRAIN is the one command that does not name a troll id, so **more than one TRAIN in a turn is
possible**; they are applied one after another, and each re-checks affordability and the empty
shack against the state the previous one left. In practice the second is rarely affordable.

`MINE id` — a troll with chopPower > 0 and free capacity, standing on a GRASS cell
**orthogonally adjacent to an IRON cell**, gains `min(chopPower, free capacity)` iron. Iron is
never worth points; it exists to be spent on chop talent.

---

## 9. The command language

Each turn, print any number of commands on one line, separated by `;`. Whitespace-separated
arguments.

    MOVE id x y          move troll id toward (x, y)
    HARVEST id           take fruit from the tree under troll id
    CHOP id              damage the tree under troll id
    PLANT id TYPE        plant a carried seed of TYPE under troll id
    PICK id TYPE         take one TYPE out of the shack (troll must be next to it)
    DROP id              bank everything troll id carries (troll must be next to the shack)
    TRAIN ms cc hp chop  buy a troll
    MINE id              mine iron adjacent to troll id
    WAIT                 do nothing
    MSG text             show text in the replay; costs nothing, does nothing

**One command per troll per turn.** The referee keeps the **first** command that names a given
troll id and ignores the rest. `MSG` may not contain a `;` — the separator wins.

Commands naming a troll you do not own, or a troll id that does not exist, are non-fatal errors:
that command is skipped and the turn goes on. An **unrecognised verb is fatal** — you lose.

---

## 10. The turn

Both players print. Then the referee applies every command from both players in **this fixed
order of verbs**, not in the order you printed them:

    1 MOVE      2 HARVEST   3 PLANT    4 CHOP
    5 PICK      6 TRAIN     7 DROP     8 MINE

Then every tree ticks (§6), and both scores are recomputed.

Read that order carefully; several rules of the world follow from it alone:

- **HARVEST happens after MOVE**, so a troll cannot move onto a tree and harvest it in the same
  turn — but it does not need to: it arrives, and harvests next turn.
- **PLANT happens before CHOP**, so a seed planted on a cell this turn cannot be chopped this
  turn.
- **PICK happens before TRAIN, and DROP after it.** Money you bank this turn is not available
  to this turn's TRAIN; money you PICK out of the shack this turn is gone before TRAIN checks.
- **MINE happens last**, after DROP: iron mined this turn is on the troll, not in the shack.

---

## 11. How a match ends

A match ends at the end of turn **300**. It also ends early, and this matters more than it
sounds, under the referee's stall rule:

- **While at least one tree is alive on the map**, a countdown is held open. It is set each turn
  to the largest, over all trolls currently standing on a tree, of
  `(that troll's BFS distance home) / (its speed) + 6`. The match does not end.
- **Once no tree is alive anywhere**, that countdown starts running down, one per turn.
  The match ends when it reaches zero.
- A player is **stuck** when it holds no fruit and no wood anywhere — none in the shack, none
  carried by any troll (carried *iron* does not count as unstuck). With no trees left, the match
  also ends immediately if **both** players are stuck, or if a **stuck player is behind**.

So: felling the last tree on the map starts a clock, and a clock that expires ends the match at
the score it has then. Games in real play end at every length from about 80 turns to the full
300.

---

## 12. Time and legality

- **First turn: 1000 ms.** Every other turn: **50 ms.**
- The referee tolerates three overruns of at most 50 ms each; a single overrun of more than
  50 ms over the limit, or a fourth small one, loses the match.
- An unrecognised command loses the match. Every other error (a troll that is not yours, a
  DROP too far from the shack, a TRAIN you cannot afford, a PLANT on an occupied cell) is
  non-fatal: the action simply does not happen and the match continues.

---

## 13. What you are given each turn

**Once, at the start:**

    width height
    height lines of width characters, from the table in §2

**Every turn, in this order:**

    your inventory:      plum lemon apple banana iron wood
    opponent inventory:  plum lemon apple banana iron wood
    treeCount
    treeCount lines:     TYPE x y size health fruits cooldown
    trollCount
    trollCount lines:    id player x y movementSpeed carryCapacity harvestPower chopPower
                         carryPlum carryLemon carryApple carryBanana carryIron carryWood

`player` is **0 if the troll is yours, 1 if it is the opponent's** — it is relative to you, not
an absolute seat number. Every other coordinate is absolute.

You see the whole board: every tree with its exact health, fruit count and cooldown, every
troll of both players with its exact talents and carry, and both inventories. There is no
hidden information in this game.
