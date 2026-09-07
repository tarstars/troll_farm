// Observed productive-source ledger (SERVICED-SOURCE-PROTOCOL-2026-09-05).
//
// This module only *remembers*. It never chooses a unit, never runs BFS territory tests, never
// simulates a turn and never reads an opponent command: it turns consecutive real observed states
// into (turn, amount) fruit-service records and converts a record set into a denied-fruit figure.
// V439's existing opponent-crop memory, its 100/200 target priorities and its scarce-type bonus are
// untouched; this is an additional, independently falsifiable observation, not a replacement.
//
// HARVEST proof. The referee grants fruit to a unit standing *on* the plant cell; PICK grants
// exactly one banked item to a unit within manhattan one of its own shack; MINE yields IRON and
// iron cells are never walkable, so they are never plant cells. Off a shack, therefore, a same-kind
// cargo increase for an enemy unit that stood on a retained, living, same-kind tree in both views
// can only be a harvest, and no fruit-count reasoning is needed.
//
// On a shack-adjacent source PICK can mimic that signature exactly, and per-unit fruit matching is
// not enough: two enemy units may share the cell, so one may PICK while the other harvests, and the
// tree's decrease then "explains" the picker. Bank deltas cannot separate them because both actors
// spend the bank in the same phase. This ledger instead requires whole-cell conservation: the sum
// of same-kind cargo gains of *every* enemy unit on the source must not exceed the tree's observed
// fruit decrease, and any unit on the source without a predecessor voids the turn. Any extra PICK
// breaks the inequality. Growth (at most +1) and last-fruit duplication also break it, so those
// turns are dropped; this direction loses services but can never manufacture one, and it needs no
// growth model.

use crate::candidate::game::nav::{manhattan, ortho_neighbors};
use crate::candidate::game::rules::effective_cooldown;
use crate::candidate::game::types::{Cell, GameState, Plant, PlantKind, Stock, Unit, ITEM_COUNT};

/// A service on turn `t` is retained for a view of turn `v` exactly while `v - WINDOW <= t < v`.
pub const WINDOW: i32 = 12;
/// One past the last playable turn: turn 300 is the last turn that can bank anything.
pub const DEADLINE: i32 = 301;
/// Distinct service turns required before a source is credited at all.
const MIN_SERVICE_TURNS: usize = 2;

struct UnitMemo {
    player: usize,
    cell: Cell,
    carry: Stock,
    harvest_power: i32,
}

struct PlantMemo {
    kind: PlantKind,
    fruits: i32,
    health: i32,
}

/// The minimum previous state a transition needs: units and plants, never the map.
struct Snapshot {
    turn: i32,
    units: Vec<(i32, UnitMemo)>,
    plants: Vec<(Cell, PlantMemo)>,
}

impl Snapshot {
    fn unit(&self, id: i32) -> Option<&UnitMemo> {
        self.units.iter().find(|(other, _)| *other == id).map(|(_, memo)| memo)
    }

    fn plant(&self, cell: Cell) -> Option<&PlantMemo> {
        self.plants.iter().find(|(other, _)| *other == cell).map(|(_, memo)| memo)
    }
}

/// Observed productive fruit sources. Sizes are bounded by the board and by WINDOW.
pub struct Ledger {
    previous: Option<Snapshot>,
    /// Retained (turn, amount) services per source cell, ascending by turn.
    events: Vec<(Cell, Vec<(i32, i32)>)>,
    /// Cells whose current plant was born from our own seed, or ambiguously ours; never credited.
    own: Vec<Cell>,
}

impl Ledger {
    pub fn new() -> Self {
        Self {
            previous: None,
            events: Vec::new(),
            own: Vec::new(),
        }
    }

    /// Fold one real observed state in. Only a strict successor transition can create a service:
    /// a repeated view is idempotent, and any gap or restart drops the observation history.
    #[inline(never)]
    pub fn observe(&mut self, view: &GameState) {
        let current = Self::snapshot(view);
        match self.previous.take() {
            Some(previous) if previous.turn == view.turn => {
                self.previous = Some(previous);
                return;
            }
            Some(previous) if previous.turn + 1 == view.turn => {
                self.reconcile_plants(&previous, &current);
                self.record_services(view.shacks[1], &previous, &current);
            }
            _ => {
                // Gap or restart: nothing between the two states may be inferred. Own births are
                // ownership rather than observation, so they survive while their plant survives;
                // keeping them can only withhold credit, never grant it.
                self.events.clear();
                self.own.retain(|cell| current.plant(*cell).is_some());
            }
        }
        self.prune(view.turn);
        self.previous = Some(current);
    }

