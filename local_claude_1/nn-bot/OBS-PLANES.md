# Full-game neural policy observation planes

Status: signed interface, 2026-08-29. This is the normative plane
layout for both `rust/src/rl_full.rs` and the independent dataset builder. It expands delineate's
published channel groups into exact per-channel meanings; the source deliberately leaves the
details open and says that a sensible choice is sufficient.

## Tensor, coordinates, and quantization

- Shape and dtype: C-contiguous `u8[104, 11, 22]`, flattened channel-major as
  `channel * 242 + y * 22 + x`.
- The viewing player is always "own". Absolute seat 0 is unchanged. Absolute seat 1 is rotated
  180 degrees: `(x, y) -> (w - 1 - x, h - 1 - y)`, and the two players are relabelled own/opponent.
  The padded tensor is not rotated as a 22 by 11 rectangle; real coordinates are rotated inside
  the actual `w` by `h` board and then placed at the tensor's top left.
- All padding cells (`x >= w` or `y >= h`) are zero in every plane. Scalar planes are broadcast
  only over valid board cells.
- For a non-negative value `v` with table scale `S`, use
  `q(v, S) = floor(255 * clamp(v, 0, S) / S + 0.5)`. This is Rust's non-negative `round`, not
  NumPy's ties-to-even `round`. Binary planes have `v` in `{0,1}` and `S = 1`.
- Resource order is always `PLUM, LEMON, APPLE, BANANA, IRON, WOOD`. Talent order is always
  `movement, carry, harvest, chop`.

## The 104 channels

