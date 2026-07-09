//! Per-seed map features, to correlate with win/loss and find a map-adaptivity signal.
//! Prints: seed shack_dist n_trees n_water n_iron mean_tree_dist_from_shack.
use troll_farm::game::mapgen::generate_bronze;

fn manh(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn main() {
    let n: u64 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(200);
    println!("seed shackdist trees water iron w h treedist");
    for s in 0..n {
        let g = generate_bronze(s);
        let sd = manh(g.shacks[0], g.shacks[1]);
        let trees = g.plants.len();
        let water = g.water.len();
        let iron = g.iron.len();
        let td: f64 = if trees > 0 {
            g.plants
                .iter()
                .map(|p| manh(p.pos(), g.shacks[0]) as f64)
                .sum::<f64>()
                / trees as f64
        } else {
            0.0
        };
        println!(
            "{} {} {} {} {} {} {} {:.1}",
            s, sd, trees, water, iron, g.width, g.height, td
        );
    }
}
