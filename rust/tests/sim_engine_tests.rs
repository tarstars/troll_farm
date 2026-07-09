use std::collections::HashMap;
/// Rust ports of tests/test_sim_engine.py
/// Each test corresponds to a Python test case and verifies identical semantics.
use std::collections::HashSet;
use troll_farm::game::engine::{
    apply_chop, apply_drop, apply_harvest, apply_mine, apply_moves, apply_train, next_cell,
    recompute_scores, step, tick_plants, tree_health, IRON, WOOD,
};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{from_ascii, GameState, Plant, Unit};

// ── helpers ───────────────────────────────────────────────────────────────────

/// Build a line of walkable cells from x=0..n-1 at y=0, excluding `blocked`.
fn line(n: i32, blocked: &[(i32, i32)]) -> HashSet<(i32, i32)> {
    let b: HashSet<(i32, i32)> = blocked.iter().copied().collect();
    (0..n).map(|x| (x, 0)).filter(|c| !b.contains(c)).collect()
}

/// Two-unit state: 6x1 corridor, player 0's two units.
fn two_unit_state() -> GameState {
    let mut g = from_ascii(&["0....1"]);
    g.units = vec![
        Unit {
            id: 0,
            player: 0,
            x: 2,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 0,
            carry: [0; 6],
        },
        Unit {
            id: 1,
            player: 0,
            x: 3,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 0,
            carry: [0; 6],
        },
    ];
    g.next_id = 2;
    g
}

// ── tree health fidelity (real arena formula) ──────────────────────────────────

#[test]
fn test_tree_health_matches_real_arena_observations() {
    // Every (type, size, health) ever observed in a real referee replay must
    // round-trip through tree_health (health = base + slope*size).
    let obs = [
        ("PLUM", 1, 6),
        ("PLUM", 2, 8),
        ("PLUM", 3, 10),
        ("PLUM", 4, 12),
        ("LEMON", 2, 8),
        ("LEMON", 4, 12),
        ("APPLE", 1, 11),
        ("APPLE", 3, 17),
        ("BANANA", 3, 5),
        ("BANANA", 4, 6),
    ];
    for (t, size, want) in obs {
        assert_eq!(
            tree_health(t, size),
            want,
            "{} size {} should be {} health",
            t,
            size,
            want
        );
    }
}

#[test]
fn test_mapgen_is_realistic_size_and_tree_density() {
    // Silver-calibrated maps: height 8..=11, width = 2*height, ~18 trees. Guard
    // against regressing to the old sparse 20x10 / ~10-tree maps that under-rewarded
    // wood/chopping. Also every generated tree must carry the real health for its
    // type+size (no hardcoded 6).
    use troll_farm::game::mapgen::dims_for_seed;
    for seed in 0..40u64 {
        let g = generate_bronze(seed);
        let (w, h) = dims_for_seed(seed);
        assert_eq!((g.width, g.height), (w, h), "seed {} wrong dims", seed);
        assert!(
            (8..=11).contains(&h) && w == 2 * h,
            "seed {}: dims {}x{} out of Silver range",
            seed,
            w,
            h
        );
        assert!(
            g.plants.len() >= 10 && g.plants.len() <= 30,
            "seed {}: {} trees outside Silver density (~18)",
            seed,
            g.plants.len()
        );
        for p in &g.plants {
            assert_eq!(
                p.health,
                tree_health(&p.plant_type, p.size),
                "seed {}: {} size {} has health {} (want {})",
                seed,
                p.plant_type,
                p.size,
                p.health,
                tree_health(&p.plant_type, p.size)
            );
        }
    }
}

