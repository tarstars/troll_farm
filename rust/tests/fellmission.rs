//! FellForWood mission tests (v1.60.0-fellmission): the wrong-tree fix (pick the reachable
//! tree by wood EFFICIENCY, not the nearest tanky one), commitment (no abandon/backtrack),
//! and the decide_elite wiring (the chopper runs the mission and is excluded from the band
//! system; everyone else's bands are untouched; the joint move solver still resolves
//! everyone's movement together). See
//! docs/superpowers/plans/2026-07-10-fellmission.md and
//! docs/superpowers/specs/2026-07-10-intent-missions-design.md.
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign_resolved;
use troll_farm::botmain::tactics::{Phase, Plan, RingRole};
use troll_farm::botmain::{missions, resolve_commands, State, Tree, Troll, WOOD};

const SHACK: (i32, i32) = (0, 2);

fn open_room() -> HashSet<(i32, i32)> {
    let mut w = HashSet::new();
    for x in 0..14 {
        for y in 0..8 {
            w.insert((x, y));
        }
    }
    w.remove(&SHACK); // shack cell impassable (convention: ringfix3.rs / planner_tasks.rs)
    w
}

fn base_state() -> State {
    State {
        walkable: open_room(),
        my_shack: SHACK,
        opp_shack: (13, 6),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 60,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

/// The champion chopper (GE_SPEC = (2,3,0,2)): ms=2, cc=3, hp=0, chop=2.
fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 2,
        carry_capacity: 3,
        harvest_power: 0,
        chop_power: 2,
        carry: [0; 6],
    }
}

/// An enemy chopper (for the race/doomed-tree check).
fn opp_chopper(id: i32, x: i32, y: i32, chop_power: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 2,
        carry_capacity: 3,
        harvest_power: 0,
        chop_power,
        carry: [0; 6],
    }
}

fn tree(ty: &str, x: i32, y: i32, size: i32, health: i32) -> Tree {
    Tree {
        tree_type: ty.into(),
        x,
        y,
        size,
        health,
        fruits: 0,
        cooldown: 0,
    }
}

/// A pure gatherer (chop_power=0, like ringfix3.rs's `gatherer()`): isolates it from every
/// fell-related band (40/42/31/30 all gate on `u.chop_power > 0`), so its behavior in the
/// Task 4 wiring test cannot collide with the chopper's mission target.
fn gatherer(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 1,
        harvest_power: 1,
        chop_power: 0,
        carry: [0; 6],
    }
}

/// The REAL starting troll (mapgen.rs ms=1/cc=1/hp=1/chop=1 — every game starts with exactly
/// one of these per side). Unlike `gatherer` (chop_power=0), this "hand" DOES emit chop-help
/// (band 42/40) and anti-starvation (31/30) Wood-claim candidates — Code review Fix C2 is
/// specifically about whether the joint matcher deconflicts THIS troll's claims against the
/// chopper's.
fn starter_hand(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 1,
        harvest_power: 1,
        chop_power: 1,
        carry: [0; 6],
    }
}

