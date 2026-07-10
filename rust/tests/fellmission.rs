//! FellForWood mission tests (v1.60.0-fellmission): the wrong-tree fix (pick the reachable
//! tree by wood EFFICIENCY, not the nearest tanky one), commitment (no abandon/backtrack),
//! and the decide_elite wiring (the chopper runs the mission and is excluded from the band
//! system; everyone else's bands are untouched; the joint move solver still resolves
//! everyone's movement together). See
//! docs/superpowers/plans/2026-07-10-fellmission.md and
//! docs/superpowers/specs/2026-07-10-intent-missions-design.md.
use std::collections::HashSet;
use troll_farm::botmain::{missions, State, Tree, Troll};

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
    assert_eq!(
        missions::fell_target(&st, &u),
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
    assert_eq!(
        missions::fell_target(&st, &u),
        Some((7, 0)),
        "the banana is doomed (enemy fells it before our ETA) — fell_target must skip it and \
         fall back to the lemon, not the tanky apple"
    );
}