#[test]
fn test_generate_bronze_is_deterministic_across_processes() {
    // generate_bronze must NOT depend on HashSet iteration order (randomized per
    // process). Before the fix it built candidate-cell lists by iterating
    // `walkable` directly, so the seeded RNG picked different cells each run and
    // every tournament/diag measurement was irreproducible. This golden signature
    // for seed 0 is stable run-to-run; if it drifts, determinism regressed (or the
    // mapgen algorithm changed deliberately -- then update this string).
    let g = generate_bronze(0);
    let mut plants: Vec<String> = g
        .plants
        .iter()
        .map(|p| format!("{}@{},{}:s{}h{}", p.plant_type, p.x, p.y, p.size, p.health))
        .collect();
    plants.sort();
    let sig = format!(
        "{}x{} {:?} iron{} water{} | {}",
        g.width,
        g.height,
        g.shacks,
        g.iron.len(),
        g.water.len(),
        plants.join(" ")
    );
    let expected = "22x11 [(1, 10), (20, 0)] iron4 water6 | \
APPLE@12,3:s4h20 APPLE@13,1:s4h20 APPLE@14,8:s1h11 APPLE@7,2:s1h11 APPLE@8,9:s4h20 APPLE@9,7:s4h20 \
BANANA@14,10:s4h6 BANANA@18,3:s4h6 BANANA@3,7:s4h6 BANANA@7,0:s4h6 \
LEMON@0,5:s1h6 LEMON@16,3:s4h12 LEMON@17,9:s3h10 LEMON@21,5:s1h6 LEMON@4,1:s3h10 LEMON@5,7:s4h12 \
PLUM@0,10:s4h12 PLUM@12,8:s4h12 PLUM@12,9:s4h12 PLUM@21,0:s4h12 PLUM@9,1:s4h12 PLUM@9,2:s4h12";
    assert_eq!(
        sig, expected,
        "generate_bronze(0) drifted -- determinism regressed?"
    );
}

// ── tick_plants ───────────────────────────────────────────────────────────────

#[test]
fn test_tick_plants_grows_then_produces() {
    let mut g = from_ascii(&["....", "0..1"]);
    // PLUM at full size (4), health 4, 2 fruits, cooldown 1
    // After tick: cd 1->0, already at max size, fruits < MAX_FRUITS (3), so fruits++ -> 3, cd resets to 8
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 1,
        y: 0,
        size: 4,
        health: 4,
        fruits: 2,
        cooldown: 1,
    }];
    tick_plants(&mut g);
    let p = &g.plants[0];
    assert_eq!(p.fruits, 3, "expected 3 fruits");
    assert_eq!(p.cooldown, 8, "expected cooldown 8");
}

#[test]
fn test_tick_plants_growing_tree_increases_size_no_fruit() {
    let mut g = from_ascii(&["....", "0..1"]);
    // BANANA at size 2, health 6, 0 fruits, cooldown 1
    // After tick: cd->0, size<MAX_SIZE -> size++ to 3, cd resets to 6
    g.plants = vec![Plant {
        plant_type: "BANANA".to_string(),
        x: 2,
        y: 0,
        size: 2,
        health: 6,
        fruits: 0,
        cooldown: 1,
    }];
    tick_plants(&mut g);
    assert_eq!(g.plants[0].size, 3);
    assert_eq!(g.plants[0].fruits, 0);
}

// ── recompute_scores ──────────────────────────────────────────────────────────

#[test]
fn test_recompute_scores_counts_only_fruit() {
    let mut g = from_ascii(&["....", "0..1"]);
    // [PLUM=3, LEMON=2, APPLE=1, BANANA=4, IRON=9, WOOD=0]
    // score = 3+2+1+4 + 4*0 = 10 (iron and wood don't score as fruit; WOOD scores 4*0=0)
    g.inventories[0] = [3, 2, 1, 4, 9, 0];
    recompute_scores(&mut g);
    assert_eq!(g.scores[0], 10);
}

// ── next_cell ─────────────────────────────────────────────────────────────────

#[test]
fn test_next_cell_direct_when_in_range() {
    let w = line(6, &[(0, 0)]);
    // target (5,0) is 2 away from (3,0), speed=2 -> go directly
    assert_eq!(next_cell(&w, (3, 0), (5, 0), 2), (5, 0));
}

#[test]
fn test_next_cell_steps_toward_far_target() {
    let w = line(6, &[(0, 0)]);
    // from (1,0) to (5,0), speed 1 -> one step to (2,0)
    assert_eq!(next_cell(&w, (1, 0), (5, 0), 1), (2, 0));
}

#[test]
fn test_next_cell_routes_to_nearest_reachable_when_unreachable() {
    // (0,0) is a shack cell (not in walkable), target is (0,0)
    let w = line(6, &[(0, 0)]);
    // from (3,0) with speed 1, aim toward (0,0) which is unreachable -> step toward it -> (2,0)
    assert_eq!(next_cell(&w, (3, 0), (0, 0), 1), (2, 0));
}

// ── apply_moves ───────────────────────────────────────────────────────────────