    /// Every retained service as (source, turn, amount), for instrumentation only.
    pub fn service_events(&self) -> Vec<(Cell, i32, i32)> {
        let mut out: Vec<_> = self.events
            .iter()
            .flat_map(|(cell, events)| events.iter().map(move |(turn, amount)| (*cell, *turn, *amount)))
            .collect();
        out.sort_unstable();
        out
    }

    /// Sources that currently satisfy the two-distinct-turn rule and are not ours.
    pub fn eligible_sources(&self) -> Vec<Cell> {
        let mut out: Vec<_> = self.events
            .iter()
            .filter(|(cell, _)| !self.own.contains(cell))
            .filter(|(_, events)| events.len() >= MIN_SERVICE_TURNS)
            .map(|(cell, _)| *cell)
            .collect();
        out.sort_unstable();
        out
    }

    /// Denied fruit for killing `plant` in `kill_turns` turns, in fruit points; the caller converts
    /// it with V439's own 250 * denied / cycle. Zero unless the plant is a live, non-own source of
    /// the generation we observed, with at least two distinct recent service turns, and unless the
    /// last observed snapshot is exactly this view, so a stale ledger can never grant credit.
    #[inline(never)]
    pub fn denied_fruit_points(&self, view: &GameState, plant: &Plant, kill_turns: i32) -> f64 {
        if kill_turns <= 0 || plant.health <= 0 || self.own.contains(&plant.cell) {
            return 0.0;
        }
        let Some(previous) = self.previous.as_ref() else {
            return 0.0;
        };
        if previous.turn != view.turn {
            return 0.0;
        }
        match previous.plant(plant.cell) {
            Some(memo) if memo.kind == plant.kind && memo.health > 0 => {}
            _ => return 0.0,
        }
        let Some(events) = self.events.iter().find(|(cell, _)| *cell == plant.cell)
            .map(|(_, events)| events) else {
            return 0.0;
        };
        // observe() handles each strict transition once and record_services() aggregates every
        // unit on that transition before pushing, so retained entries have unique ascending turns.
        if events.len() < MIN_SERVICE_TURNS {
            return 0.0;
        }
        let (first, first_amount) = events[0];
        let last = events.last().unwrap().0;
        let total: i32 = events.iter().map(|(_, amount)| amount).sum();
        if last <= first {
            return 0.0;
        }
        // The opening service only dates the window; the fruit gained since it is the rate.
        let rate = f64::from(total - first_amount) / f64::from(last - first);
        let near_water = ortho_neighbors(plant.cell)
            .iter()
            .any(|cell| view.water.contains(cell));
        let reset = effective_cooldown(plant.kind, near_water).max(0);
        // A same-kind replacement from seed to first fruit with no travel, capped by what is left
        // of the game once we have actually killed the tree.
        let interruption = (2 + 4 * reset).min((DEADLINE - view.turn - kill_turns).max(0));
        rate * f64::from(interruption)
    }

    #[inline(never)]
    fn snapshot(view: &GameState) -> Snapshot {
        Snapshot {
            turn: view.turn,
            units: view.units.iter().map(|unit| (unit.id, Self::memo(unit))).collect(),
            plants: view
                .plants
                .iter()
                .map(|plant| {
                    (
                        plant.cell,
                        PlantMemo {
                            kind: plant.kind,
                            fruits: plant.fruits,
                            health: plant.health,
                        },
                    )
                })
                .collect(),
        }
    }

    fn memo(unit: &Unit) -> UnitMemo {
        UnitMemo {
            player: unit.player,
            cell: unit.cell,
            carry: unit.carry,
            harvest_power: unit.stats.harvest_power,
        }
    }

    /// Generation bookkeeping: a source that vanished or changed kind is a different tree, so its
    /// services and its ownership die with it, and a fresh plant is classified once, on its birth.
    #[inline(never)]
    fn reconcile_plants(&mut self, previous: &Snapshot, current: &Snapshot) {
        for (cell, before) in &previous.plants {
            let retained = current.plant(*cell).is_some_and(|now| now.kind == before.kind);
            if !retained {
                self.events.retain(|(source, _)| source != cell);
                self.own.retain(|source| source != cell);
            }
        }
        for (cell, now) in &current.plants {
            let fresh = previous.plant(*cell).is_none_or(|before| before.kind != now.kind);
            if !fresh {
                continue;
            }
            self.events.retain(|(source, _)| source != cell);
            if Self::own_birth(previous, current, *cell, now.kind) {
                if !self.own.contains(cell) {
                    self.own.push(*cell);
                }
            } else {
                self.own.retain(|source| source != cell);
            }
        }
    }

