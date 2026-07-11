use std::collections::HashSet;

/// A grid cell (x, y).
pub type Cell = (i32, i32);

/// A troll unit (SimUnit in Python).
#[derive(Clone, Debug, PartialEq)]
pub struct Unit {
    pub id: i32,
    pub player: i32,
    pub x: i32,
    pub y: i32,
    /// movement speed
    pub ms: i32,
    /// carry capacity
    pub cc: i32,
    /// harvest power
    pub hp: i32,
    /// chop power
    pub chop: i32,
    /// carried items: [PLUM, LEMON, APPLE, BANANA, IRON, WOOD]
    pub carry: [i32; 6],
}

impl Unit {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
    pub fn total(&self) -> i32 {
        self.carry.iter().sum()
    }
    pub fn free(&self) -> i32 {
        self.cc - self.total()
    }
}

/// A plant / tree (SimPlant in Python).
#[derive(Clone, Debug, PartialEq)]
pub struct Plant {
    pub plant_type: String,
    pub x: i32,
    pub y: i32,
    pub size: i32,
    pub health: i32,
    pub fruits: i32,
    pub cooldown: i32,
}

impl Plant {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
}

/// Full game state (GameState in Python).
#[derive(Clone, Debug)]
pub struct GameState {
    pub width: i32,
    pub height: i32,
    pub walkable: HashSet<Cell>,
    pub shacks: [Cell; 2],
    pub inventories: [[i32; 6]; 2],
    pub units: Vec<Unit>,
    pub plants: Vec<Plant>,
    pub scores: [i32; 2],
    pub turn: i32,
    pub next_id: i32,
    pub iron: HashSet<Cell>,
    pub water: HashSet<Cell>,
}

/// Parse an ASCII grid into a GameState.
///
/// Characters:
///   '.' or ' ' -> walkable
///   '#'        -> wall (not walkable, not anything else)
///   '0'        -> shack for player 0  (added to walkable)
///   '1'        -> shack for player 1  (added to walkable)
///   '+'        -> iron cell (NOT walkable, but in iron set)
///   '~'        -> water cell (NOT walkable, but in water set)
///
/// The Python from_ascii adds '0' and '1' cells to walkable implicitly
/// (they are not excluded from walkable — iron/water are excluded instead).
/// Looking at the Python: shacks go into shacks[], everything else that is
/// NOT '#' ends up in walkable or iron or water.  Actually the Python code
/// skips '#' (no else branch adds it), adds '0'/'1' as shacks, adds '+'
/// as iron, '~' as water, and everything else (including '.') to walkable.
/// So shack cells ARE in walkable (they don't go into walkable explicitly
/// but the engine uses shack as a position for units — need to check).
///
/// Re-reading Python from_ascii: the loop does `walkable.add((x,y))` only
/// in the else branch, which catches '.' and any other char not '0','1','+','~'.
/// So shack cells are NOT in walkable. Iron/water cells are NOT in walkable.
/// Only '.' (and unrecognised chars) end up in walkable.
///
/// Talents defaults: (ms=1, cc=1, hp=1, chop=0)
pub fn from_ascii(rows: &[&str]) -> GameState {
    from_ascii_with_talents(rows, (1, 1, 1, 0))
}

pub fn from_ascii_with_talents(rows: &[&str], talents: (i32, i32, i32, i32)) -> GameState {
    let height = rows.len() as i32;
    let width = if rows.is_empty() {
        0
    } else {
        rows[0].len() as i32
    };
    let mut walkable: HashSet<Cell> = HashSet::new();
    let mut iron: HashSet<Cell> = HashSet::new();
    let mut water: HashSet<Cell> = HashSet::new();
    let mut shacks: [Cell; 2] = [(0, 0), (0, 0)];

    for (y, row) in rows.iter().enumerate() {
        for (x, ch) in row.chars().enumerate() {
            let cell = (x as i32, y as i32);
            match ch {
                '0' => {
                    shacks[0] = cell;
                }
                '1' => {
                    shacks[1] = cell;
                }
                '+' => {
                    iron.insert(cell);
                }
                '~' => {
                    water.insert(cell);
                }
                '#' => { /* wall, skip */ }
                _ => {
                    walkable.insert(cell);
                }
            }
        }
    }

    let (ms, cc, hp, chop) = talents;
    let mut units = Vec::new();
    for p in 0..2i32 {
        let (sx, sy) = shacks[p as usize];
        units.push(Unit {
            id: p,
            player: p,
            x: sx,
            y: sy,
            ms,
            cc,
            hp,
            chop,
            carry: [0; 6],
        });
    }

    GameState {
        width,
        height,
        walkable,
        shacks,
        inventories: [[0; 6]; 2],
        units,
        plants: Vec::new(),
        scores: [0; 2],
        turn: 1,
        next_id: 2,
        iron,
        water,
    }
}