#[test]
fn test_two_movers_take_distinct_cells() {
    let mut g = two_unit_state();
    // Both want (5,0) — should end up on distinct cells (no overlap)
    let mut intents = HashMap::new();
    intents.insert(0, (5, 0));
    intents.insert(1, (5, 0));
    apply_moves(&mut g, &intents);
    let cells: Vec<(i32, i32)> = g.units.iter().map(|u| u.pos()).collect();
    // No two units on the same cell
    let unique: HashSet<(i32, i32)> = cells.iter().copied().collect();
    assert_eq!(unique.len(), 2, "units should not overlap: {:?}", cells);
}

#[test]
fn test_unit_blocked_by_stationary_teammate_stays_put() {
    let mut g = two_unit_state();
    g.units[0].x = 2;
    g.units[0].y = 0; // stationary on (2,0)
    g.units[1].x = 1;
    g.units[1].y = 0; // mover at (1,0)
    let mut intents = HashMap::new();
    intents.insert(1, (2, 0)); // wants to move to occupied cell
    apply_moves(&mut g, &intents);
    assert_eq!(g.units[0].pos(), (2, 0));
    assert_eq!(g.units[1].pos(), (1, 0)); // blocked, stays
}

#[test]
fn test_higher_id_wins_contested_cell() {
    let mut g = two_unit_state();
    g.units[0].x = 1;
    g.units[0].y = 0; // unit 0 at (1,0)
    g.units[1].x = 3;
    g.units[1].y = 0; // unit 1 at (3,0)
    let mut intents = HashMap::new();
    intents.insert(0, (2, 0));
    intents.insert(1, (2, 0)); // both want (2,0); higher id=1 wins
    apply_moves(&mut g, &intents);
    assert_eq!(g.units[1].pos(), (2, 0), "unit 1 (higher id) should win");
    assert_eq!(g.units[0].pos(), (1, 0), "unit 0 (lower id) should stay");
}

// ── apply_harvest ─────────────────────────────────────────────────────────────

#[test]
fn test_harvest_takes_one_fruit_for_capacity_one_troll() {
    let mut g = from_ascii(&["0....1"]);
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 1,
        hp: 1,
        chop: 0,
        carry: [0; 6],
    }];
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 1,
        y: 0,
        size: 4,
        health: 4,
        fruits: 3,
        cooldown: 5,
    }];
    apply_harvest(&mut g, &[0]);
    assert_eq!(g.units[0].carry[0], 1, "troll should carry 1 PLUM");
    assert_eq!(g.plants[0].fruits, 2, "plant should have 2 fruits left");
}

#[test]
fn test_last_fruit_duplicates_across_two_trolls() {
    let mut g = from_ascii(&["0....1"]);
    // Two trolls on same cell, plant has only 1 fruit
    g.units = vec![
        Unit {
            id: 0,
            player: 0,
            x: 1,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 0,
            carry: [0; 6],
        },
        Unit {
            id: 9,
            player: 1,
            x: 1,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 0,
            carry: [0; 6],
        },
    ];
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 1,
        y: 0,
        size: 4,
        health: 4,
        fruits: 1,
        cooldown: 5,
    }];
    apply_harvest(&mut g, &[0, 9]);
    assert_eq!(g.units[0].carry[0], 1, "unit 0 should get 1 PLUM");
    assert_eq!(
        g.units[1].carry[0], 1,
        "unit 9 should also get 1 PLUM (duplication)"
    );
    assert_eq!(g.plants[0].fruits, 0, "plant should have 0 fruits");
}

// ── apply_drop ────────────────────────────────────────────────────────────────

#[test]
fn test_drop_moves_carry_to_inventory_when_next_to_shack() {
    let mut g = from_ascii(&["0....1"]);
    // unit at (1,0) which is adjacent to shack (0,0)
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 9,
        hp: 1,
        chop: 0,
        carry: [2, 0, 1, 0, 0, 0],
    }];
    apply_drop(&mut g, &[0]);
    assert_eq!(g.inventories[0][0], 2); // PLUM
    assert_eq!(g.inventories[0][2], 1); // APPLE
    assert_eq!(g.units[0].total(), 0); // carry cleared
}

// ── apply_train ───────────────────────────────────────────────────────────────