| index | meaning | value and scale |
|---:|---|---|
| 0 | valid board cell | binary, `S=1` |
| 1 | grass cell | binary, `S=1`; a cell with a tree is still grass |
| 2 | water cell | binary, `S=1` |
| 3 | rock cell | binary, `S=1` |
| 4 | iron cell | binary, `S=1` |
| 5 | own shack cell | binary, `S=1` |
| 6 | opponent shack cell | binary, `S=1` |
| 7 | any living tree | binary, `S=1` |
| 8 | plum tree | binary, `S=1` |
| 9 | lemon tree | binary, `S=1` |
| 10 | apple tree | binary, `S=1` |
| 11 | banana tree | binary, `S=1` |
| 12 | tree size | `0..4`, `S=4` |
| 13 | tree health | `0..20`, `S=20` |
| 14 | fruit on tree | `0..3`, `S=3` |
| 15 | tree cooldown | `0..9`, `S=9` |
| 16 | own troll occupancy | binary at the troll cell, `S=1` |
| 17 | opponent troll occupancy | binary at the troll cell, `S=1` |
| 18 | own troll movement speed | at its cell, `S=3` |
| 19 | own troll carry capacity | at its cell, `S=4` |
| 20 | own troll harvest power | at its cell, `S=3` |
| 21 | own troll chop power | at its cell, `S=3` |
| 22 | own troll carried plum | at its cell, `S=4` |
| 23 | own troll carried lemon | at its cell, `S=4` |
| 24 | own troll carried apple | at its cell, `S=4` |
| 25 | own troll carried banana | at its cell, `S=4` |
| 26 | own troll carried iron | at its cell, `S=4` |
| 27 | own troll carried wood | at its cell, `S=4` |
| 28 | opponent troll movement speed | at its cell, `S=3` |
| 29 | opponent troll carry capacity | at its cell, `S=4` |
| 30 | opponent troll harvest power | at its cell, `S=3` |
| 31 | opponent troll chop power | at its cell, `S=3` |
| 32 | opponent troll carried plum | at its cell, `S=4` |
| 33 | opponent troll carried lemon | at its cell, `S=4` |
| 34 | opponent troll carried apple | at its cell, `S=4` |
| 35 | opponent troll carried banana | at its cell, `S=4` |
| 36 | opponent troll carried iron | at its cell, `S=4` |
| 37 | opponent troll carried wood | at its cell, `S=4` |
| 38 | walking distance from this cell to an own-shack door | clipped distance, `S=40` |
| 39 | walking distance from this cell to an opponent-shack door | clipped distance, `S=40` |
| 40 | cell is orthogonally adjacent to iron | binary, `S=1` |
| 41 | cell is orthogonally adjacent to water | binary, `S=1` |
| 42 | turn number | broadcast, `0..300`, `S=300` |
| 43 | own bank plum | broadcast, `S=64` |
| 44 | own bank lemon | broadcast, `S=64` |
| 45 | own bank apple | broadcast, `S=64` |
| 46 | own bank banana | broadcast, `S=64` |
| 47 | own bank iron | broadcast, `S=64` |
| 48 | own bank wood | broadcast, `S=128` |
| 49 | opponent bank plum | broadcast, `S=64` |
| 50 | opponent bank lemon | broadcast, `S=64` |
| 51 | opponent bank apple | broadcast, `S=64` |
| 52 | opponent bank banana | broadcast, `S=64` |
| 53 | opponent bank iron | broadcast, `S=64` |
| 54 | opponent bank wood | broadcast, `S=128` |
| 55 | own referee score | broadcast, fruit plus four times banked wood, `S=1024` |
| 56 | opponent referee score | broadcast, fruit plus four times banked wood, `S=1024` |
| 57 | own troll count | broadcast, `S=12` |
| 58 | opponent troll count | broadcast, `S=12` |
| 59 | current turn has a nonzero train target | broadcast binary, `S=1` |
| 60 | train-target movement speed | broadcast, `S=3` |
| 61 | train-target carry capacity | broadcast, `S=4` |
| 62 | train-target harvest power | broadcast, `S=2` |
| 63 | train-target chop power | broadcast, `S=3` |
| 64 | effective train cost: plum | broadcast, `S=32` |
| 65 | effective train cost: lemon | broadcast, `S=32` |
| 66 | effective train cost: apple | broadcast, `S=32` |
| 67 | effective train cost: iron | broadcast, `S=32` |
| 68 | current train deficit: plum | broadcast `max(cost-bank,0)`, `S=32` |
| 69 | current train deficit: lemon | broadcast `max(cost-bank,0)`, `S=32` |
| 70 | current train deficit: apple | broadcast `max(cost-bank,0)`, `S=32` |
| 71 | current train deficit: iron | broadcast `max(cost-bank,0)`, `S=32` |
| 72 | maximum own movement speed | broadcast, `S=3` |
| 73 | maximum own carry capacity | broadcast, `S=4` |
| 74 | maximum own harvest power | broadcast, `S=3` |
| 75 | maximum own chop power | broadcast, `S=3` |
| 76 | sum of own movement speeds | broadcast, `S=36` |
| 77 | sum of own carry capacities | broadcast, `S=48` |
| 78 | sum of own harvest powers | broadcast, `S=36` |
| 79 | sum of own chop powers | broadcast, `S=36` |
| 80 | maximum opponent movement speed | broadcast, `S=3` |
| 81 | maximum opponent carry capacity | broadcast, `S=4` |
| 82 | maximum opponent harvest power | broadcast, `S=3` |
| 83 | maximum opponent chop power | broadcast, `S=3` |
| 84 | sum of opponent movement speeds | broadcast, `S=36` |
| 85 | sum of opponent carry capacities | broadcast, `S=48` |
| 86 | sum of opponent harvest powers | broadcast, `S=36` |
| 87 | sum of opponent chop powers | broadcast, `S=36` |
| 88 | distance from this cell to the nearest living plum tree | clipped distance, `S=40` |
| 89 | distance from this cell to the nearest living lemon tree | clipped distance, `S=40` |
| 90 | distance from this cell to the nearest living apple tree | clipped distance, `S=40` |
| 91 | distance from this cell to the nearest living banana tree | clipped distance, `S=40` |
| 92 | distance from this cell to the nearest legal mining cell | clipped distance, `S=40` |
| 93 | own troll total carried items | at its cell, `S=4` |
| 94 | own troll free capacity | at its cell, `S=4` |
| 95 | opponent troll total carried items | at its cell, `S=4` |
| 96 | opponent troll free capacity | at its cell, `S=4` |
| 97 | plan action accepted for this turn | broadcast binary after any plan action, zero or nonzero, `S=1` |
| 98 | prior turn successfully trained its queued target | broadcast binary during the next plan phase, `S=1` |
| 99 | active troll | one-hot at the active own troll, `S=1`; all zero means plan phase |
| 100 | own troll is full | binary at its cell, `S=1` |
| 101 | own troll is full and carries only iron/wood | binary at its cell, `S=1` |
| 102 | opponent troll is full | binary at its cell, `S=1` |
| 103 | opponent troll is full and carries only iron/wood | binary at its cell, `S=1` |

