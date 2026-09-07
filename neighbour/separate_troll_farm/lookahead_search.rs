//! Experimental sequence-level policy improvement; never changes the deployed files.
use self::game::types::{GameState, Plant, PlantKind, Stats, Unit};
use self::policy::bot::{Bot as PolicyBot, moisan::SecureOrchardBot as Policy};
use self::simulation::{state as sim, parity};

pub mod bot {
    pub use super::policy::bot::Bot;
    pub mod moisan { pub type SecureOrchardBot = super::super::SearchBot; }
}

#[derive(Clone)]
pub struct SearchBot {
    own: Policy,
    opponent: Policy,
    stalled: i32,
    last_turn: i32,
    pub searches: usize,
    pub changes: usize,
    pub fallbacks: usize,
}

// Frozen initial development configuration, not a platform-qualified candidate.
const START_TURN: i32 = 220;
const SHORT_HORIZON: usize = 8;
const HORIZON: usize = 16;
const ROOTS: usize = 3;
const MAX_RANK: usize = 6;
const MIN_GAIN: f64 = 1.0;

fn physical_seat(view: &GameState) -> Option<usize> {
    // Starting unit 0 belongs to physical player 0; trolls cannot die.
    view.units.iter().find(|u| u.id == 0).map(|u| u.player)
}

fn to_sim(view: &GameState, seat: usize) -> sim::GameState {
    sim::GameState {
        width: view.width, height: view.height,
        walkable: view.walkable.iter().copied().collect(),
        shacks: [view.shacks[seat], view.shacks[seat ^ 1]],
        inventories: [view.inventories[seat], view.inventories[seat ^ 1]],
        scores: [view.scores[seat], view.scores[seat ^ 1]],
        units: view.units.iter().map(|u| sim::Unit {
            id: u.id, player: (u.player ^ seat) as i32, x: u.cell.0, y: u.cell.1,
            ms: u.stats.movement_speed, cc: u.stats.carry_capacity,
            hp: u.stats.harvest_power, chop: u.stats.chop_power, carry: u.carry,
        }).collect(),
        plants: view.plants.iter().map(|p| sim::Plant {
            plant_type: p.kind.as_str().to_owned(), x: p.cell.0, y: p.cell.1,
            size: p.size, health: p.health, fruits: p.fruits, cooldown: p.cooldown,
        }).collect(),
        turn: view.turn, next_id: view.next_id,
        iron: view.iron.iter().copied().collect(), water: view.water.iter().copied().collect(),
    }
}

fn from_sim(g: &sim::GameState, seat: usize) -> GameState {
    GameState {
        width: g.width, height: g.height,
        walkable: g.walkable.iter().copied().collect(),
        shacks: [g.shacks[seat], g.shacks[seat ^ 1]],
        inventories: [g.inventories[seat], g.inventories[seat ^ 1]],
        scores: [g.scores[seat], g.scores[seat ^ 1]],
        units: g.units.iter().map(|u| Unit {
            id: u.id, player: (u.player as usize) ^ seat, cell: (u.x,u.y),
            stats: Stats { movement_speed:u.ms, carry_capacity:u.cc,
                harvest_power:u.hp, chop_power:u.chop }, carry:u.carry,
        }).collect(),
        plants: g.plants.iter().map(|p| Plant {
            kind: PlantKind::parse(&p.plant_type).expect("known fruit"), cell:(p.x,p.y),
            size:p.size, health:p.health, fruits:p.fruits, cooldown:p.cooldown,
        }).collect(),
        turn:g.turn, next_id:g.next_id,
        iron:g.iron.iter().copied().collect(), water:g.water.iter().copied().collect(),
    }
}

fn leaf_value(g: &sim::GameState, seat: usize, terminal: bool) -> f64 {
    let mut values = [g.scores[0] as f64, g.scores[1] as f64];
    if !terminal {
        for player in 0..2 {
            let home = simulation::engine::bfs_distances(&g.walkable, &[g.shacks[player]]);
            for unit in g.units.iter().filter(|u| u.player as usize == player) {
                let Some(distance) = home.get(&unit.pos()) else { continue; };
                let travel = ((*distance - 1).max(0) + unit.ms.max(1) - 1) / unit.ms.max(1);
                let bank_turns = travel + 1;
                // Unbankable end-game cargo is worthless, not credited as final score.
                if bank_turns > (301 - g.turn).max(0) { continue; }
                let cargo = unit.carry[..4].iter().sum::<i32>() + 4 * unit.carry[5];
                values[player] += cargo as f64 * 0.9 / (1.0 + 0.04 * bank_turns as f64);
            }
        }
    }
    values[seat] - values[seat ^ 1]
}

