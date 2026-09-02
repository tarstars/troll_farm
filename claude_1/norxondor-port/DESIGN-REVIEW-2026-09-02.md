# Norxondor port — design review, round 1 (claude_1)

Date: 2026-09-02 · Task: `20260902-norxondor-port` · Reviewed: `codex_1/norxondor-port/DESIGN-2026-09-02.md`
at `e1300d02fbc79571d2f5e4fabde948435678aa1e` (pin verified reachable from `origin/agent/codex_1`).

Read against: `local_claude_1/reconstructions/norxondor_gorgonax/ALGORITHM.md` (§2, §3, §4, §5),
`readable/denial-off-champion.rs` (the functions the design borrows, by name), `rust/src/game/engine.rs`
(`step`, `apply_pick`, `apply_train`, `near_shack`), `claude_1/narrate6/narrate6.py` and
`claude_1/h2h-panel/bed_new_bot.py` (the v6 grammar the bed enforces), `docs/mechanics.md`.

## Verdict: ACCEPT WITH TWO EDITS — build after the edits are in the design note

The hybrid is specifiable: every layer of §3.1–3.9 has a boundary, every §5 gap a default, and the
borrowed champion functions exist under the names the design uses (`bank_candidates`,
`fruit_candidates`, `iron_candidates`, `predict_tree`, `chop_outcome`, `chop_candidates`, `select`,
`next_cell`, `collection_eta`). The TRAIN transaction is right against the engine. Two defaults are
holes in the card's sense — as written each one contradicts the measured behaviour it claims to
preserve — and each has an exact edit below with the number that falsifies the current text.
If codex_1 takes E1 and E2 (or an equivalent that passes the two named tests) no second review round
is needed from me; if either edit is disputed, that dispute is round 2 and the coordinator rules.

## E1 — the D-switch projection uses the wrong unit (review question 1) — HOLE

**What the design says (§3.2):** `eta = ceil(sum(champion collection_eta for each missing floor
resource) / min(2, funders))`, switch to Deforest when `turn + eta > 185`.

**What `collection_eta` computes** (`readable/denial-off-champion.rs:1150`): for `missing` units of one
item, `missing × (2·d + 2) + wait`, with `d` the door-to-source distance — **one item per round trip**.
It was written for the champion's opening, where the deficit is a handful of items. It ignores the
funder's carry capacity, its harvest power and the dwell on the tree.

**The arithmetic that falsifies it.** Floor costs are `n + v²` per talent (engine `training_cost`).

| state | floor bought next | items missing from an emptied shack | design's eta (d = 3, ÷2) | turn + eta | rule fires? | corpus |
|---|---|---|---|---|---|---|
| roster 3, turn 106 (third troll just bought) | 4th: `2/3/0/3`, n = 3 → 7 plum, 12 lemon, 3 apple, 12 iron = 34 | 34 × 8 / 2 = 136 | 242 | **D at once** | 4th troll bought in 113/186 games (61 %), median turn 132–138 |
| roster 4, turn 138 | 5th: `2/4/0/3`, n = 4 → 8 plum, 20 lemon, 4 apple, 13 iron = 45 | 45 × 8 / 2 = 180 | 318 | D at once | 5th troll in 24/184 (13 %) — D here is the majority outcome |

So the default as written ends the ladder at three trolls in essentially every game, while the
reconstruction has four or more trolls at the end in 52 % of games (§4: 41 % + 11 %) and the design's
own stated intent is to "preserve the measured final training frontier". The champion's spec spends
the shack down at each purchase (componentwise maximum), so "emptied shack" is the normal state after
a TRAIN, not a corner.

**Exact edit.** Per missing resource `r`, with the best eligible funder's carry `c` and harvest power
`h` (chop power for iron; mining yields `min(chop, free)` per turn):

```text
trips_r = ceil(missing_r / c)
dwell_r = ceil(min(c, missing_r) / h)          # turns on the tree or beside the iron per trip
eta_r   = trips_r × (2·d_r + dwell_r) + wait_r  # d_r, wait_r as collection_eta already computes them
eta     = ceil(sum_r eta_r / min(2, eligible funders))
```

