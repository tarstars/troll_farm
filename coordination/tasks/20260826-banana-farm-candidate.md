# 20260826-banana-farm-candidate: Track F-2 — the banana wood farm candidate, from the owner's contract to the ladder queue

- Status: **CLOSED — the line closed by the owner 2026-08-27T10:04Z ("closed")**; obituary in `coordination/GRAVEYARD.md`. Previously: chartered 2026-08-26T19:55Z; stopped at validity 2026-08-27 ~02:00Z; viewed on the ladder one hour (10.8/172); a denial-first repair designed and parked (below). Board row F-2.
- Record owner: local_claude_1 · Work owner: **claude_1** (design packet, then build, then panel) · Reviewer: **codex_1** (design ≤ 2 rounds; one panel reproduction) · Arena: the coordinator submits, in the ladder queue's order.
- **Design input (binding):** `docs/BANANA-FARM-CONTRACT-2026-08-26.md` — the owner's stages, the three owner decisions (the hut ring; a one-way latch; mothers-only planting during denial), the verified rules (wood = 4 points; one seed → 16 points; trees are walkable; denial earns wood), the restored worker rules of §3, and the acceptance shape of §5. A design that departs from the contract says where and why, in the packet, before the build.
- **Done means:** (1) a design packet `claude_1/farm/g0-farm-2026-08-2x.md` that fixes what the contract leaves open (§6: the aim-selection rule; the latch threshold and the denial round criterion K, calibrated from the turn corpus `data/processed/turns.jsonl.gz`; whether the capacity-2 troll is trained first; the exact state machine TRAIN → DENY(+mothers) → FARM → WOOD with one-way edges) and pre-commits the panel gates; (2) codex_1 ACCEPT within two rounds; (3) the build as a diff on the readable champion `readable/door1-champion.rs` (`readable/diffs/banana-farm.diff`), round-trip identity, plus the diagnostic (v6) line extended with the farm's state (plants, mother harvests, latch turn, denial end reason, enemy chops on the ring); (4) **one local panel** (240 games + fixtures): containment byte-identical with the farm off; **validity first** — no new blocked games, no no-progress turns, the worker rules of contract §3 measured; the latch fires ≤ 1× per game and never resets; every changed game named with its own-score delta; (5) codex_1's one reproduction; (6) **queued on the ladder as slot 3**: submitted by the coordinator when L-1's block ends, **only if the validity gates pass** — a farm that blocks or strands trolls does not go on the platform (the August-2 lesson: 12.99 at rank 127); the value number from the panel is a go/no-go for the slot, never a verdict; (7) on the ladder: an A-B-B-A block against the champion with diagnostics, 8 reads each, plus the annotated games — the ladder is the judge.
- **Dead means:** the design cannot be made to pass two rounds; or the validity gates fail on the panel (then the packet says which worker rule broke and on which games, the obituary is written, and the owner decides in the morning whether a bounded repair is chartered).
- **Budget:** design ≤ 2 rounds; 1 build; 1 panel; 1 reproduction; 1 ladder block (slot 3); calendar: design tonight, build + panel by 2026-08-27 evening, ladder as the queue allows.
- Created UTC: 2026-08-26T19:55:00Z · Last updated UTC: 2026-08-26T19:55:00Z

## Order tonight

claude_1: finish bot B's file for L-1 first (small), then the design packet from the contract; codex_1: L-1's byte-identity check first, then the design review. The coordinator wakes hourly: rulings that unblock, the L-1 ledger, the board.

## Do not touch

The resolver's hold logic; the Arena (coordinator only); `data/raw/games/`; the cron; hash-locked sources with formatters.

## The parked repair design, on file (designed 2026-08-27 07:15Z; owner chose (a) at 07:40Z; superseded by the champion ablation at 08:05Z; line closed 10:04Z)

**Denial first, farm next**, as the owner asked ("chopping down plum or lemon first, banana farm next"):
1. **Aim = every plum and lemon tree standing on the opponent's half**, nearest first (bigger first among
   equals); apple dropped; the packet's species-selection rule (§3) removed.
2. **Denial is the trolls' job:** once the second troll exists, a troll that is free (not carrying wood,
   with room and chop power) and has a plum/lemon in reach is filtered to the denial offers (the seed
   guard's shape), keeps its tree until it falls, and two trolls never take the same tree; a wood carrier
   still banks first (W1).
3. **Denial does not end for lack of targets:** it ends on the first of — we felled everything we saw and
   nothing regrows (the existing round rule, K = 2 rounds of 40 turns), the opponent trains a third troll,
   turn 120. With no target in sight the bot plays as the champion.
4. **(a) Nothing is planted until denial ends** (reverses owner decision 3 of the contract); then the farm
   as built (plots and mothers), with its known weaknesses unchanged (the opponent eating the ring crop;
   the latch counting chops).

Coordinator's assessment at the time: the opponent's second troll is paid from the starting shack (2–10 of
every fruit), the four leaders never train a third troll and train the second at turns 18–28, so early
denial rarely *prevents* a power troll — it removes the trees afterwards and pays 4 points a wood; a
full-size plum/lemon has 12 health (one troll, 12 hits, 16 points); expected effect a point or two either
way. The ladder viewing later showed the built farm's denial stage did run (65 turns a game).

