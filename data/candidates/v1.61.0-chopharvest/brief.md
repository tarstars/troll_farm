# v1.61.0-chopharvest builder brief — chopper opportunistically harvests full trees

**Base:** champion v1.59.0-ringfix3. Bump VERSION → "1.61.0-chopharvest". Preserve all OTHER
champion consts. This runs in PARALLEL with the etudes library build (different files; no conflict).

**Origin (user, 2026-07-11):** the ring's fruit bananas fill to the cap (`fruits < MAX_FRUITS`
stops growth) and STALL when the gatherer is off foraging distant (the documented mid-game farm
death). The CHOPPER banks wood right next to the ring but NEVER harvests — because its spec is
`(2,3,0,2)` → hp=0, and every harvest band gates on `harvest_power > 0`. User's idea: let the
chopper harvest the full/ripe bananas WHEN IT DOESN'T CONTRADICT CHOPPING — cheap, keeps the ring
producing, un-caps stalled trees, banks the fruit as points.

## The two changes

### 1. Chopper spec: hp 0 → 1
`GE_SPEC: (i32,i32,i32,i32) = (2, 3, 0, 2)` → `(2, 3, 1, 2)` (botmain.rs ~:87). Cost impact:
training_cost apple = `n + hp²`, so for the 2nd troll it goes 2 → 3 = **+1 apple** (verify the
funding ladder still affords it; the farm/starting apples cover it — but check the boss gate that
the chopper still trains on time, train-turn not delayed vs ringfix3).

### 2. Chopper opportunistic-harvest — STRICTLY below all its chopping
With hp=1 the chopper now qualifies for harvest bands. THE CONSTRAINT (user's "doesn't contradict
chopping"): the chopper's harvest must be LOWER priority than its fell (70/72), chop-help (40/42),
and funding work — so chopping/felling ALWAYS wins; harvest fires only when the chopper is
otherwise idle or passing. INVESTIGATE FIRST: with hp=1, which existing bands fire for the
chopper? The high harvest bands — standing-harvest (75, planner.rs ~:509-525) and fruit-MoveTo
(62) — sit ABOVE the fell bands and would make the chopper HARVEST INSTEAD OF FELL (bad, violates
the constraint). The idle-fruit band (38) sits BELOW chop-help (40) — that's the RIGHT priority.
So:
- GATE the chopper OUT of the high harvest bands (75 and 62) — keep those non-chopper-only (add
  `!is_chopper` to their firing condition, or equivalently gate them on the starter). Confirm
  this does NOT change the STARTER's behavior (byte-identical for the hp=1... wait, starter hp=1
  already — so 75/62 already fire for the starter; adding `!is_chopper` leaves the starter
  untouched and only newly-excludes the chopper, which never reached them at hp=0 anyway → net
  behavior change is ONLY for the now-hp=1 chopper).
- LET the chopper use the idle-fruit band (38) (planner.rs, gated `harvest_power>0` +
  `free_capacity>0` + no higher task): with hp=1 it now fires, below all the chopper's chopping —
  exactly "harvest when not chopping." Confirm idle-fruit already exists and fires for any
  hp>0 troll; if it's currently starter-gated, widen it to the chopper.
- PREFER full/near-cap trees: within the chopper's opportunistic harvest, if choosing among ripe
  fruit, prefer the one closest to MAX_FRUITS (the stalled-throughput case the user flagged) —
  a small tie-break, not a new band. (If simpler to just harvest the nearest ripe fruit, that's
  acceptable; note which you did.)

## What must NOT change
- The STARTER's behavior: byte-identical to ringfix3 (it already has hp=1; the `!is_chopper`
  gate on 75/62 must not alter it — verify with a starter-unchanged test).
- The chopper's FELLING: it must still fell exactly as ringfix3 when a fell/chop-help task exists
  (harvest is strictly lower priority). The wood cycle is the +1.7 core — do not disturb it.
- Champion consts other than GE_SPEC.

## Tests (TDD, RED first)
1. `chopharvest_spec_hp1`: GE_SPEC == (2,3,1,2).
2. `chopharvest_fells_over_harvest`: a chopper with a valid fell target (band 70) AND a ripe
   adjacent banana → command is the FELL/CHOP, NOT harvest (harvest strictly below chopping). RED
   if the chopper harvests (e.g. if band 75 fires for it). Must pass — the core constraint.
3. `chopharvest_harvests_when_idle`: a chopper with NO fell/chop-help task, free capacity, adjacent
   to a ripe/full banana → command is HARVEST. RED pre-change (hp=0 → can't harvest). GREEN after.
4. `chopharvest_starter_unchanged`: a starter (chop=1, hp=1) in a state with a ripe fruit → its
   command is byte-identical to a ringfix3 baseline (the `!is_chopper` gate on 75/62 must not touch
   the starter).
5. Full suite green + self-determinism equality 8 seeds.

## Gates + validation
- Standard builder gates (cargo test, bundle→rustc→minify<100KB→compile, freeze artifacts + DEBUG
  probe). VERSION 1.61.0-chopharvest. Commit per logical step (trailer
  `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`); COMMIT OFTEN (API drops subagents).
- Candidate validation (play vs boss ≥6 with the DEBUG probe, paired vs ringfix3 on the same
  batch, sequential to avoid 422s). REPORT: (a) chopper train-turn NOT delayed vs ringfix3 (the
  +1 apple didn't stall training); (b) does the chopper actually HARVEST full/ripe bananas (grep
  HARVEST by the chopper id in the replays)? does the ring stay alive longer (last-ring-plant
  turn, fruit cadence in the back half vs the documented t148 death)? (c) WOOD must NOT drop vs
  ringfix3 (the chopping is the +1.7 core — if wood drops, the harvest is stealing chop turns →
  fail); (d) score/win-rate.
- If wood drops or the chopper stops felling effectively → the harvest is contradicting chopping
  → flag before freezing (the constraint is violated).

Report: status, commits, the exact band changes (hp bump + how you kept harvest below chopping +
the 75/62 `!is_chopper` gate), test summary (RED evidence each), the paired boss validation
(train-turn, chopper-harvest-count, ring-longevity, wood vs ringfix3, win-rate), self-equality,
artifact sizes, concerns. NOTE (temper expectations): this is farm-sustainability class (0-for-3
in the arena — seedloop/reserve/ownership) but a fresh cheap mechanism; the arena decides.