## Exact compound semantics

### Terrain and distances

The map row is authoritative for planes 1-6. A tree does not replace grass. Planes 38-39 use BFS
over grass cells to the set of walkable cells orthogonally adjacent to the named shack. The named
shack cell itself has distance zero. Other non-grass cells and unreachable grass cells use the
clipped value 40. Planes 88-91 use current living tree cells as BFS targets regardless of ripeness;
planes 12-15 tell the policy whether the nearest tree is presently useful. Plane 92 targets every
walkable cell orthogonally adjacent to an iron cell. If a target set is empty, the distance is 40.

### Train target and plan index

Plan index is
`(((movement-1) * 4 + (carry-1)) * 3 + harvest) * 4 + chop`, with movement `1..3`, carry
`1..4`, harvest `0..2`, and chop `0..3`. Index 0 would be `(1,1,0,0)`, which is mechanically
useless; it is repurposed as **train nothing**. Index 0 zeroes planes 59-71 and 97.

For a nonzero plan, cost uses the current own troll count `n`:
`PLUM=n+movement^2`, `LEMON=n+carry^2`, `APPLE=n+harvest^2`, and
`IRON=n+chop^2`. On a map with no iron, effective iron cost and deficit are both zero because the
referee does not charge iron there. Cost and deficit ignore BANANA and WOOD, whose train costs are
zero.

At plan phase, plane 99 is all zero. Once the plan action is accepted, the plan is visible in
59-71 during every troll mini-step and plane 97 is one even when the accepted plan is zero. Plane 98 is a
one-turn latch: it is set only in the plan-phase observation immediately after the prior full turn
successfully created the queued specification, then cleared when the new plan action is accepted.

### Several trolls and staged commands

Own trolls are decided in ascending troll-id order. During a later troll's mini-step, an earlier
own troll is drawn at its staged end cell: for MOVE, the exact destination predicted by the engine
after the movement-speed limit; for another verb, its current cell. Its unchanged talents, cargo,
occupancy and full flags move together. Trees, inventories and cargo are not speculatively changed.
This makes earlier spatial reservations visible without inventing extra planes.

The action mask additionally rejects an action whose staged end cell duplicates an earlier own
troll's reserved end cell. If this conservative filter would empty the mask, MOVE to the active
troll's current cell remains the canonical WAIT fallback and the engine resolves the conflict.
Opponent trolls remain at their pre-turn positions because the two players' commands execute
simultaneously and cross-player occupancy is legal.

### Full-with-only-iron/wood

Planes 101 and 103 require both `total carried == carry capacity` and zero carried PLUM, LEMON,
APPLE and BANANA. A full troll carrying any fruit is therefore absent from the only-iron/wood
plane even if it also carries iron or wood.

## Required equality checks

1. Seat-0 observation rotated in Python must be byte-identical to the same point-symmetric state
   viewed as seat 1 after player relabelling.
2. The Rust environment and `tf_full_obs_from_state` must be byte-identical for every mini-step of
   1,000 sampled states, including staged earlier-troll commands.
3. The independent dataset plane builder must match `tf_full_obs_from_state` byte-for-byte on
   1,000 states; comparison uses raw `u8` bytes, not normalized floats.
