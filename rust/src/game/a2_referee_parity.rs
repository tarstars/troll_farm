//! Isolated referee-parity substrate for Architecture-2.
//!
//! Historical experiments keep using `engine` and `official_mapgen` unchanged. This
//! module preserves the post-map SHA1PRNG state and mirrors the referee's x-major/y-minor
//! movement candidate ordering.

use super::engine::bfs_distances;
use super::state::{Cell, GameState};
use std::collections::{HashMap, HashSet};

use super::a2_continued_mapgen::{generate_official_with_rng, Sha1Prng};

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct MovementRngStats {
    pub draws: u64,
    pub tied_draws: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MoveSelection {
    pub cell: Cell,
    pub candidate_count: usize,
    pub drew_rng: bool,
}

#[derive(Clone, Debug)]
pub struct RefereeGame {
    pub game: GameState,
    random: Sha1Prng,
    pub movement_rng: MovementRngStats,
}

pub fn generate_official(seed: i64) -> RefereeGame {
    let (game, random) = generate_official_with_rng(seed);
    RefereeGame {
        game,
        random,
        movement_rng: MovementRngStats::default(),
    }
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// Source-shaped `Board.getNextCell`.
///
/// The direct-target fast path consumes no RNG. Every other selection calls
/// `nextInt(closest.size())`, including `nextInt(1)`.
pub fn select_next_cell(
    referee: &mut RefereeGame,
    current: Cell,
    target: Cell,
    speed: i32,
) -> MoveSelection {
    let game = &referee.game;
    let source_dist = bfs_distances(&game.walkable, &[current]);
    let mut target_dist = bfs_distances(&game.walkable, &[target]);

    if source_dist.get(&target).is_some_and(|distance| *distance <= speed) {
        return MoveSelection {
            cell: target,
            candidate_count: 1,
            drew_rng: false,
        };
    }

    if !source_dist.contains_key(&target) {
        let best = source_dist
            .keys()
            .map(|cell| manhattan(target, *cell))
            .min()
            .expect("current cell is always a BFS source");
        let mut closest_to_target = Vec::new();
        for x in 0..game.width {
            for y in 0..game.height {
                let cell = (x, y);
                if source_dist.contains_key(&cell) && manhattan(target, cell) == best {
                    closest_to_target.push(cell);
                }
            }
        }
        target_dist = bfs_distances(&game.walkable, &closest_to_target);
    }

    let mut closest = Vec::new();
    let mut best = game.width * game.height;
    for x in 0..game.width {
        for y in 0..game.height {
            let cell = (x, y);
            let Some(&source) = source_dist.get(&cell) else {
                continue;
            };
            if source > speed {
                continue;
            }
            let Some(&remaining) = target_dist.get(&cell) else {
                continue;
            };
            if remaining < best {
                best = remaining;
                closest.clear();
            }
            if remaining == best {
                closest.push(cell);
            }
        }
    }

    assert!(!closest.is_empty(), "referee movement candidate set is non-empty");
    let index = referee.random.next_int(closest.len() as i32) as usize;
    referee.movement_rng.draws += 1;
    if closest.len() > 1 {
        referee.movement_rng.tied_draws += 1;
    }
    MoveSelection {
        cell: closest[index],
        candidate_count: closest.len(),
        drew_rng: true,
    }
}

/// Apply already-resolved movement targets using `MoveTask.apply` collision semantics.
///
/// Movement targets must be resolved, in command parse order, with [`select_next_cell`]
/// before this function is called.
pub fn apply_resolved_moves(game: &mut GameState, intents: &HashMap<i32, Cell>) -> Vec<i32> {
    let mut blocked = Vec::new();
    for player in 0..2i32 {
        let player_unit_ids: Vec<i32> = game
            .units
            .iter()
            .filter(|unit| unit.player == player)
            .map(|unit| unit.id)
            .collect();
        let initial_positions: HashMap<i32, Cell> = game
            .units
            .iter()
            .filter(|unit| unit.player == player)
            .map(|unit| (unit.id, unit.pos()))
            .collect();
        let target: HashMap<i32, Cell> = player_unit_ids
            .iter()
            .map(|unit_id| {
                (
                    *unit_id,
                    intents
                        .get(unit_id)
                        .copied()
                        .unwrap_or(initial_positions[unit_id]),
                )
            })
            .collect();

        let mut occupied: HashSet<Cell> = player_unit_ids
            .iter()
            .map(|unit_id| initial_positions[unit_id])
            .collect();
        let mut movers: Vec<i32> = player_unit_ids
            .iter()
            .filter(|unit_id| target[unit_id] != initial_positions[unit_id])
            .copied()
            .collect();
        movers.sort_by(|left, right| right.cmp(left));

        let mut progress = true;
        let mut resolve_blocking = false;
        while progress {
            progress = false;
            let mut frequency: HashMap<Cell, i32> = HashMap::new();
            for unit_id in &movers {
                *frequency.entry(target[unit_id]).or_insert(0) += 1;
            }

            let mut moved = Vec::new();
            for unit_id in &movers {
                let destination = target[unit_id];
                let current = game
                    .units
                    .iter()
                    .find(|unit| unit.id == *unit_id)
                    .expect("known mover")
                    .pos();
                if (resolve_blocking || frequency[&destination] == 1)
                    && !occupied.contains(&destination)
                {
                    occupied.remove(&current);
                    occupied.insert(destination);
                    let unit = game
                        .units
                        .iter_mut()
                        .find(|unit| unit.id == *unit_id)
                        .expect("known mover");
                    unit.x = destination.0;
                    unit.y = destination.1;
                    moved.push(*unit_id);
                    progress = true;
                    resolve_blocking = false;
                }
            }
            movers.retain(|unit_id| !moved.contains(unit_id));
            if progress {
                continue;
            }

            let mover_at: HashMap<Cell, i32> = movers
                .iter()
                .map(|unit_id| {
                    let position = game
                        .units
                        .iter()
                        .find(|unit| unit.id == *unit_id)
                        .expect("known mover")
                        .pos();
                    (position, *unit_id)
                })
                .collect();
            let mut swap_resolved = false;
            'outer: for start in &movers {
                let mut path = vec![*start];
                loop {
                    let destination = target[path.last().expect("non-empty path")];
                    let Some(next) = mover_at.get(&destination).copied() else {
                        break;
                    };
                    if next == path[0] {
                        for unit_id in &path {
                            let destination = target[unit_id];
                            let unit = game
                                .units
                                .iter_mut()
                                .find(|unit| unit.id == *unit_id)
                                .expect("known mover");
                            unit.x = destination.0;
                            unit.y = destination.1;
                        }
                        movers.retain(|unit_id| !path.contains(unit_id));
                        progress = true;
                        swap_resolved = true;
                        break 'outer;
                    }
                    if path.contains(&next) {
                        break;
                    }
                    path.push(next);
                }
            }
            if !swap_resolved && !resolve_blocking {
                resolve_blocking = true;
                progress = true;
            }
        }
        blocked.extend(movers);
    }
    blocked
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::official_mapgen;
    use crate::game::state::from_ascii;

    fn assert_same_state(left: &GameState, right: &GameState) {
        assert_eq!(left.width, right.width);
        assert_eq!(left.height, right.height);
        assert_eq!(left.walkable, right.walkable);
        assert_eq!(left.shacks, right.shacks);
        assert_eq!(left.inventories, right.inventories);
        assert_eq!(left.units, right.units);
        assert_eq!(left.plants, right.plants);
        assert_eq!(left.scores, right.scores);
        assert_eq!(left.turn, right.turn);
        assert_eq!(left.next_id, right.next_id);
        assert_eq!(left.iron, right.iron);
        assert_eq!(left.water, right.water);
    }

    #[test]
    fn continued_generator_is_field_identical_for_1024_seeds() {
        for seed in 9_900_000..9_901_024 {
            let continued = generate_official(seed);
            let historical = official_mapgen::generate_official(seed);
            assert_same_state(&continued.game, &historical);
        }
    }

    #[test]
    fn direct_target_consumes_no_rng() {
        let mut referee = generate_official(9_900_001);
        referee.game = from_ascii(&["0..1"]);
        let selected = select_next_cell(&mut referee, (0, 0), (1, 0), 1);
        assert_eq!(selected.cell, (1, 0));
        assert!(!selected.drew_rng);
        assert_eq!(referee.movement_rng, MovementRngStats::default());
    }

    #[test]
    fn unique_non_direct_target_consumes_bound_one_draw() {
        let mut referee = generate_official(9_900_002);
        referee.game = from_ascii(&["0..1"]);
        let selected = select_next_cell(&mut referee, (0, 0), (2, 0), 1);
        assert_eq!(selected.cell, (1, 0));
        assert_eq!(selected.candidate_count, 1);
        assert!(selected.drew_rng);
        assert_eq!(
            referee.movement_rng,
            MovementRngStats {
                draws: 1,
                tied_draws: 0,
            }
        );
    }

    #[test]
    fn tied_candidates_follow_referee_x_major_y_minor_order() {
        let mut referee = generate_official(9_900_003);
        referee.game = from_ascii(&["0..", "...", "..1"]);
        let selected = select_next_cell(&mut referee, (0, 0), (2, 2), 1);
        assert!(selected.cell == (0, 1) || selected.cell == (1, 0));
        assert_eq!(selected.candidate_count, 2);
        assert_eq!(
            referee.movement_rng,
            MovementRngStats {
                draws: 1,
                tied_draws: 1,
            }
        );
    }
}