    /// A birth is ours when one of our own units stood on the cell in both views and spent a seed
    /// of the new plant's kind there. A birth shared with an enemy planter matches too and counts
    /// as ours, which withholds credit rather than granting it.
    fn own_birth(previous: &Snapshot, current: &Snapshot, cell: Cell, kind: PlantKind) -> bool {
        let index = kind.item_index();
        current.units.iter().any(|(id, now)| {
            now.player == 0
                && now.cell == cell
                && previous.unit(*id).is_some_and(|before| {
                    before.player == 0
                        && before.cell == cell
                        && before.carry[index] > 0
                        && now.carry[index] < before.carry[index]
                })
        })
    }

    #[inline(never)]
    fn record_services(&mut self, enemy_shack: Cell, previous: &Snapshot, current: &Snapshot) {
        let turn = previous.turn;
        for (cell, now) in &current.plants {
            let Some(before) = previous.plant(*cell) else {
                continue;
            };
            if before.kind != now.kind || before.health <= 0 || now.health <= 0 {
                continue;
            }
            let index = now.kind.item_index();
            let mut credited = 0;
            let mut gained = 0;
            let mut unresolved = false;
            for (id, holder) in current.units.iter().filter(|(_, memo)| memo.player == 1 && memo.cell == *cell) {
                let Some(was) = previous.unit(*id) else {
                    unresolved = true;
                    continue;
                };
                let gain = holder.carry[index] - was.carry[index];
                if gain <= 0 {
                    continue;
                }
                // Everything the tree lost must be accounted for, including gains by units that do
                // not themselves qualify as harvesters.
                gained += gain;
                let settled = (0..ITEM_COUNT).all(|item| item == index || holder.carry[item] == was.carry[item]);
                if was.player == 1 && was.cell == *cell && was.harvest_power > 0 && settled {
                    credited += gain;
                }
            }
            if credited <= 0 {
                continue;
            }
            if manhattan(*cell, enemy_shack) <= 1 && (unresolved || before.fruits - now.fruits < gained) {
                continue;
            }
            if let Some((_, services)) = self.events.iter_mut().find(|(source, _)| source == cell) {
                services.push((turn, credited));
            } else {
                self.events.push((*cell, vec![(turn, credited)]));
            }
        }
    }

    fn prune(&mut self, turn: i32) {
        for (_, services) in &mut self.events {
            services.retain(|(recorded, _)| *recorded >= turn - WINDOW && *recorded < turn);
        }
        self.events.retain(|(_, services)| !services.is_empty());
    }

}

/// Minimal test-only surface: behavioural fixtures over real GameState views. The production ledger
/// above never constructs a state, never simulates a turn and is exported without this module.
#[cfg(test)]
mod serviced_source_tests {
    use super::*;
    use crate::candidate::game::types::{Stats, IRON, PLUM};
    use std::collections::BTreeSet;

    const HOME: Cell = (1, 2);
    const ENEMY: Cell = (7, 2);
    const FAR: Cell = (4, 2);
    const DOORSTEP: Cell = (7, 1);

    fn stock(index: usize, amount: i32) -> Stock {
        let mut carry = [0; ITEM_COUNT];
        carry[index] = amount;
        carry
    }

    fn unit(id: i32, player: usize, cell: Cell, harvest_power: i32, carry: Stock) -> Unit {
        Unit {
            id,
            player,
            cell,
            stats: Stats {
                movement_speed: 1,
                carry_capacity: 8,
                harvest_power,
                chop_power: 1,
            },
            carry,
        }
    }

    fn plum(cell: Cell, fruits: i32) -> Plant {
        Plant {
            kind: PlantKind::Plum,
            cell,
            size: 3,
            health: 4,
            fruits,
            cooldown: 5,
        }
    }

    fn view(turn: i32, units: Vec<Unit>, plants: Vec<Plant>) -> GameState {
        let shacks = [HOME, ENEMY];
        let walkable: BTreeSet<Cell> = (0..9)
            .flat_map(|x| (0..5).map(move |y| (x, y)))
            .filter(|cell| !shacks.contains(cell))
            .collect();
        GameState {
            width: 9,
            height: 5,
            walkable,
            shacks,
            inventories: [[0; ITEM_COUNT]; 2],
            units,
            plants,
            scores: [0; 2],
            turn,
            next_id: 9,
            iron: BTreeSet::new(),
            water: BTreeSet::new(),
        }
    }

    /// One enemy harvester with `held` plums, standing on `at`, and a plum tree of `fruits`.
    fn scene(turn: i32, tree: Cell, fruits: i32, at: Cell, held: i32) -> GameState {
        view(turn, vec![unit(1, 1, at, 2, stock(PLUM, held))], vec![plum(tree, fruits)])
    }

