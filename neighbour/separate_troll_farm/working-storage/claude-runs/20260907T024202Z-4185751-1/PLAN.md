# PLAN — orchard / near-bank fruit-production economy (frozen before measurement)

Written 2026-09-07T03:04Z (`date -u`), before any test or panel row exists.

## Mechanism (falsifiable)

Parent `claude_candidate_policy_flat.rs` (sha256 95ee691e…) mints no fruit for
recruitment. Its only PLANT paths are *timber* regeneration: the near-bank
`PICK BANANA` → PLANT branch is gated on `view.plants.len() <= 2` and turn>=100
(a deforested board) and exists to be **chopped back into wood**; the mother-tree
branch is the same idea. `can_train`/`training_affordable` then hard-stop at
`n >= 2`, so the workforce is capped at two whatever the bank holds.
`apply_harvest` credits a troll only when `u_hp >= i`, so an hp0 hire can never
forage. Result (field screen): two workers, monoculture bank, no recruitment.

**Change — one coherent orchard controller, variant `a`:**

1. *Role (capability-aware).* Orchardist = among own trolls with
   `harvest_power >= 1`, the one minimising `(chop_power, carry_capacity, id)` —
   the **least** valuable forester, never the best one. If no troll can harvest,
   the orchard is disabled entirely.
2. *Finite near-bank plan.* At most `ORCHARD_SITES = 2` own trees on walkable
   cells within BFS distance `<= 2` of a shack door (shack cell excluded, no
   existing plant). Planting stops after turn 210, starts at turn 40, and only
   while the next hire's bill is unmet — the plan is finite, not a forest.
3. *Executed multi-turn loop* injected into `main_candidates` (the actually
   executed controller, not a proposal a later stage rewrites): `PICK <kind>`
   at the bank (6200) → MOVE to a free site (6300 − dist) → `PLANT` (6400) →
   grow → MOVE/`HARVEST` ripe orchard tree (6100 + fruits) → the parent's own
   bank candidates (7000/8000) carry it home. 6100–6400 outranks chopping
   (≈1000–1900) and loses to banking, so a full orchardist still banks.
4. *Kind by deficit.* The planted/picked kind is the PLUM/LEMON/APPLE with the
   largest shortfall against the chosen hire's `training_cost(2, spec)`.
5. *Protection, scoped.* While the bill is unmet, chop candidates targeting a
   live orchard-kind tree inside the near-bank radius are dropped. Nothing else
   is protected.
6. *Recruitment.* A separate `orchard_hire` emits `TRAIN` when and only when
   `n == 2`, no opening TRAIN this turn, turn ≤ 240, `TOTAL_TURNS − turn > 20`,
   the orchard is live, the shack cell holds no unit, and the bank affords the
   bill by the referee's own rule (iron only when `!view.iron.is_empty()`).
   Spec is chosen strongest-affordable from `(2,2,1,1) → (1,2,1,1) → (1,1,1,1)`,
   all `harvest_power >= 1`: a producer-capable hire, so it can forage the next
   basket rather than being physically unable to pick fruit.

Prediction: on a development board the orchardist really executes
PICK→PLANT→grow→HARVEST→DROP, banked fruit rises, and a third worker is trained
from orchard fruit. Displaced wood income is real and is measured, not assumed
away.

## Comparison, budget and decision rule (frozen)

1. `rustc 1.90.0 --test` on `claude_candidate_orchard_a_tests.rs`, which carries
   the untouched parent as `mod baseline`; both arms on one real referee, same
   board/seat/opponent. All tests must pass. Required fixtures: full
   plant→growth→harvest→bank cycle; finite seed/recruitment cost; blocked-bank
   recovery; late-game legality.
2. Serial 16-stream bench (`benchmark_lookahead.py --games 16`, absolute rustc
   1.90, nothing else running): max decision < 50 ms and
   `packaging_different_games == 0` (readable vs compact equality) FIRST.
3. Then exactly one panel: `candidate_compare_panel`, 192 pairs, seeds
   9947500..9947507, both seats, 12 adaptive opponents, `ALLOW_ANY_MAP_SEED=1`,
   run-local `CARGO_TARGET_DIR`, the just-built binary. Baseline command arrays
   must match run 20260906T210944Z-3184968-1's authoritative controls.
4. **Gate (both required):** whole-panel candidate W+0.5D strictly greater than
   baseline **and** zero candidate critical issues. Otherwise PARK — no
   parameter sweep, no second variant, no re-tune, no holdout. Failed games stay
   in the denominator. Report W/D/L, points, own/opponent score, margin,
   per-opponent deltas, and how many pairs actually planted/harvested/hired.

No fresh maps, no favourable-map selection, no platform action, no commit,
no additional agents. Offline only.
