# Same-turn training is corrected in the experimental controller

The independently reproduced MOVE-before-TRAIN rule in `TRAIN-EGRESS-FINDING-2026-09-05.md`
is now implemented in `next_bot/`, under the separate `TRAIN-EGRESS-DESIGN-2026-09-05.md`.
This is not part of the V439 restoration submission and does not justify publishing the
experimental controller by itself.

Claude supplied a bounded read-only patch proposal (17 turns, reported USD 1.8001425, no
permission denials). The primary agent applied and reviewed it, then strengthened malformed/
unknown/non-owned/duplicate MOVE handling, out-of-range destinations and own-unit endpoint
collisions. Egress priority is active only when a hire is actually intended. The new first-hire
reservation fixture covers both worker ceilings; an initially over-strict Claude test was
corrected because banana PICK is legitimate when no third hire is allowed.

An affordable hire now reserves its bill, arranges legal shack egress, resolves all own moves,
then emits TRAIN only if the shack will be clear. A move into an initially empty shack suppresses
the purchase. Current enemy shack occupancy blocks the intent conservatively; no enemy move is
predicted. An enemy-held exit is conservatively excluded even though ordinary cross-player MOVE
collisions are not enforced by the referee. Cancelled intents do not spend inventory or invent
workers, but can conservatively withhold a seed PICK/new goal for that turn.

Verification:

- All 36 Rust behavior fixtures pass under eight configurations (serial/parallel capital,
  two/four workers, denial disabled/enabled), including every old fixture and nine new cases.
- The complete pre-publication project suite passes: 456 tests in 165.50 seconds.
  The final suite including eleven publication guards passes 467 tests in 155.57 seconds.
- The frozen corrected two-worker/denial export executes MOVE + TRAIN on 32 generated starting
  maps in both seats: 64/64 successful first-turn hires, exact bank subtraction, zero referee
  issues. This uses the local Java-parity referee, not 64 official platform games.
- Frozen compact SHA-256 `47849a135302e1bfda29d3fda54f76bdad70031b74ee6bc7f4494bc774a25609`,
  37,660 UTF-16 units. Module SHA-256
  `7c2ccefa33a80cc2258483c1a0f756cf1fc357c39bd093328a6ac2d31fd28bd6`.

The reused 8-map/12-family/two-seat development panel completed all 192 pairs in 107.87 seconds.
Every V439 reference field matches the frozen pre-fix panel. First hire moves from turn 2 in all
192 pre-fix games to turn 1 in all corrected games. There are zero command issues in either arm.
However, outcomes decline from **157 W / 2 D / 33 L (158 points)** to **153 / 2 / 37 (154 points)**.
Mean own/opponent scores move from 193.79/118.84 to 195.04/121.39; mean margin falls from +74.95
to +73.65. Own wood rises 46.78 to 47.04 and ring plants 10.92 to 11.33, without a win-rate gain.
The unchanged V439 reference is 173/5/14 (175.5 points), mean scores 238.46/110.56, margin +127.90.

| Local opponent family | Pre-fix W/D/L | Corrected W/D/L | Margin before / after |
|---|---|---|---|
| boss_real | 16/0/0 | 16/0/0 | 119.38 / 125.00 |
| compact_gold | 5/1/10 | 5/0/11 | -72.75 / -95.63 |
| gold_adaptive | 15/1/0 | 14/0/2 | 89.81 / 87.31 |
| legend_balanced | 13/0/3 | 14/0/2 | 104.69 / 102.38 |
| legend_v3_hp2_four | 16/0/0 | 16/0/0 | 139.75 / 145.19 |
| legend_v7_hp2_four | 16/0/0 | 16/0/0 | 148.06 / 156.75 |
| legend_v8_hp2_four | 16/0/0 | 16/0/0 | 142.63 / 146.13 |
| mybot | 15/0/1 | 13/0/3 | 36.25 / 33.94 |
| norx_native_three | 13/0/3 | 13/0/3 | 90.31 / 90.88 |
| resident | 1/0/15 | 1/2/13 | -51.31 / -50.63 |
| script_boss | 15/0/1 | 15/0/1 | 102.44 / 93.13 |
| silver_boss | 16/0/0 | 14/0/2 | 50.13 / 49.38 |

Whole-map point deltas are -3, -1, 0, 0, -1, -1, +1, +1. These are eight heavily reused maps,
not 192 independent observations; no fresh significance or ladder inference is made. The
machine-readable `panel-analysis.json` contains both scores, margins, match points and issues
for every family. Retain the valid rules capability in experimental code, but do not promote
the corrected greedy policy. Earlier hiring is not independently proven to be better, and the
changed action timing can alter later assignment/collisions. No new platform requests were made
for this fix while the V439 ladder candidate rolled out.

Evidence: `/data/separate_troll_farm-working/train-egress/2026-09-05/` (snapshot, generated-start
referee harness/log, frozen panel executable and TSV). The unedited Claude response is archived
under `scarce-denial/2026-09-05/claude-training-fix-response.json` in the same working-storage root.
