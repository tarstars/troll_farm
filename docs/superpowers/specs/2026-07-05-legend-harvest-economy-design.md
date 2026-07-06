# Legend harvest-economy bot (v1.5.0) — design

**Goal:** promote Gold→Legend (beat Boss 5) by replicating the decoded 180-wood
"continuous 4-troll" economy. Current live bot v1.4.5 (2-troll) banks ~90 wood @ rank 118.

## Decoded target (Tchoubidouwa123, game 895146562 — 180 wood)
- **4 trolls**, trained EARLY (turns ~3, 73, 119).
- **Big banana farm**: 45 BANANA plants over the game (v1.4.5 does ~15-20 standing).
- **Native-fruit funding**: 41 lemon + 26 plum harvested → funds the 4 trolls (banked as
  fruit early, spent on training).
- **Continuous operation, NO hard hold**: from ~t75 it chops AND replants simultaneously
  (late phase: 69 chops + 34 plants + 33 harvests together). "0 wood until t75" is just
  the funding/seeding ramp, not a deliberate withhold.

## Approach
Extend gold_elite's existing supply-variant infrastructure (this session's `planters`
field + `(1,1,1,1)` cheap-planter training + no-hold + configurable farm cap) — it
structurally matches the decode. Port that to `main.rs decide_elite` as v1.5.0. NOT a
from-scratch rewrite (would re-derive working logic and risk new bugs).

## Bot design (v1.5.0)
- **Roles (4 trolls):** starter `(1,1,1,1)` + 1 cheap planter `(1,1,1,1)` + 2 choppers
  `(2,2,0,2)`. Train order: chopper#1 → planter → chopper#2, each funded by native fruit.
- **Planters** (starter + planter, hp>0): early — harvest native lemon/plum to fund
  trolls; sustained — banana printer (harvest banana fruit for seeds, PLANT near base),
  keeping a LARGE farm (cap ~24) stocked. Seed-reserve keeps ≥2 bananas fruiting.
- **Choppers** (×2): perma-fell farm + native trees, bank when full (cc=2). Run
  continuously from training; the 2 planters keep the farm big enough to feed both.
- **No hold** (`hold_until=0`). Farm cap 24 (vs v1.4.5's 12).

## Validation & ship — ARENA-FIRST (user decision)
The local sim rates all 4-troll builds below v1.4.5 (transfer wall); we IGNORE that and
judge by real arena rank. Steps:
1. Port to `main.rs decide_elite` (v1.5.0). Keep default = new economy; keep the knobs.
2. Compile-check, minify, size-gate (≤99000), freeze to `cgauto/submissions/`.
3. Submit via `api_submit.py`; monitor rank vs v1.4.5's 118 for ~40 min (findProgressByPrettyId).
4. **If it regresses below ~118, REVERT** to frozen `v1.4.5-seedreserve.min.rs`.
5. If it holds/improves, iterate tuning (farm cap, troll mix) with more arena tests.

**Success = rank clearly better than 118 (toward Legend); Failure = regression → revert.**

## Risks
- Transfer failure (multi-troll historically regressed in sim; arena unknown). Mitigated
  by the frozen-fallback revert.
- Placement churn dips rank ~40 min during the test (acceptable, recoverable).
- 4-troll funding may not complete on sparse arena maps → weak games there. Watch for it.