The same two rows under this edit, with the funder `2/3/1/2` (c = 3, h = 1; iron with chop 2):
roster 3 at turn 106 → lemons 4 × 9 = 36, plums 3 × 9 = 27, apples 1 × 9 = 9, iron 4 × 8 = 32,
sum 104 / 2 = 52 → 158 ≤ 185, **stays Produce**; roster 4 at turn 138 → 7 × 9 + 3 × 9 + 2 × 9 + 5 × 8
= 148 / 2 = 74 → 212 > 185, **Deforest** — the fourth troll is kept, the fifth is usually not, which
is the corpus frontier (4th median 132–138, 5th in 13 %).

**Two unit tests to add to gate 6:** (i) roster 3, empty shack, turn 106, every source at door
distance 3 → mode stays Produce; (ii) roster 4, empty shack, turn 138, same distances → Deforest.

**Two lines to state while editing:** the sum omits iron on maps without iron terrain (the engine
pays slots `[0,1,2,3,5]` when `game.iron` is empty, `apply_train`), otherwise the sentinel 10,000
switches every iron-free map to Deforest on turn 1; and a resource with no source anywhere (the
sentinel) does switch the mode — say so, it is the design's "hopeless" case and the corpus's 1 % of
one-troll games.

## E2 — priority step 3 "carrying anything: bank" strands the funding coalition — HOLE

**What the design says (§3.4):** `2. else if load is full: bank · 3. else if carrying anything:
bank`, with the reason "matches the 91 % full-load tendency without stranding partial loads".

**Why it is the opposite of that.** A troll gains `min(harvestPower, freeCapacity, fruitsOnTree)` per
turn (`docs/mechanics.md:61`), and MINE gives `min(chopPower, freeCapacity)`. Under step 3 a troll
whose carry exceeds its harvest power — every troll from the second onward (`2/2/2/2`, `2/3/1/2`)
— harvests once, is "carrying something", and walks home. A carry-3 harvest-1 funder makes three
round trips per load instead of one; the coalition's throughput drops by the carry factor at exactly
the stage where E1's frontier depends on it. The corpus's 91 % full-load drops (§3.6) and "stay 2–3
turns for a full load" (§3.4) are what this step prevents, not what it reproduces. The champion's own
code does not do this: `main_candidates` banks a partial load only when the unit is already adjacent
to the shack or when no work candidate remains (`chops.is_empty() && carried > 0`), and
`fruit_candidates` scores the tree the unit stands on at `+900`, so continuing a harvest wins on its
own.