    /// Services of 2 on turn 10 and 1 on turn 12, observed from consecutive views of `tree`.
    fn serviced(tree: Cell) -> (Ledger, GameState) {
        let mut ledger = Ledger::new();
        ledger.observe(&scene(10, tree, 3, tree, 0));
        ledger.observe(&scene(11, tree, 1, tree, 2));
        ledger.observe(&scene(12, tree, 1, tree, 2));
        let last = scene(13, tree, 0, tree, 3);
        ledger.observe(&last);
        (ledger, last)
    }

    #[test]
    fn unambiguous_off_shack_harvests_scale_and_meet_the_deadline() {
        let (ledger, last) = serviced(FAR);
        assert_eq!(ledger.service_events(), vec![(FAR, 10, 2), (FAR, 12, 1)]);
        assert_eq!(ledger.eligible_sources(), vec![FAR]);
        // rate = (3 - 2) / (12 - 10); interruption = min(2 + 4 * 8, 301 - 13 - 5) = 34.
        let denied = ledger.denied_fruit_points(&last, &plum(FAR, 0), 5);
        assert!((denied - 17.0).abs() < 1e-9, "{denied}");
        // Deadline cap: only 6 turns remain after the kill, and a dead tree is worth nothing.
        assert!((ledger.denied_fruit_points(&last, &plum(FAR, 0), 282) - 3.0).abs() < 1e-9);
        assert_eq!(ledger.denied_fruit_points(&last, &plum(FAR, 0), 300), 0.0);
        let mut dead = plum(FAR, 0);
        dead.health = 0;
        assert_eq!(ledger.denied_fruit_points(&last, &dead, 5), 0.0);
    }

    #[test]
    fn one_service_or_a_stale_ledger_credits_nothing() {
        let mut ledger = Ledger::new();
        ledger.observe(&scene(10, FAR, 3, FAR, 0));
        let last = scene(11, FAR, 1, FAR, 2);
        ledger.observe(&last);
        assert_eq!(ledger.service_events(), vec![(FAR, 10, 2)]);
        assert!(ledger.eligible_sources().is_empty());
        assert_eq!(ledger.denied_fruit_points(&last, &plum(FAR, 1), 5), 0.0);
        // A view we have not observed is never credited from remembered services.
        let (ledger, _) = serviced(FAR);
        assert_eq!(ledger.denied_fruit_points(&scene(14, FAR, 0, FAR, 3), &plum(FAR, 0), 5), 0.0);
    }

    #[test]
    fn adjacency_and_foreign_cargo_are_not_services() {
        let mut ledger = Ledger::new();
        // Standing beside the tree, not on it, while plums appear in cargo and fruit leaves.
        ledger.observe(&scene(10, FAR, 3, (5, 2), 0));
        ledger.observe(&scene(11, FAR, 1, (5, 2), 2));
        assert!(ledger.service_events().is_empty());
        // On the tree but mining iron: no gain of the source's kind.
        let mut ledger = Ledger::new();
        ledger.observe(&view(10, vec![unit(1, 1, FAR, 2, stock(IRON, 0))], vec![plum(FAR, 3)]));
        ledger.observe(&view(11, vec![unit(1, 1, FAR, 2, stock(IRON, 1))], vec![plum(FAR, 3)]));
        assert!(ledger.service_events().is_empty());
        // On the tree, plums gained, but the unit cannot harvest.
        let mut ledger = Ledger::new();
        ledger.observe(&view(10, vec![unit(1, 1, FAR, 0, stock(PLUM, 0))], vec![plum(FAR, 3)]));
        ledger.observe(&view(11, vec![unit(1, 1, FAR, 0, stock(PLUM, 2))], vec![plum(FAR, 3)]));
        assert!(ledger.service_events().is_empty());
    }