impl SearchBot {
    pub fn new() -> Self {
        Self { own:Policy::new(), opponent:Policy::new(), stalled:0, last_turn:0,
            searches:0, changes:0, fallbacks:0 }
    }

    fn rollout(&self, g: &sim::GameState, seat: usize, mut own: Policy,
        root: &[String], opponent_root: &[String])
        -> Option<[f64;2]>
    {
        let mut referee = parity::from_game(g.clone());
        let mut opponent = self.opponent.clone();
        let mut stalled = self.stalled;
        let mut ours = root.to_vec();
        let mut theirs = opponent_root.to_vec();
        let mut values = [0.0;2];
        for depth in 0..HORIZON {
            let (a,b) = if seat == 0 {(&ours,&theirs)} else {(&theirs,&ours)};
            parity::step_direct(&mut referee,a,b).ok()?;
            // Keep only current-step legality; rollouts must not grow an event archive.
            if referee.legality.critical_issue_count() > 0 { return None; }
            referee.legality = Default::default();
            let terminal = referee.game.turn > 300
                || simulation::engine::has_stalled(&referee.game,&mut stalled);
            if terminal || depth + 1 == SHORT_HORIZON || depth + 1 == HORIZON {
                let value=leaf_value(&referee.game,seat,terminal);
                if depth + 1 <= SHORT_HORIZON {values[0]=value;}
                if terminal || depth + 1 == HORIZON {
                    values[1]=value;
                    return Some(values);
                }
            }
            ours = own.commands(&from_sim(&referee.game,seat));
            theirs = opponent.commands(&from_sim(&referee.game,seat ^ 1));
        }
        None
    }
}

impl PolicyBot for SearchBot {
    fn commands(&mut self, view: &GameState) -> Vec<String> {
        let mut baseline = self.own.clone();
        baseline.set_selection_rank(0);
        let baseline_commands = baseline.commands(view);
        let Some(seat) = physical_seat(view) else {
            self.own = baseline;
            return baseline_commands;
        };
        let g = to_sim(view,seat);
        if view.turn > 1 && view.turn != self.last_turn {
            simulation::engine::has_stalled(&g,&mut self.stalled);
        }
        self.last_turn = view.turn;
        if view.turn < START_TURN {
            self.own = baseline;
            return baseline_commands;
        }
        self.searches += 1;
        // This is an adaptive V439 opponent hypothesis, not its observed policy.
        let opponent_root = self.opponent.commands(&from_sim(&g,seat ^ 1));
        let mut roots = vec![(baseline,baseline_commands.clone())];
        for rank in 1..=MAX_RANK {
            if roots.len() >= ROOTS { break; }
            let mut branch = self.own.clone();
            branch.set_selection_rank(rank);
            let commands = branch.commands(view);
            branch.set_selection_rank(0);
            if !roots.iter().any(|(_,other)| other == &commands) { roots.push((branch,commands)); }
        }
        if roots.len() == 1 {
            self.own = roots.remove(0).0;
            return baseline_commands;
        }
        let mut values = Vec::new();
        for (branch,commands) in &roots {
            let Some(value) = self.rollout(&g,seat,branch.clone(),commands,&opponent_root) else {
                self.fallbacks += 1;
                self.own = roots[0].0.clone();
                return baseline_commands;
            };
            values.push(value);
        }
        let mut best = 0;
        let mut best_gain = 0.0;
        for index in 1..values.len() {
            let gain=(values[index][0]-values[0][0]).min(values[index][1]-values[0][1]);
            if gain >= MIN_GAIN && gain > best_gain {best=index;best_gain=gain;}
        }
        self.changes += usize::from(best != 0);
        // Commit only memory associated with the command actually issued, not a rollout leaf.
        let (chosen,commands) = roots.swap_remove(best);
        self.own = chosen;
        commands
    }
}