#[test]
fn test_train_costs_and_spawns_on_shack() {
    let mut g = from_ascii(&["0....1"]);
    // Keep only player 0 unit, move it off the shack
    g.units = vec![g.units[0].clone()];
    g.next_id = 1;
    g.units[0].x = 2;
    g.units[0].y = 0;
    g.inventories[0] = [5, 5, 5, 5, 0, 0];
    // n=1, talents=(1,1,1,0): cost = [1+1, 1+1, 1+1, 1+0] = [2,2,2,1] for slots 0,1,2,3
    apply_train(&mut g, 0, (1, 1, 1, 0));
    assert_eq!(g.inventories[0][0], 3); // 5 - 2
    assert_eq!(g.inventories[0][1], 3);
    assert_eq!(g.inventories[0][2], 3);
    let spawned: Vec<&Unit> = g.units.iter().filter(|u| u.id == 1).collect();
    assert!(!spawned.is_empty(), "new unit should have been spawned");
    assert_eq!(spawned[0].pos(), g.shacks[0], "new unit should be at shack");
}

#[test]
fn test_train_blocked_when_shack_occupied() {
    let mut g = from_ascii(&["0....1"]);
    // unit 0 is at shack (0,0) — shack occupied
    g.inventories[0] = [5, 5, 5, 5, 0, 0];
    apply_train(&mut g, 0, (1, 1, 1, 0));
    assert_eq!(
        g.units.len(),
        2,
        "no new unit should be spawned when shack is occupied"
    );
}

// ── step priority ─────────────────────────────────────────────────────────────

#[test]
fn test_step_moves_then_harvests_in_priority_order() {
    let mut g = from_ascii(&["0....1"]);
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 1,
        hp: 1,
        chop: 0,
        carry: [0; 6],
    }];
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 2,
        y: 0,
        size: 4,
        health: 4,
        fruits: 3,
        cooldown: 5,
    }];

    // Turn 1: move onto the plant
    step(&mut g, &["MOVE 0 2 0".to_string()], &[]);
    assert_eq!(g.units[0].pos(), (2, 0));
    assert_eq!(g.turn, 2);

    // Turn 2: harvest
    step(&mut g, &["HARVEST 0".to_string()], &[]);
    assert_eq!(g.units[0].carry[0], 1, "should have harvested 1 PLUM");
}

#[test]
fn test_step_ignores_msg_and_wait_and_advances_turn() {
    let mut g = from_ascii(&["0....1"]);
    step(
        &mut g,
        &["MSG hi".to_string(), "WAIT".to_string()],
        &["WAIT".to_string()],
    );
    assert_eq!(g.turn, 2);
}

// ── apply_chop ────────────────────────────────────────────────────────────────

#[test]
fn test_apply_chop_fells_tree_and_collects_wood_eq_size() {
    let mut g = from_ascii(&["0....1"]);
    // chop power 3, cc 4; plant size 4, health 3
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 4,
        hp: 0,
        chop: 3,
        carry: [0; 6],
    }];
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 1,
        y: 0,
        size: 4,
        health: 3,
        fruits: 0,
        cooldown: 5,
    }];
    apply_chop(&mut g, &[0]);
    assert!(g.plants.is_empty(), "tree should be felled");
    // wood collected == size (4), but limited by cc (4) — all 4 fit
    assert_eq!(g.units[0].carry[WOOD], 4);
}

#[test]
fn test_apply_chop_only_damages_a_healthy_tree() {
    let mut g = from_ascii(&["0....1"]);
    // chop power 2, health 10 — not killed
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 4,
        hp: 0,
        chop: 2,
        carry: [0; 6],
    }];
    g.plants = vec![Plant {
        plant_type: "PLUM".to_string(),
        x: 1,
        y: 0,
        size: 4,
        health: 10,
        fruits: 0,
        cooldown: 5,
    }];
    apply_chop(&mut g, &[0]);
    assert_eq!(
        g.plants[0].health, 8,
        "health should be reduced by chop power"
    );
    assert_eq!(
        g.units[0].carry[WOOD], 0,
        "no wood collected from living tree"
    );
}

// ── apply_mine ────────────────────────────────────────────────────────────────

