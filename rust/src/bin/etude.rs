//! `etude` — terminal runner/renderer for the forced-outcome oracle etudes (see
//! `troll_farm::etudes`). Loads a Situation text file, renders an ASCII board + entity table,
//! runs `forced_verdict`, and (with `--step`) walks the forcing-line proof one ply at a time.
//!
//! Usage: `etude <situation-file.txt> [--step]`

use troll_farm::etudes::situation::Situation;

/// [PLUM, LEMON, APPLE, BANANA, IRON, WOOD] — matches the carry/inventory slot order used
/// throughout `game::state`/`game::engine`.
const RESOURCE_INITIALS: [char; 6] = ['P', 'L', 'A', 'B', 'I', 'W'];

/// Render a Situation as an ASCII board (terrain, with shack/tree/troll overlays, troll drawn on
/// top of everything) followed by an entity table (trolls, trees, inventories, scores, turn,
/// horizon). Pure function of the Situation — used directly by `main` and unit-tested here.
pub fn render(sit: &Situation) -> String {
    let st = &sit.state;
    let mut out = String::new();

    // Board: terrain, then shack, then tree, then troll — each layer overlays the previous one,
    // so a troll standing on a tree (or a shack) shows its id digit, never the terrain beneath.
    for y in 0..st.height {
        let mut row = String::with_capacity(st.width as usize);
        for x in 0..st.width {
            let cell = (x, y);
            let mut ch = if st.walkable.contains(&cell) {
                '.'
            } else if st.water.contains(&cell) {
                '~'
            } else if st.iron.contains(&cell) {
                '+'
            } else {
                '#'
            };
            if cell == st.shacks[0] {
                ch = '0';
            } else if cell == st.shacks[1] {
                ch = '1';
            }
            if let Some(p) = st.plants.iter().find(|p| p.pos() == cell) {
                ch = tree_glyph(&p.plant_type);
            }
            if let Some(u) = st.units.iter().find(|u| u.pos() == cell) {
                ch = std::char::from_digit(u.id as u32, 10).unwrap_or('?');
            }
            row.push(ch);
        }
        out.push_str(&row);
        out.push('\n');
    }
    out.push('\n');

    out.push_str("Trolls:\n");
    let mut units: Vec<_> = st.units.iter().collect();
    units.sort_by_key(|u| u.id);
    for u in units {
        out.push_str(&format!(
            "  id={} player={} pos=({},{}) ms={} cc={} hp={} chop={} carry=[{}]\n",
            u.id,
            u.player,
            u.x,
            u.y,
            u.ms,
            u.cc,
            u.hp,
            u.chop,
            fmt_carry(&u.carry)
        ));
    }

    out.push_str("Trees:\n");
    let mut plants: Vec<_> = st.plants.iter().collect();
    plants.sort_by_key(|p| (p.x, p.y));
    for p in plants {
        out.push_str(&format!(
            "  {} pos=({},{}) size={} health={} fruits={}\n",
            p.plant_type, p.x, p.y, p.size, p.health, p.fruits
        ));
    }

    out.push_str(&format!(
        "Inventories: P0=[{}] P1=[{}]\n",
        fmt_carry(&st.inventories[0]),
        fmt_carry(&st.inventories[1])
    ));
    out.push_str(&format!("Scores: {} {}\n", st.scores[0], st.scores[1]));
    out.push_str(&format!("Turn: {}\n", st.turn));
    out.push_str(&format!("Horizon: {}\n", sit.horizon));

    out
}

fn tree_glyph(plant_type: &str) -> char {
    plant_type.chars().next().unwrap_or('?').to_ascii_uppercase()
}

fn fmt_carry(carry: &[i32; 6]) -> String {
    RESOURCE_INITIALS
        .iter()
        .zip(carry.iter())
        .map(|(initial, n)| format!("{initial}{n}"))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    // TODO: IO + render + forced_verdict wiring (later stages).
}

#[cfg(test)]
mod tests {
    use super::*;
    use troll_farm::etudes::situation::from_text;

    fn fixture_basic() -> Situation {
        from_text(
            "\
MAP 5 3
.0..1
.....
..B..
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 7 0 4 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE -",
        )
    }

    #[test]
    fn render_places_shacks_tree_and_troll_glyphs() {
        let sit = fixture_basic();
        let out = render(&sit);
        let lines: Vec<&str> = out.lines().collect();
        assert_eq!(lines[0], ".0..1", "row 0: shacks at (1,0) and (4,0)");
        assert_eq!(lines[1], "....7", "row 1: troll id 7 at (4,1)");
        assert_eq!(lines[2], "..B..", "row 2: banana tree at (2,2)");
    }

    #[test]
    fn render_troll_wins_over_tree_when_co_located() {
        let sit = from_text(
            "\
MAP 5 3
.0..1
.....
..B..
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 3 0 2 2 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE -",
        );
        let out = render(&sit);
        let lines: Vec<&str> = out.lines().collect();
        assert_eq!(lines[2], "..3..", "troll standing on the tree renders its id, not B");
    }
}
