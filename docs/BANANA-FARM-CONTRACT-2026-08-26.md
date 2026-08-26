# The banana-farm contract — owner's outline consolidated (2026-08-26)

This page is the design input for the banana-farm candidate (board Track F, row F-2). It merges
the owner's outline of 2026-08-26 with the elements of the owner's earlier descriptions
(2026-08-02 → 08-17) that the outline had dropped, states the game rules the plan depends on
with their source lines, and records the three decisions the owner made on 2026-08-26. Plain
words; every internal term explained at first use. A design that departs from this page must say
where and why.

## 0. The three owner decisions of 2026-08-26

| question | decision | note |
|---|---|---|
| Where does the farm go? | **The ring around our hut** — the four orthogonally adjacent cells are *plots* (plant, grow, chop), the four diagonal cells are *mothers* (grow to size 4, harvest their fruit as seeds) | Replaces the approved Spec A's "any home-side cell at least as close to our hut as the enemy's" (2026-08-15). |
| How does planting stop? | **A one-way latch.** Once the farm is judged to feed the enemy more than us, planting stops for the rest of the game; there is no way back | As in the owner's 2026-08-07 and 08-15 versions ("fall back to chopping everything", "all transitions latched"). |
| May we plant during denial? | **Mothers only, by the second troll.** No other planting while denial runs | Amends the 2026-08-17 ruling "during denial our bot can't plant" for the reason in §3. |

## 1. The rules the plan depends on (from `docs/mechanics.md`, verified 2026-08-26)

- **Score = fruit in the shack + 4 × wood in the shack** (line 103). A banana banked is 1 point; wood is 4 points per unit.
- **A chopped tree yields wood equal to its size, max 4** (line 97). So **one banana seed → a size-4 tree → 16 points**, against 1 point for banking the seed.
- **Growth:** one size per cooldown; banana cooldown 6 turns, or 4 next to water (line 70–71: near water the cooldown is *reduced by* 2 for bananas, 7 for apples, 5 for plums/lemons — water helps bananas least). Seed → size 4: 24 turns dry, 16 wet. A size-4 tree then produces one fruit per cooldown, three stored; harvesting a full tree makes the next fruit come one tick later (line 77–78). **First seed from a mother: ~30 turns after planting it.**
- **Chopping:** a banana's health is 2 + size (6 hits at chop power 1 at size 4; an apple is 8 + 3·size = 20). Cheapest tree to farm for wood. Chop damage from both players counts; on death the wood goes to the chopper(s) (line 97) — **chopping an enemy tree gives us the wood**.
- **Harvesting:** the troll must stand on the tree; it takes min(harvest power, free capacity, fruits) per turn and cannot move that turn (lines 59–61).
- **Movement:** only grass is walkable; **a tree cell is walkable** (that is how harvesting works), so planting the ring blocks nothing. The shack cell is not walkable; trolls DROP from an orthogonally adjacent cell (lines 35–36). Two of *our* trolls cannot share a cell; enemy trolls can share ours (line 56).
- **Planting:** a troll plants on its own cell; a seed is one fruit of that type; planting is free of any other cost. The starting inventory in the shack holds fruit of all types (expected 24 in total, drawn at random and mirrored — line 21–23), so the first seeds are available at turn 1 via PICK from the shack.
- **Training:** the second troll costs, per talent, (number of existing trolls) + talent² of each fruit: plums for speed, lemons for capacity, apples for harvest power, iron for chop power; bananas and wood are never a training cost (line 89–91). A capacity-2 second troll = 5 lemons + 2 plums + 2 apples + 2 iron.
- **No fruit→wood conversion action exists.** "Late conversion" means planting the fruit and chopping the tree. It pays down to about ten turns before the end (a size-1 tree chopped = 4 points vs 1 banked).
- **Game length: 300 turns** (corrected 2026-08-26 20:25Z — the contract first said 200; claude_1's F-2 packet measured 301 keyframes in 266 of 290 replays and the champion's own endgame gate is `turn > 250`). The late wave therefore has far more room than "ten turns before the end" suggested.
- Capacity and wood: `docs/mechanics.md` line 61–62 ("Wood = 1 fruit then full") reads as *one unit of wood fills a troll whatever its capacity*; if so, capacity 2 helps only the seed/fruit trips, not the wood leg. The design packet may take either reading with its evidence.

## 2. The stages, as the owner ordered them

1. **Collect resources for the second troll.** Standing rule (owner, 2026-08-10, no exceptions): **no banana action of any kind before the second troll is trained.** "Preserve second-worker funding before denial work" (2026-08-02).
2. **Train the second troll.** A capacity-2 troll is preferred for the farm role (it carries a seed and a banana to bank in one trip). Our current bot trains at turn ~9; the leaders at 18–28 — speed is not the problem, talent choice may be.
3. **Select an aim for denial** — the tree species the enemy needs for its next troll (or the species it has fewest of), near the enemy's hut.
4. **Deny the aim** — chop those trees. Denial is income: the wood is ours at 4 points per unit.
5. **Denial ends** (one-way) on the first of: (a) the aim trees are all felled; (b) *reproduction* — the count of aim trees is **not falling across rounds**, where a round is "we felled every aim tree we could see" and the recount at the next round is compared with the previous; (c) the enemy trains a third troll (2026-08-15); (d) no aim tree is left in reach (2026-08-15). The owner's risk statement stands: denial may be left incomplete ("I'm ready to take this risk", 2026-08-15).
   **Mothers during denial (decision 3):** the second troll may plant mother bananas on the diagonal cells during denial, using seeds PICKed from the shack. Nothing else is planted. Reason: a mother needs ~30 turns before its first seed; if planting waits for denial to end, the farm feeds itself only after turn ~90.