#[test]
fn test_apply_mine_gains_iron_when_adjacent() {
    let mut g = from_ascii(&["0....1", "......"]);
    g.iron = {
        let mut s = std::collections::HashSet::new();
        s.insert((1i32, 1i32));
        s
    };
    // unit at (1,0): adjacent to iron at (1,1) (Manhattan distance 1)
    // chop power 3, free capacity 5
    g.units = vec![Unit {
        id: 0,
        player: 0,
        x: 1,
        y: 0,
        ms: 1,
        cc: 5,
        hp: 0,
        chop: 3,
        carry: [0; 6],
    }];
    apply_mine(&mut g, &[0]);
    // gains min(chop=3, free=5) = 3 iron
    assert_eq!(g.units[0].carry[IRON], 3);
}

// ── from_ascii ────────────────────────────────────────────────────────────────

#[test]
fn test_from_ascii_basic() {
    let g = from_ascii(&["0....1"]);
    assert_eq!(g.width, 6);
    assert_eq!(g.height, 1);
    assert_eq!(g.shacks[0], (0, 0));
    assert_eq!(g.shacks[1], (5, 0));
    // cells 1..4 are walkable
    assert!(g.walkable.contains(&(1, 0)));
    assert!(g.walkable.contains(&(4, 0)));
    // shack cells are NOT in walkable (Python semantics)
    assert!(!g.walkable.contains(&(0, 0)));
    assert!(!g.walkable.contains(&(5, 0)));
    assert_eq!(g.units.len(), 2);
    assert_eq!(g.units[0].pos(), (0, 0));
    assert_eq!(g.units[1].pos(), (5, 0));
}

#[test]
fn test_from_ascii_iron_and_water() {
    let g = from_ascii(&["0+~1"]);
    assert!(g.iron.contains(&(1, 0)));
    assert!(g.water.contains(&(2, 0)));
    // iron and water cells should NOT be in walkable
    assert!(!g.walkable.contains(&(1, 0)));
    assert!(!g.walkable.contains(&(2, 0)));
}

// ── generate_bronze smoke test ────────────────────────────────────────────────

#[test]
fn test_generate_bronze_valid_symmetric_map() {
    let g = generate_bronze(0);
    let (w, h) = (g.width, g.height);
    let mir = |c: (i32, i32)| (w - 1 - c.0, h - 1 - c.1);

    // Dimensions (Silver-calibrated: seed 0 -> 22x11 = height 11, width 2*height)
    assert_eq!((g.width, g.height), (22, 11));

    // Two distinct shacks mirrored
    let s0 = g.shacks[0];
    let s1 = g.shacks[1];
    assert_ne!(s0, s1);
    assert_eq!(mir(s0), s1); // mirror check

    // Two starting units with chop=1
    assert_eq!(g.units.len(), 2);
    assert!(g.units.iter().all(|u| u.chop == 1));
    assert_eq!(g.units[0].pos(), s0);
    assert_eq!(g.units[1].pos(), s1);

    // Inventories equal (symmetric start) and include iron
    assert_eq!(g.inventories[0], g.inventories[1]);
    assert!(g.inventories[0][IRON] >= 2 && g.inventories[0][IRON] <= 10);

    // At least one fruit on the map
    assert!(
        g.plants.iter().any(|p| p.fruits > 0),
        "at least one plant should have fruit"
    );

    // Iron and water are mirrored pairs
    for &ic in &g.iron {
        let m = mir(ic);
        assert!(
            g.iron.contains(&m),
            "iron cell {:?} should have mirror {:?}",
            ic,
            m
        );
    }
    for &wc in &g.water {
        let m = mir(wc);
        assert!(
            g.water.contains(&m),
            "water cell {:?} should have mirror {:?}",
            wc,
            m
        );
    }

    // Count of iron/water pairs
    assert_eq!(g.iron.len(), 4, "expected 2 pairs = 4 iron cells");
    assert_eq!(g.water.len(), 6, "expected 3 pairs = 6 water cells");

    // Plants are mirrored
    for p in &g.plants {
        let m = mir(p.pos());
        assert!(
            g.plants
                .iter()
                .any(|q| q.pos() == m && q.plant_type == p.plant_type),
            "plant at {:?} should have mirror",
            p.pos()
        );
    }
}

#[test]
fn test_generate_bronze_deterministic() {
    let g1 = generate_bronze(42);
    let g2 = generate_bronze(42);
    assert_eq!(g1.shacks, g2.shacks);
    assert_eq!(g1.inventories, g2.inventories);
    assert_eq!(g1.plants.len(), g2.plants.len());
}