/// A Plan with the REAL champion consts, rest hand-set — same convention as
/// ringfix3.rs/planner_tasks.rs's `base_plan`. `ring: vec![]` (off the ring path) so this
/// test exercises only the pieces relevant to the chopper's mission / the gatherer's legacy
/// bands, not the ringfarm economy.
fn base_plan(st: &State) -> Plan {
    let farm_d = troll_farm::botmain::bfs_distances(&st.walkable, &[st.my_shack]);
    Plan {
        shack: st.my_shack,
        farm_d,
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 240,
        n: 2,
        farm_now: 0,
        nchop: 1,
        spec: (2, 3, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 2, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 2,
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 2,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 0,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
        pressure: ownership::Pressure::default(),
        door: None,
        door_d: None,
        ring: vec![],
        raid: false,
    }
}

/// A plan permissive enough that own_half/within_roam never reject the pre-existing
/// efficiency/doomed/commitment tests' hand-picked tree coordinates (chosen for clean
/// manhattan arithmetic centered on a chopper far from the shack — never meant to exercise
/// realistic farm-radius placement). Isolates those tests from the C1 ring-protection filters
/// added below. fell_ok's meaningful gates (diag_ring, seed_cells, liquidation) stay at
/// `base_plan`'s real, champion-faithful defaults (empty ring/seed_cells, liquidation=false).
fn permissive_plan(st: &State) -> Plan {
    Plan {
        opp: (-1000, -1000), // own_half: every in-room tree is nearer our shack than this
        chop_r: 1000,        // within_roam: trivially true regardless of distance from shack
        ..base_plan(st)
    }
}

// ── Task 2: the wrong-tree fix — pick by wood efficiency, not nearest-tank ──────────────

#[test]
fn fellmission_picks_wood_efficient_tree_not_nearest_tank() {
    // Clipboard geometry (plan Task 2 Step 1): chopper at (6,2); APPLE (7,1) health 20 size
    // 4, LEMON (7,0) health 12 size 4, BANANA health 6 size 4, farther. NOTE: the plan's
    // illustrative banana cell (9,5) is manhattan-6 from (6,2), which cannot reproduce the
    // plan's own worked efficiency (4/(4+3)=0.57, i.e. steps=4) on an open grid — BFS
    // distance can never be LESS than manhattan distance, so (9,5) would tie the lemon's
    // 0.44 (4000/(6+3)=444) instead of beating it. Relocated to (8,4), which IS genuinely 4
    // steps away (manhattan (6,2)-(8,4) = 2+2 = 4) and reproduces the plan's exact worked
    // numbers (apple 0.33 < lemon 0.44 < banana 0.57) while remaining farther than both the
    // apple(2) and the lemon(3) — see the plan's Self-Review ("test State construction is
    // sketched... implementer must fill it").
    let mut st = base_state();
    let u = chopper(0, 6, 2);
    st.trees = vec![
        tree("APPLE", 7, 1, 4, 20), // steps=2, chops=ceil(20/2)=10, eff=4000/12=333
        tree("LEMON", 7, 0, 4, 12), // steps=3, chops=ceil(12/2)=6,  eff=4000/9=444
        tree("BANANA", 8, 4, 4, 6), // steps=4, chops=ceil(6/2)=3,   eff=4000/7=571 (winner)
    ];
    st.my_trolls = vec![u.clone()];
    let plan = permissive_plan(&st);
    assert_eq!(
        missions::fell_target(&st, &plan, &u),
        Some((8, 4)),
        "the soft banana (fewer chops) must win on wood-efficiency even though it's farther \
         than both the lemon and the tanky apple — the apple must never be chosen"
    );
}

#[test]
fn fellmission_skips_doomed_tree() {
    // Same 3 trees, plus an enemy chopper standing ON the banana (the efficiency winner)
    // with enough chop_power to fell it before we arrive: our_eta = ceil(steps/ms) =
    // ceil(4/2) = 2; enemy chop_power=6 fells health=6 in ceil(6/6)=1 <= 2 turns -> doomed.
    // fell_target must skip it (never donate the travel) and fall back to the LEMON (0.44 >
    // apple's 0.33).
    let mut st = base_state();
    let u = chopper(0, 6, 2);
    st.trees = vec![
        tree("APPLE", 7, 1, 4, 20),
        tree("LEMON", 7, 0, 4, 12),
        tree("BANANA", 8, 4, 4, 6),
    ];
    st.opp_trolls = vec![opp_chopper(99, 8, 4, 6)];
    st.my_trolls = vec![u.clone()];
    let plan = permissive_plan(&st);
    assert_eq!(
        missions::fell_target(&st, &plan, &u),
        Some((7, 0)),
        "the banana is doomed (enemy fells it before our ETA) — fell_target must skip it and \
         fall back to the lemon, not the tanky apple"
    );
}

// ── Task 3: commitment — no abandon/backtrack; re-plan only on Done/Invalidated ─────────

#[test]
fn fellmission_commits_then_replans_on_done() {
    missions::reset();
    let u = chopper(0, 6, 2);

    // Turn A: only the lemon (7,0) stands (steps=3, chops=6, eff=444) -> committed to it.
    let mut st = base_state();
    st.trees = vec![tree("LEMON", 7, 0, 4, 12)];
    st.my_trolls = vec![u.clone()];
    // st.walkable/my_shack/opp_shack never change across turns A/B/C (only st.trees mutates),
    // so one permissive plan is valid for all three chopper_target calls below.
    let plan = permissive_plan(&st);
    let turn_a = missions::chopper_target(&st, &plan, &u);
    assert_eq!(
        turn_a,
        Some((7, 0)),
        "turn A must commit to the only standing tree (lemon)"
    );

    // Turn B: a NEARER, more efficient banana appears (steps=1, chops=3, eff=4000/4=1000) —
    // a FRESH fell_target() would prefer it (1000 > 444), but the mission must NOT abandon
    // the already-committed lemon (no flap/backtrack).
    st.trees.push(tree("BANANA", 6, 1, 4, 6)); // adjacent to the chopper: steps=1
    let turn_b = missions::chopper_target(&st, &plan, &u);
    assert_eq!(
        turn_b,
        Some((7, 0)),
        "committed mission must not flap to a newly-nearer/more-efficient tree"
    );

    // Turn C: the committed lemon is felled (Done — removed from state.trees, matching the
    // engine's real behavior of dropping a plant the instant health<=0). Only the banana
    // remains, so the mission re-plans to it.
    st.trees.retain(|t| t.pos() != (7, 0));
    let turn_c = missions::chopper_target(&st, &plan, &u);
    assert_eq!(
        turn_c,
        Some((6, 1)),
        "once the committed target is Done (felled/gone), the mission re-plans to the next best"
    );
}

// ── Task 4: decide_elite wiring — chopper mission, others' bands + joint-solve unchanged ──

#[test]
fn fellmission_chopper_uses_mission_starter_unchanged() {
    missions::reset();
    // A 2-troll state: a chopper far from a gatherer, one lemon EXACTLY ms(=2) steps from
    // the chopper (6,2)->(4,2) — WEST, within base_plan's real chop_r(5)/farm_r(2) roam of the
    // shack (0,2) (Fix C1: the mission now filters candidates through fell_ok/own_half/
    // within_roam, same as the champion's bands, so the test tree must actually be in realistic
    // roam) — so the joint solver's max-progress landing is uniquely the tree cell itself
    // (distance 0 to goal cannot be tied) — no tie-break ambiguity to hand-verify. The gatherer
    // (chop_power=0) has zero overlap with any fell band, so nothing here can make it compete
    // with the chopper's mission target.
    let mut st = base_state();
    st.trees = vec![tree("LEMON", 4, 2, 4, 12)];
    st.my_trolls = vec![chopper(1, 6, 2), gatherer(0, 1, 2)];
    let plan = base_plan(&st);

    // (a) the chopper's emitted command is a MOVE toward its mission target (not on it yet),
    // landing exactly on the tree this turn (distance 2 == movement_speed 2) — NOT whatever
    // the legacy bands would have produced for a chopper (which this mission entirely
    // replaces).
    let cmds = resolve_commands(&st, &plan, &st.my_trolls);
    assert_eq!(
        cmds[&1], "MOVE 1 4 2",
        "the chopper must move toward its FellForWood mission target, landing on it this turn"
    );

    // (b) the gatherer's command is byte-identical to a baseline run with ONLY the gatherer
    // through assign_resolved — excluding the chopper from the band system, and the final
    // joint-solve-with-everyone pass, must not perturb it (the +1.7 economy stays on the
    // bands, untouched).
    let baseline = assign_resolved(&st, &plan, &[gatherer(0, 1, 2)]);
    assert_eq!(
        cmds[&0], baseline[&0],
        "excluding the chopper from the bands + the final joint solve must not change the \
         gatherer's command"
    );
}

// ── Code review Fix C1: fell_target must respect the ring protections ──────────────────────

#[test]
fn fellmission_never_fells_protected_ring_diagonal() {
    // The ring-protection defect: fell_target originally ignored fell_ok/own_half/within_roam
    // entirely, so the chopper's committed mission could target our OWN standing diagonal
    // seed-banana (the ring economy's fruit/seed engine) — it is small/soft and CLOSE, so it
    // wins on raw wood-efficiency math over a farther, tankier native tree, even though
    // ringfix3's bands 70/72 would never touch it (fell_ok blocks any standing
    // `RingRole::Diagonal` cell outside liquidation/raid).
    //
    // Chopper at (2,2); diagonal ring cell (1,1): steps=2 (BFS, orthogonal movement),
    // chops=ceil(2/2)=1, eff=4*1000/(2+1)=1333 — WINS on raw efficiency, unfiltered.
    // Native LEMON (4,2): steps=2, chops=ceil(12/2)=6, eff=4*1000/(2+6)=500 — must win once
    // the diagonal is correctly excluded. Both cells are within base_plan's real chop_r(5)/
    // own_half of the shack (0,2) — this is a REALISTIC ring-adjacent geometry, not a
    // permissive-plan test.
    let mut st = base_state();
    let u = chopper(0, 2, 2);
    st.trees = vec![
        tree("BANANA", 1, 1, 4, 2),  // protected diagonal ring cell — must be skipped
        tree("LEMON", 4, 2, 4, 12),  // native fallback — must be chosen instead
    ];
    st.my_trolls = vec![u.clone()];
    let mut plan = base_plan(&st);
    plan.ring = vec![((1, 1), RingRole::Diagonal)];

    assert_eq!(
        missions::fell_target(&st, &plan, &u),
        Some((4, 2)),
        "the diagonal ring cell (1,1) wins on raw efficiency (1333 > 500) but MUST be skipped \
         — it is the protected seed/fruit engine (fell_ok blocks any standing \
         RingRole::Diagonal tree outside liquidation/raid); the native LEMON at (4,2) must be \
         picked instead"
    );
}

#[test]
fn fellmission_ring_protection_lifted_under_liquidation() {
    // Same geometry as above, but under `plan.liquidation` — fell_ok's diagonal-ring guard is
    // explicitly bypassed during the endgame ("fell anything reachable"), so the protected
    // diagonal becomes eligible again and wins on efficiency as raw math would suggest. Proves
    // the C1 filter isn't a blanket ban — it defers to the SAME liquidation/raid escape hatch
    // the champion's own bands use.
    let mut st = base_state();
    let u = chopper(0, 2, 2);
    st.trees = vec![
        tree("BANANA", 1, 1, 4, 2),
        tree("LEMON", 4, 2, 4, 12),
    ];
    st.my_trolls = vec![u.clone()];
    let mut plan = base_plan(&st);
    plan.ring = vec![((1, 1), RingRole::Diagonal)];
    plan.liquidation = true;

    assert_eq!(
        missions::fell_target(&st, &plan, &u),
        Some((1, 1)),
        "under liquidation the diagonal ring guard is lifted (same escape hatch the champion's \
         bands use) — the diagonal's higher raw efficiency should win"
    );
}

// ── Code review Fix C2: assign_resolved must still see the chopper (starter deconfliction) ──

#[test]
fn fellmission_starter_deconfliction_preserved_with_real_starter_spec() {
    missions::reset();
    // Two eligible fell trees (fell_ok && own_half && within_roam under REAL champion consts:
    // chop_r=5, farm_r=2, farm_fell=2, fell_size=2, opp=(13,6)):
    //   Tree A (4,2): starter steps=2/eta=2 (ms=1), chopper steps=2/eta=1 (ms=2) — the BEST
    //     pick for BOTH the starter's chop-help band (40) and the chopper's own fell/mission
    //     target (band 70/efficiency).
    //   Tree B (0,4): starter steps=4/eta=4, chopper steps=8/eta=4 — each one's clearly-worse
    //     fallback.
    // Because the chopper's fell value (band 70, ~6,999,997) always dominates the starter's
    // chop-help value (band 40, ~3,999,994) for the SAME cell (claims_conflict: same-cell
    // Wood-vs-Wood always conflicts), a joint matcher that sees BOTH trolls must award Tree A
    // to the chopper and force the starter onto Tree B (total value 10,999,989, strictly
    // higher than awarding A to the starter: 10,999,988). A matcher that never sees the
    // chopper (the C2 bug: `others` excludes it from `assign_resolved`) lets the starter grab
    // Tree A outright — a DIFFERENT assignment than ringfix3's own joint matcher would ever
    // produce for this roster.
    let mut st = base_state();
    st.trees = vec![
        tree("LEMON", 4, 2, 2, 4), // Tree A: contested — chopper's mission target
        tree("LEMON", 0, 4, 2, 4), // Tree B: each troll's fallback
    ];
    let starter = starter_hand(0, 2, 2);
    let chopper_u = chopper(1, 6, 2);
    st.my_trolls = vec![starter.clone(), chopper_u.clone()];
    let plan = base_plan(&st);

    // planner::reset() clears the STICKY (LAST_TGT) thread-local before EACH independent
    // measurement below — cargo test's worker threads reuse thread_locals across tests, and
    // (more importantly) `resolve_commands` and `assign_resolved` each WRITE LAST_TGT as a
    // side effect (render_assignments(..., update_last_target=true)); without resetting
    // between the two calls, whichever runs SECOND gets a same-cell STICKY bonus (+6) toward
    // whatever the FIRST call already picked — enough to hide the exact conflict this test
    // exists to catch. Both measurements must start from the same blank slate.
    troll_farm::botmain::planner::reset();
    missions::reset();
    let cmds = resolve_commands(&st, &plan, &st.my_trolls);

    // Baseline: a direct, INDEPENDENT assign_resolved call over the FULL roster (chopper
    // included, no mission override at all) — exactly ringfix3's own joint matcher. If
    // resolve_commands truly preserves the starter's ringfix3 assignment, its result for the
    // starter must be byte-identical to this baseline, independent of whatever the mission
    // does to the chopper.
    troll_farm::botmain::planner::reset();
    let baseline = assign_resolved(&st, &plan, &st.my_trolls);
    assert_eq!(
        cmds[&0], baseline[&0],
        "the starter's assignment must be exactly what a full-roster assign_resolved (chopper \
         included, so the joint matcher deconflicts the starter's chop-help claim against the \
         chopper's Wood claim on Tree A) would produce — excluding the chopper from \
         assign_resolved (the C2 bug) lets the starter wrongly grab the tree the chopper's \
         mission needs"
    );
}

// ── Fix C3: banking-crater — a full/endgame chopper must BANK, not be redirected to fell ──
//
// THE BUG: `resolve_commands` unconditionally overwrote the chopper's `assign_resolved`
// command with the FellForWood mission command. The mission only ever emits CHOP/MOVE (it
// has no concept of banking), so whenever the band system's OWN pick for the chopper was
// actually a Bank action (band 80 full->bank, or band 95 endgame-bank-a-partial-load), that
// decision was silently discarded and replaced with "go fell the next tree" — felled wood
// piled up in the chopper's carry forever and was never banked (boss-gate measurement: our
// banked wood == 0 across all 6 games, vs champion ringfix3's ~48).
//
// THE FIX: only let the mission override the chopper's command when the band's own pick is
// NOT itself a bank/endgame action. `u.free_capacity() == 0` is a provably exact detector on
// its own for the full case: `candidates()` always offers band 80 (80*BAND) whenever
// free_capacity()==0, and 80*BAND outranks every fell candidate a chopper can have (<=72*BAND
// plus small offsets, BAND=100_000), so `assign_resolved`'s pick for a full chopper is always
// that Bank candidate. `plan.liquidation` (turns_rem <= GE_LIQ_T) additionally defers for the
// chopper's whole endgame tail — a safe superset of the exact turn band 95 fires (which needs
// `d_home`, not available in `resolve_commands`): whenever band 95 hasn't fired yet inside
// liquidation, `assign_resolved`'s own bands 70/72/30/31 still fell trees, so this only forgoes
// the mission's wood-efficiency PICK for this short (~11%-of-the-game) tail, never a bank
// action for a fell action. A rendered `"DROP "` command is also an unambiguous tell (only
// `Kind::Bank`'s `motion::bank_cmd` ever emits one) kept as a belt-and-braces guard.

#[test]
fn fellmission_full_chopper_banks_not_fells() {
    missions::reset();
    troll_farm::botmain::planner::reset();
    // Chopper is FULL (free_capacity() == 3 - 3 == 0) and stands directly adjacent to the
    // shack (manhattan((1,2),(0,2)) == 1) — assign_resolved's band 80 ("full -> bank",
    // 80*BAND) strictly outranks every fell candidate this chopper has (<=72*BAND, small
    // offsets), so its own pick renders via `motion::bank_cmd` as exactly "DROP 1" — no
    // camp-cell tie-break to hand-verify. An eligible LEMON (size 4 >= fell_size 2, well
    // within base_plan's real chop_r(5)/own_half of the shack) stands nearby so the (buggy)
    // unconditional mission override had somewhere else to send the chopper.
    let mut st = base_state();
    st.trees = vec![tree("LEMON", 4, 2, 4, 12)];
    let mut u = chopper(1, 1, 2); // adjacent to SHACK (0,2): manhattan == 1
    u.carry[WOOD] = 3; // full: free_capacity() == 3 - 3 == 0
    st.my_trolls = vec![u];
    let plan = base_plan(&st);

    let cmds = resolve_commands(&st, &plan, &st.my_trolls);
    assert_eq!(
        cmds[&1], "DROP 1",
        "a FULL chopper (free_capacity() == 0) must bank its carried wood (the band's own \
         DROP), never be redirected by the mission to fell another tree — overriding this \
         stranded every chop of felled wood in carry forever (banked wood stuck at 0)"
    );
}

#[test]
fn fellmission_endgame_banks_partial_load() {
    missions::reset();
    troll_farm::botmain::planner::reset();
    // Chopper carries a PARTIAL load (free_capacity() == 3 - 1 == 2 > 0, so band 80
    // "full->bank" does NOT fire) but the game is in the endgame liquidation window
    // (plan.liquidation, i.e. turns_rem <= GE_LIQ_T): at this geometry — chopper at (2,2),
    // BFS distance 1 from the nearest shack camp cell (1,2), movement_speed 2 — band 95's own
    // trigger is `turns_rem <= e+1` where `e = ceil(d_home/ms) + 1 = ceil(1/2) + 1 = 2`, so
    // turns_rem=3 satisfies `3 <= 3`: band 95 ("bank a carried load in time to score it",
    // 95*BAND) genuinely fires and outranks every fell candidate (<=72*BAND), not merely
    // "liquidation is set". The chopper is deliberately NOT adjacent to the shack (manhattan
    // 2, not 1) so this test exercises ONLY the `plan.liquidation` deferral, isolated from
    // both the free_capacity()==0 and the rendered-"DROP " disjuncts covered by the previous
    // test. The camp cell (1,2) is exactly 1 step away (<= movement_speed 2), so the chopper
    // lands there this turn with no partial-progress tie to hand-verify. An eligible LEMON
    // stands nearby so the (buggy) unconditional mission override had somewhere else to send
    // the chopper instead of banking.
    let mut st = base_state();
    st.trees = vec![tree("LEMON", 4, 2, 4, 12)];
    let mut u = chopper(1, 2, 2);
    u.carry[WOOD] = 1; // partial: free_capacity() == 3 - 1 == 2 > 0
    st.my_trolls = vec![u];
    let mut plan = base_plan(&st);
    plan.turns_rem = 3; // triggers band 95's own e+1(=2+1=3) threshold at this geometry
    plan.liquidation = true; // tactics::plan_impl always sets this exactly when turns_rem <= GE_LIQ_T

    let cmds = resolve_commands(&st, &plan, &st.my_trolls);
    assert_eq!(
        cmds[&1], "MOVE 1 1 2",
        "in the endgame liquidation window a partially-loaded chopper must bank (band 95's \
         MOVE toward the camp cell (1,2)), never be redirected by the mission to fell another \
         tree — a load banked too late scores zero"
    );
}
