//! E1: port of the referee's `hasStalled` end-of-game rule (engine/Board.java, v1.0.5).
//! Verified verbatim against the real referee source (github.com/eulerscheZahl/Troll-Farm,
//! src/main/java/engine/Board.java lines 409-436) — see the task report for the fetch.
use std::collections::HashSet;
use troll_farm::game::engine::has_stalled;
use troll_farm::game::state::{Cell, GameState, Plant, Unit};

/// A 6x4 all-walkable map (every cell, including the shack cells, is walkable — the
/// shack's own walkability never affects `has_stalled`'s BFS: it is always used purely
/// as a seed cell, exactly like the referee's `getDistances`). Shacks (0,1)/(5,2), empty
/// inventories/scores, no plants, one unit per player at a shack-adjacent cell, carry
/// all zeros. (Field shape copied from `game::state::from_ascii_with_talents`'s
/// `GameState { ... }` literal.)
fn base_state() -> GameState {
    let mut walkable: HashSet<Cell> = HashSet::new();
    for x in 0..6 {
        for y in 0..4 {
            walkable.insert((x, y));
        }
    }
    GameState {
        width: 6,
        height: 4,
        walkable,
        shacks: [(0, 1), (5, 2)],
        inventories: [[0; 6]; 2],
        units: vec![
            Unit {
                id: 0,
                player: 0,
                x: 1,
                y: 1,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 0,
                carry: [0; 6],
            },
            Unit {
                id: 1,
                player: 1,
                x: 4,
                y: 2,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 0,
                carry: [0; 6],
            },
        ],
        plants: Vec::new(),
        scores: [0, 0],
        turn: 1,
        next_id: 2,
        iron: HashSet::new(),
        water: HashSet::new(),
    }
}

/// Add a fresh (fruitless, undamaged) plant at (x, y). Type/size/health are irrelevant
/// to `has_stalled` — it only cares whether a plant occupies the cell a unit stands on.
fn put_plant(g: &mut GameState, x: i32, y: i32) {
    g.plants.push(Plant {
        plant_type: "BANANA".to_string(),
        x,
        y,
        size: 1,
        health: 3,
        fruits: 0,
        cooldown: 0,
    });
}

/// Move the unit at `idx` (0 = player 0's unit, 1 = player 1's unit, per `base_state`) to `pos`.
fn move_unit(g: &mut GameState, idx: usize, pos: Cell) {
    g.units[idx].x = pos.0;
    g.units[idx].y = pos.1;
}

#[test]
fn ends_immediately_when_no_plants_no_grace_no_resources() {
    let g = base_state();
    let mut tue = 0;
    assert!(has_stalled(&g, &mut tue)); // 0 -> -1 <= 0, both stuck
}

#[test]
fn plants_reset_grace_from_unit_standing_on_plant() {
    let mut g = base_state();
    // plant at (3,2); OUR unit standing on it; own shack (0,1): BFS dist (3,2)->(0,1)-adj...
    // use a straight-line map so dist = manhattan = 4; ms=1 -> grace = 4/1 + 6 = 10
    put_plant(&mut g, 3, 2);
    move_unit(&mut g, 0, (3, 2));
    let mut tue = 0;
    assert!(!has_stalled(&g, &mut tue));
    assert_eq!(tue, 10);
    // Now the plant dies: grace counts down, game survives 9 more checks. Give both
    // players a token banked resource so NEITHER is "stuck" here — verified against the
    // real referee (Board.java hasStalled): playerStuck is recomputed UNCONDITIONALLY on
    // every no-plants call, not gated on turnsUntilEnd's value, so base_state()'s default
    // zero carry/zero bank would otherwise trip the independent "both stuck" end on the
    // very next call, before the counter ever got a chance to count down. This isolates
    // the counter-decrement mechanic under test here; the stuck/mercy rule itself is
    // covered by the two tests below.
    g.plants.clear();
    g.inventories[0][0] = 1;
    g.inventories[1][0] = 1;
    for expect_alive in [true; 9] {
        assert_eq!(!has_stalled(&g, &mut tue), expect_alive);
    }
    assert!(has_stalled(&g, &mut tue)); // 10th check: 0 -> end
}

#[test]
fn banked_fruit_keeps_a_player_unstuck_but_mercy_rule_ends_a_losing_stuck_player() {
    let mut g = base_state();
    let mut tue = 5;
    g.inventories[0][3] = 2; // we bank 2 bananas -> not stuck
    g.scores[0] = 2;
    g.scores[1] = 0; // opponent stuck AND losing -> mercy end
    assert!(has_stalled(&g, &mut tue));
    // but if the stuck opponent is WINNING, game continues (they just wait it out)
    let mut tue2 = 5;
    g.scores[1] = 10;
    assert!(!has_stalled(&g, &mut tue2));
}

#[test]
fn carried_non_iron_keeps_unstuck_carried_iron_does_not() {
    let mut g = base_state();
    let mut tue = 5;
    g.units[0].carry[4] = 2; // iron only -> still stuck
    g.scores[0] = 0;
    g.scores[1] = 0; // both stuck, tie -> end
    assert!(has_stalled(&g, &mut tue));
    let mut g2 = base_state();
    let mut tue2 = 5;
    g2.units[0].carry[5] = 1; // wood in carry -> not stuck (non-iron item)
    assert!(!has_stalled(&g2, &mut tue2));
}