6. **The banana wood farm** around the gate the bot chooses — "avoid long trips over the map" (the ring is by definition next to the hut, so trips are one or two steps):
   - **Plots** = the orthogonal cells next to the hut: plant a banana, let it grow, chop it for wood, replant. At most 8 plots in the ring (2026-08-04 cap: |ring| ≤ 8).
   - **Mothers** = the diagonal cells: grow to size 4, harvest seeds. **2 to 4 mothers** (2026-08-04: "mothers beyond 2 are surplus"). Place them on the side of the hut *away* from the enemy — "do not create fruit the opponent can harvest before us" (2026-08-02).
   - Water within the ring is a small bonus (banana cooldown 6 → 4), not a siting rule.
7. **Harvest the mothers, bank, replant.** Seeds from the mothers go to plots first; bananas beyond what the plots need are **banked** (1 point each, and a reserve for the late wave). The named defect of the first attempt (2026-08-04) — "harvested bananas are not being collected to the tent" — becomes a test.
8. **Stop planting (the latch, decision 2)** when the farm is more profitable for the enemy than for us — the owner's criterion: *it lowers the enemy's moves per wood unit*. Observable in-game: enemy chop hits on our ring cells per turn, against our own harvests and chops there; the threshold is calibrated from the leaders' games in the turn corpus (`data/processed/turns.jsonl.gz`), and once tripped it never resets.
9. **After the latch:** usual wood harvesting (chop the best trees in reach, ours and theirs), and the **late wave**: plant every held banana while a tree can still reach size ≥ 1 before the end (about ten turns), chop it; bank what cannot mature.

## 3. The worker rules that every earlier attempt broke (owner, 2026-08-02) — tests, not assumptions

- A troll carrying wood to the hut **keeps going until it drops it or loses it**.
- Trolls **never chase each other's occupied tree or cell**.
- Target choice has enough stickiness to **prevent A→B→A loops** (the swap loop of Candidate 2; the stranded troll of map 61).
- Two of our trolls never plan the same ring cell for the same turn.

## 4. What the evidence says (2026-08-26)

- Top-10 analysis (`codex_1/top10/field-comparison-2026-08-26.md`): the four leaders plant 3–6 bananas in turns 1–50 (we: 0.05), harvest 21–30 times on their own planted cells (we: 2.85), and bank ~61 wood a game to our 45 — about 15 trees of production. Our chops on enemy-planted trees (8.7 a game) already exceed theirs (0.5–2.5). Boundary: commands issued, not referee-accepted.
- The only ladder trial of a farm (2026-08-02, unconditional, no latch, no worker rules): 12.99 at rank 127/131 against the parent's 23.3 — 98 games, 49 losses, worst −348. Wins narrowly, loses catastrophically.
- The local bench overstated that farm by ~10 ladder points. **The ladder is the judge**; the bench is the ticket.

## 5. Acceptance shape (the design must pre-commit these before the first run)

- Containment: with the farm switched off the bot is byte-identical in play to the champion.
- Validity before value: no new blocked games, no no-progress turns, the worker rules of §3 hold on every panel game — measured, not argued.
- The latch fires at most once per game and never resets; denial ends by exactly one of (a)–(d).
- Value: one local panel (240 games + fixtures) as go/no-go for **one** ladder block (8 reads A-B-B-A against the champion with diagnostics); no promotion from the panel alone.
- Real-game readout from the diagnostic line: plants, mother harvests, latch turn, denial end reason, enemy chops on the ring.

## 6. Not decided here

The denial aim-selection rule (which species, how "near the enemy" is measured); the exact numbers for the latch threshold and the round criterion (K rounds); whether the capacity-2 troll is trained first or the farm starts with capacity 1; who builds. These belong to the design packet (Track F-2), which is chartered separately.

## Sources

Owner's outline of 2026-08-26 (this session); `coordination/tasks/20260802-banana-restoration-r2.md` (the nine-clause contract); `claude_1/banana-restoration-r2/invariant-spec-2026-08-04.md` (ring roles, caps); `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md` §1, §3; `docs/PROGRAMME-banana-farm-2026-08-15.md`; `coordination/tasks/20260815-banana-farm-two-specs.md`; `docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md` (geometry superseded by decision 1); `coordination/ITERATION.md` (08-17 rulings); `docs/mechanics.md`; `codex_1/top10/field-comparison-2026-08-26.md`.
