# 4b buckets D and E — owner ruling 2026-08-21 (~08:55Z): OSC-026 and OSC-012 are BUGS; 4b CLOSED

Recorded by local_claude_1 from the owner's words. Facts from the FROZEN library
(`claude_1/banana-restoration-r2/oscillation-library-98628e98/library/`) and the champion
grader (`claude_1/picker2/sweep34-door1-base.json`). Companion record for bucket B:
`4b-bucket-B-ruling-2026-08-21.md`.

## The rulings

| case | owner's judgment (verbatim gist) | ruling |
|---|---|---|
| OSC-026 | "there is a tree ⇒ there is work ⇒ can improve score ⇒ bug" | **BUG under R-2, known-open** |
| OSC-012 | "one troll is on a tree and another oscillates — we already discussed such a case — bug" | **BUG under R-2, known-open** |

The two proposed stamps ("no pairing decision exists to be wrong"; "waiting was provably
correct") are **withdrawn**. Each was true of the unit it described and beside the point of the
game: 026 is not a pairing case at all, and 012's "correct waiter" is the troll that blocks the
only tree for the whole game.

## OSC-026 — a single troll flips between two jobs

- Window t17–25 (9 turns), our only troll #0 (speed 1, carry 2, harvest 1, chop 1) steps
  (1,4) ↔ (2,4) beside our shack; 8 MOVEs and 1 PICK in the window.
- One plant on the map: a LEMON at (9,1), 3 fruits, 12 hp, reachable (open map). Shack
  inventory: 1 lemon, 2 iron, 1 wood.
- No teammate exists, so no blocking of any kind. Library label **M3: the alternation comes
  from the goal selector** — two jobs nearly tied, the winner flipping with every step (the
  PICK suggests "harvest the lemon" vs "pick the seed and plant here"; which two is
  unmeasured and not claimed).
- Champion `547fa706`: NOT FIXED — detector fires, no progress.
- Mechanism for the ledger: **single-troll goal-selector flip** (third mechanism, distinct
  from bucket B's three).

## OSC-012 — the useless troll parks on the only tree for the whole game

- One-wide corridor, our shack at the east end (12,2); the ONLY plant is an APPLE at (11,2),
  20 hp, 3 fruits, adjacent to the shack.
- Troll #2 (speed 2, carry 1, **harvest 0, chop 0**) stands on the apple from t8 to t200 —
  193 turns, wait fraction 1.00, never moves.
- Troll #0 (speed 1, carry 2, harvest 1, chop 1 — the one that can work) dances (9,2) ↔ (10,2)
  in front of it for all 193 turns. Two opponent trolls sit west at (7,2), (8,2); they never
  block (enemies may share cells).
- Library label **M2: an idle unit occupying the plant cell, invisible to the bot's
  compatibility check** (a WAIT carries `Target::None`, so the tree is never seen as taken).
  A swap — legal between own units in one turn — would have resolved it at turn 8.
- Champion: NOT FIXED — detector fires, no progress.
- By cost the worst case of the 34: the entire game, both trolls.
- Open question it raises (owner's, not chartered): **why did the opening train a troll with
  neither harvest nor chop power?** (`choose_second_troll` / opening policy.) Separate look if
  the owner wants it.

## 4b CLOSED — the 34, accounted

| status | count | cases |
|---|---:|---|
| FIXED on the champion (bucket A) | 8 | 003 006 008 009 014 020 028 034 |
| BUG, benching class, cure on the shelf (bucket C) | 18 | 001 002 004 007 011 013 015 016 017 018 019 021 022 023 024 025 029 031 |
| BUG, ruled at the 4b sittings today | 6 | 005 010 027 030 (bucket B) · 026 (D) · 012 (E) |
| pending the cause-attribution G-3 (bucket F) | 2 | 032 033 |
| **total** | **34** | |

Every case now ends FIXED-with-proof, owner-ruled BUG, or in one named measurement. No
stamp of "accepted / harmless" was issued in 4b: all six candidates turned out to be bugs on
the owner's look, which is the record's own verdict on the coordinator's proxy-based stamp
proposals.

## Mechanisms named across the six (for any future cure charter — none is chartered)

1. Corridor pass blocked by a working teammate → **swap** (005, 027; R-1 shape)
2. Open-map pass blocked → **teammate-aware routing** (010)
3. Same tree wanted while a teammate works it → **tree reservation** in the picker (030)
4. Single-troll **goal-selector flip** (026)
5. **Idle troll parked on a plant cell**, invisible to the compatibility check → yield / swap (012)

A swap rule alone would have cured 005, 027 and 012 (the most expensive one).
