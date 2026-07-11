//! `etude` — terminal runner/renderer for the forced-outcome oracle etudes (see
//! `troll_farm::etudes`). Loads a Situation text file, renders an ASCII board + entity table,
//! runs `forced_verdict`, and (with `--step`) walks the forcing-line proof one ply at a time.
//!
//! Usage: `etude <situation-file.txt> [--step]`

use troll_farm::etudes::oracle::{replay_proof, Verdict};
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

/// Format a `Verdict` for terminal output: `ForcedWin` prints the side, the forcing line (one
/// `ply N: <joint command>   diff=<score-diff>` per `Proof.line` entry), and the independent
/// `replay_proof` validation; `Unresolved`/`TooLarge` print plainly. Pure function of
/// `(sit, verdict)` — `sit` is only needed to re-run `replay_proof`'s independent check.
pub fn format_verdict(sit: &Situation, verdict: &Verdict) -> String {
    let mut out = String::new();
    match verdict {
        Verdict::ForcedWin { side, proof } => {
            out.push_str(&format!("Verdict: ForcedWin(side={side})\n"));
            out.push_str("Forcing line:\n");
            for (i, (cmd, diff)) in proof.line.iter().enumerate() {
                out.push_str(&format!("  ply {}: {cmd}   diff={diff}\n", i + 1));
            }
            let valid = replay_proof(sit, verdict);
            out.push_str(&format!("proof validated: {valid}\n"));
        }
        Verdict::Unresolved => out.push_str("Verdict: Unresolved\n"),
        Verdict::TooLarge => out.push_str("Verdict: TooLarge\n"),
    }
    out
}

fn main() {
    // TODO: IO + render + forced_verdict wiring (later stages).
}

#[cfg(test)]
mod tests {
    use super::*;
    use troll_farm::etudes::oracle::forced_verdict;
    use troll_farm::etudes::situation::from_text;

    /// The oracle's forced-win-by-felling fixture (rust/tests/etudes.rs
    /// `oracle_forced_win_by_felling`) — cooldown=6 so the tree is quiescent (cooldown=0 would
    /// regrow it after the first chop; see that test's comment). Also shipped verbatim as
    /// data/etudes/sample-forced-win.txt for the CLI demo.
    const FELLING_FIXTURE: &str = "\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0";

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

    #[test]
    fn format_verdict_unresolved_and_toolarge_print_plainly() {
        let sit = fixture_basic(); // content irrelevant to these two branches
        assert_eq!(format_verdict(&sit, &Verdict::Unresolved), "Verdict: Unresolved\n");
        assert_eq!(format_verdict(&sit, &Verdict::TooLarge), "Verdict: TooLarge\n");
    }

    #[test]
    fn format_verdict_forced_win_prints_line_and_validation() {
        let sit = from_text(FELLING_FIXTURE);
        let verdict = forced_verdict(&sit);
        let text = format_verdict(&sit, &verdict);
        assert!(text.contains("ForcedWin(side=0)"), "got: {text}");
        assert!(text.contains("proof validated: true"), "got: {text}");
        let ply_lines = text.lines().filter(|l| l.trim_start().starts_with("ply ")).count();
        assert_eq!(ply_lines, 4, "H=4 proof must print exactly 4 plies; got: {text}");
    }

    #[test]
    fn sample_data_file_is_forced_win_for_side_0() {
        // Regression: the committed CLI demo fixture (data/etudes/sample-forced-win.txt) must
        // stay byte-identical in substance to FELLING_FIXTURE — a valid, quiescent forced win.
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/data/etudes/sample-forced-win.txt");
        let text = std::fs::read_to_string(path)
            .unwrap_or_else(|e| panic!("sample-forced-win.txt must exist at {path}: {e}"));
        let sit = from_text(&text);
        let verdict = forced_verdict(&sit);
        assert!(matches!(verdict, Verdict::ForcedWin { side: 0, .. }), "got: {verdict:?}");
        assert!(replay_proof(&sit, &verdict));
    }

    #[test]
    fn contested_fixture_is_unresolved() {
        // rust/tests/etudes.rs `oracle_unresolved_or_symmetric`'s fixture: neither side can
        // reach a resource in time — documents/regression-checks the runner's Unresolved path.
        let sit = from_text(
            "\
MAP 5 3
.0..1
.....
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
UNIT 3 1 3 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 2
PROVE -",
        );
        assert!(matches!(forced_verdict(&sit), Verdict::Unresolved));
    }
}