    #[test]
    fn a_pick_on_the_enemy_doorstep_is_never_read_as_a_harvest() {
        // Same cargo signature as a one-fruit harvest, but the tree lost nothing: PICK.
        let mut ledger = Ledger::new();
        ledger.observe(&scene(10, DOORSTEP, 3, DOORSTEP, 0));
        ledger.observe(&scene(11, DOORSTEP, 3, DOORSTEP, 1));
        assert!(ledger.service_events().is_empty());
        // The tree did lose the fruit: a harvest, credited even beside the enemy shack.
        let mut ledger = Ledger::new();
        ledger.observe(&scene(10, DOORSTEP, 3, DOORSTEP, 0));
        ledger.observe(&scene(11, DOORSTEP, 2, DOORSTEP, 1));
        assert_eq!(ledger.service_events(), vec![(DOORSTEP, 10, 1)]);
        // Two enemies share the cell and only one fruit leaves: the pair is unattributable.
        let stacked = |turn, fruits, first, second| {
            view(
                turn,
                vec![
                    unit(1, 1, DOORSTEP, 2, stock(PLUM, first)),
                    unit(2, 1, DOORSTEP, 2, stock(PLUM, second)),
                ],
                vec![plum(DOORSTEP, fruits)],
            )
        };
        let mut ledger = Ledger::new();
        ledger.observe(&stacked(10, 3, 0, 0));
        ledger.observe(&stacked(11, 2, 1, 1));
        assert!(ledger.service_events().is_empty());
        // Both fruits accounted for: both harvesters are summed into one turn's service.
        let mut ledger = Ledger::new();
        ledger.observe(&stacked(10, 3, 0, 0));
        ledger.observe(&stacked(11, 1, 1, 1));
        assert_eq!(ledger.service_events(), vec![(DOORSTEP, 10, 2)]);
    }

    #[test]
    fn own_and_shared_births_are_protected_and_pruned() {
        let planters = |cell: Cell, seeds: i32, enemy_seeds: i32| {
            vec![
                unit(0, 0, cell, 0, stock(PLUM, seeds)),
                unit(1, 1, cell, 2, stock(PLUM, enemy_seeds)),
            ]
        };
        for enemy_before in [0, 1] {
            let mut ledger = Ledger::new();
            ledger.observe(&view(9, planters(FAR, 1, enemy_before), vec![]));
            ledger.observe(&view(10, planters(FAR, 0, enemy_before - enemy_before.min(1)), vec![plum(FAR, 3)]));
            ledger.observe(&scene(11, FAR, 1, FAR, 2));
            ledger.observe(&scene(12, FAR, 1, FAR, 2));
            let last = scene(13, FAR, 0, FAR, 3);
            ledger.observe(&last);
            // Services are still recorded; ours is simply never a denial target.
            assert_eq!(ledger.service_events().len(), 2);
            assert!(ledger.eligible_sources().is_empty());
            assert_eq!(ledger.denied_fruit_points(&last, &plum(FAR, 0), 5), 0.0);
        }
        // Enemy-only birth on the same cell after ours is felled: ownership and history both drop.
        let mut ledger = Ledger::new();
        ledger.observe(&view(9, planters(FAR, 1, 0), vec![]));
        ledger.observe(&view(10, planters(FAR, 0, 0), vec![plum(FAR, 3)]));
        ledger.observe(&view(11, planters(FAR, 0, 0), vec![]));
        ledger.observe(&view(12, planters(FAR, 0, 0), vec![plum(FAR, 3)]));
        assert!(ledger.eligible_sources().is_empty());
        ledger.observe(&scene(13, FAR, 1, FAR, 2));
        ledger.observe(&scene(14, FAR, 1, FAR, 2));
        ledger.observe(&scene(15, FAR, 0, FAR, 3));
        assert_eq!(ledger.eligible_sources(), vec![FAR]);
    }

    #[test]
    fn repeats_gaps_resets_and_the_twelve_turn_window() {
        // A repeated real view neither double counts nor advances the window.
        let mut ledger = Ledger::new();
        ledger.observe(&scene(10, FAR, 3, FAR, 0));
        ledger.observe(&scene(11, FAR, 1, FAR, 2));
        ledger.observe(&scene(11, FAR, 1, FAR, 2));
        assert_eq!(ledger.service_events(), vec![(FAR, 10, 2)]);
        // A skipped turn discards history and infers nothing about the jump.
        ledger.observe(&scene(15, FAR, 0, FAR, 3));
        assert!(ledger.service_events().is_empty());
        // A restart at turn 1 after a later turn is a gap, not a successor.
        let (mut ledger, _) = serviced(FAR);
        ledger.observe(&scene(1, FAR, 3, FAR, 0));
        assert!(ledger.service_events().is_empty());
        // Idle turns retire the turn-10 service exactly when v - 12 passes it.
        let (mut ledger, _) = serviced(FAR);
        for turn in 14..=22 {
            ledger.observe(&scene(turn, FAR, 0, FAR, 3));
        }
        assert_eq!(ledger.service_events(), vec![(FAR, 10, 2), (FAR, 12, 1)]);
        let last = scene(23, FAR, 0, FAR, 3);
        ledger.observe(&last);
        assert_eq!(ledger.service_events(), vec![(FAR, 12, 1)]);
        assert_eq!(ledger.denied_fruit_points(&last, &plum(FAR, 0), 5), 0.0);
    }
}
