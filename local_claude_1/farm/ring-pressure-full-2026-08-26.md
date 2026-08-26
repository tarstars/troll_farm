# Ring pressure at corpus scale — claude_1's `ring_pressure.py` run unchanged over all 23,613 replays (host, 2026-08-26 20:30Z)

Answer to the F-2 packet's Q2: **yes, the script runs unchanged** (`--games data/raw/games`), all 23,613 replays, 0 skips, 0 unattributed events, ~4 minutes. Output (66 MB, 47,226 game-seats, not committed): scratch `ring/ring-pressure-full.json`; the ratio recipe recovered as `fe / max(harvest_ring + chop_ring, 1)` (`local_claude_1/farm/ratio.py`), which reproduces the packet's 290-replay numbers exactly (leaders n=37: median 0.208, Q3 0.561, max 2.83; field median 0.142, max 16.0). All 580 of the packet's rows are present in the full set and identical on every core field.

## fe/fw = enemy chop hits on our ring ÷ our own accepted harvests + chops on the ring (whole game)

| cohort | n seats | median | Q3 | max | share > 1.0 | share > 0.56 |
|---|---:|---:|---:|---:|---:|---:|
| leaders (goq, yaichi, Stounate) | 2,073 | 0.254 | 0.705 | 39.0 | **17.1 %** | 30.5 % |
| field (301 bots) | 34,879 | 0.263 | 0.681 | 204.0 | 16.1 % | 30.0 % |
| **ours (`tass`)** | 10,274 | **0.000** | 0.076 | 17.0 | 0.5 % | 1.7 % |

Per leader: Stounate n=948 median 0.315, Q3 0.935 (23.3 % > 1.0); goq n=903 median 0.241, Q3 0.605; yaichi n=222 median 0.136, Q3 0.462. Ours is ≈ 0 because we barely plant on the ring — the ratio has no denominator for us.

## The confound: game length

| leaders | n | median | Q3 | max | share > 1.0 |
|---|---:|---:|---:|---:|---:|
| games ≥ 290 turns | 1,750 | 0.194 | 0.541 | 39.0 | 11.9 % |
| games < 290 turns | 323 | **0.891** | 1.909 | 21.0 | **45.5 %** |

Full-length leader games land on the packet's 0.21 / 0.56. The packet's sample was 91.7 % full-length; the whole collection is 72.9 % (34,420 seats at exactly 301 keyframes; 77.5 % ≥ 290; 10,638 seats shorter; 86 under 50 turns; none above 301 — **the 300-turn cap is real**). Short games carry the mass above 1.0: in a game that ends early, the ring's denominator is small and the ratio spikes.

## What this means for the packet (for codex_1's round-1 review, not a ruling)

- The claim "leader-like play never latches" holds on full-length games (12 % > 1.0 whole-game) but not on short ones (46 %). A latch measured over a 60-turn window must say what it does when the game is ending early — or the window/threshold should be conditioned on turns remaining.
- The threshold 1.0 stays 5× the full-game leader median; whether it should also clear the short-game leader median (0.89) is a design choice for the reviewer.
- Worst seat in the corpus: `icecuber` g895486025 — 204 enemy chops on its ring against 1 own ring event (19 ring plants, never worked): the August-2 shape at its extreme.

Command: `nice -n 10 python3 ring_pressure.py --games data/raw/games --out ring-pressure-full.json` (script from `agent/claude_1:claude_1/farm/ring_pressure.py`, unmodified).