**Exact edit.** Delete step 3. In the Produce branch let the champion's HARVEST / MINE candidates run
for a unit with a partial load (the standing tree or iron wins by score); bank a partial load only
(a) when the gated list has no productive candidate — the champion's shape — or (b) when the unit is
adjacent to the shack (the champion's rule), or (c) on the projected TRAIN turn if the carried kind
completes the floor (optional, one line). Step 2 (full → bank) stays. In Deforest the same applies to
the banana job's wood (one wood fills any troll: `mechanics.md:61`).

**Unit test to add:** a `2/3/1/2` troll on a tree with 3 fruit and 1 carried harvests again rather
than banking.

## Q2 — one orchard job + one banana job (review question 2): no hole, three things to state

1. **The banana loop's fuel is the starting stock only.** HARVEST is closed in Deforest and banana is
   excluded from Produce funding, so the conversion count per game is bounded by the seat's starting
   bananas (the shack starts with ~24 fruit of the four kinds, drawn and mirrored:
   `docs/BANANA-FARM-CONTRACT-2026-08-26.md:26` — about six bananas). That is consistent with the
   corpus: 1,116 runs / 184 games = 6.1 conversions a game, and the real bot's own banana harvests
   (7 % of 90 fruit ≈ 6) mostly went unconverted (bananas in the shack fall only from 7.5 to 4.2,
   §2.5). Say the bound explicitly as the default; do not add banana harvesting to fix it.
2. **Carried deficit fruit versus the orchard job (admission rule 3):** a harvested lemon that is a
   next-floor deficit can be claimed by a lemon job. State the tie-break: the ladder wins — a kind in
   deficit for the next floor is banked, never planted, while Produce lasts. One line; otherwise the
   orchard taxes the coalition E1 relies on.
3. **The orchard closes at the switch; the corpus keeps planting plums and lemons to turn 279**
   (250–299: P 309 / L 266 / A 152 / B 128, §3.5). The design plants at most 7 orchard trees plus
   ~6 bananas ≈ 13 a game against the corpus's 29; a lemon planted at turn 200 is size 4 by ~220
   (age at chop median 18) = 4 wood = 16 points for one fruit point. Not a hole — it is a named
   default — but it is the first place I would look in the loss read if rung 1 reads the port
   below the champion. Put it on the refinement-loop list now.

The bound itself holds: PICK needs a reserved free cell, one global job, no job on a TRAIN turn,
the champion's `select` already refuses a PICK the stock cannot pay, and an invalidated job releases
its unit without re-picking. That is the July loop closed at its source.

## Q3 — v6 diagnostics (review question 3): no nonzero counter is required

What the bed enforces (`bed_new_bot.telemetry_errors` → `narrate6.decode`): exactly one `MSG` token
per turn, first in the command list, under 2,000 characters; `MSG [banner] NARRATE v6 t=<turn>`, then
one token per own unit `u<id>=<chosen>/<available>/r=<PLRWN>/b=<digits>/k=<012>` with `<chosen>` a
target (`NONE | SHACK | BANK(x,y) | CELL(x,y) | TREE(x,y)`) and `<available>` a target or `ABSENT`,
then all 32 per-turn fields present once each:
`pz sp wc sw so sn sf kp kq kl kr rd rg ri rx rf rt ro nl nl_producer nl_door nl_admissibility
nl_other ka kc xc xw xn xp xg xd xj`. Unit tokens must precede meta tokens; a unit twice or a meta
field twice is a decode error.

Consequences for the port:

- **All-zero counters are valid.** The four census equations (`kp = kq + kl`,
  `rd + rg + ri + rx + xc = kr`, `rf + rt + ro = rg`, the four `nl_*` summing to `nl`) hold at zero.
  `b=` must be exactly 0 (nonzero is a decode error by construction). `k=0` for every unit (the port
  has no kept goals). Neither the bed nor the h2h panel reads a counter's value; only decodability.
- **The fields that must carry truth:** `t=` the turn; one token per own unit, each once, in id order;
  `<chosen>` the target of the command actually emitted after the champion's selector and resolver
  (the `Target` the candidate already carries); `r=` from the resolver: `N` when the unit emits no
  MOVE, `P` for a primary-path MOVE, `L`/`R` if the champion's detour code is copied, `W` for a
  forced WAIT. `<available>` may be `ABSENT` throughout.
- **One banner, inside the same MSG.** The champion of record pushes its announcement as a separate
  `MSG` on turn 1 (`commands()`, `self.announced`); the v6 arm merges it as the single token before
  `NARRATE`. A second `MSG` token on any turn fails the bed. The design's "the first line may include
  the banner exactly as the v6 champion does" is the right reading; the readable file must emit the
  line itself (the card's note of record).

## Verified as stated

- **TRAIN transaction:** `engine.rs::step` applies MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE in
  that order; `apply_train` refuses when any unit stands on the shack and when the pre-turn inventory
  cannot pay. So both parts of the design's default are necessary, not optional: PICK must be
  suppressed on a TRAIN turn (PICK lands first and can spend the bill) and the shack-standing unit must
  move first (MOVE lands before TRAIN). DROP lands after TRAIN, so "affordable from the pre-turn
  inventory" is the exact test. `near_shack` is Manhattan ≤ 1, so "PICK only while adjacent to the
  shack" is the engine's own condition.
- **Ladder:** floors, caps, roster-five stop, no TRAIN in D — as §3.1; iron waived on iron-free maps
  matches `apply_train`.
- **Banana chop:** on death wood equals tree size (`mechanics.md:97`), so a size-1 banana is one wood
  = 4 points; growth during a two-turn chop is the champion's `chop_outcome`'s business, as the
  design says.
- **Determinism:** Rust `HashMap` iteration is per-process random; the design's "no hash iteration"
  gate is the right one.
- **Size and time:** 47,668-byte baseline + ≤ 22,000 budget, under 70,000 UTF-16 units; p99 < 10 ms
  against a 50 ms limit — plausible for one ETA pass and one cell scan per turn.

## Requested from codex_1 before the build

E1 and E2 written into `DESIGN-2026-09-02.md` (a dated "review edits" section is enough), the three
Q2 statements added as one line each, the four unit tests named above on the gate-6 list. Then build
exactly that version. I will reproduce the artifact byte-for-byte and run rung 1 on the pinned panel.
