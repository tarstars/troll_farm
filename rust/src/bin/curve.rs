//! Game-shape curve: play A vs B over N seeds (both seats) and sample, at a set of
//! turns, the average plants remaining, fruited plants, and each side's banked
//! score / wood / fruit. Reveals whether games deplete all trees (scorched-earth
//! race) and where value accumulates. Usage: curve [A] [B] [seeds]
use troll_farm::game::engine::{recompute_scores, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::roster;

const SAMPLE: [i32; 7] = [30, 60, 100, 150, 200, 250, 300];

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let na = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let nb = args.get(2).cloned().unwrap_or_else(|| "boss4".into());
    let seeds: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(120);

    let bots = roster();
    let a = &*bots[bots.iter().position(|x| x.name() == na).expect("bad A")];
    let b = &*bots[bots.iter().position(|x| x.name() == nb).expect("bad B")];

    // accumulators indexed by sample point; A is always the tracked "us"
    let mut nplants = [0f64; 7];
    let mut fruited = [0f64; 7];
    let mut a_score = [0f64; 7];
    let mut b_score = [0f64; 7];
    let mut a_wood = [0f64; 7];
    let mut a_fruit = [0f64; 7];
    let mut b_wood = [0f64; 7];
    let mut b_fruit = [0f64; 7];
    let mut n = 0f64;

    for seat in 0..2 {
        for s in 0..seeds {
            let (p0, p1): (
                &dyn troll_farm::strategies::Strategy,
                &dyn troll_farm::strategies::Strategy,
            ) = if seat == 0 { (a, b) } else { (b, a) };
            let us = seat; // A's player index
            let them = 1 - seat;
            let mut g = generate_bronze(s);
            let mut si = 0usize;
            for t in 0..300 {
                let c0 = p0.decide(&g, 0);
                let c1 = p1.decide(&g, 1);
                step(&mut g, &c0, &c1);
                let turn = t + 1;
                if si < SAMPLE.len() && turn == SAMPLE[si] {
                    recompute_scores(&mut g);
                    nplants[si] += g.plants.len() as f64;
                    fruited[si] += g.plants.iter().filter(|p| p.fruits > 0).count() as f64;
                    a_score[si] += g.scores[us] as f64;
                    b_score[si] += g.scores[them] as f64;
                    a_wood[si] += g.inventories[us][WOOD] as f64;
                    a_fruit[si] += g.inventories[us][0..4].iter().sum::<i32>() as f64;
                    b_wood[si] += g.inventories[them][WOOD] as f64;
                    b_fruit[si] += g.inventories[them][0..4].iter().sum::<i32>() as f64;
                    si += 1;
                }
            }
            n += 1.0;
        }
    }

    println!(
        "=== curve: {} (A) vs {} (B) | {} seeds x2 seats = {} games ===",
        na, nb, seeds, n as i64
    );
    println!(
        "{:>5} {:>8} {:>8} | {:>8} {:>7} {:>7} | {:>8} {:>7} {:>7}",
        "turn", "plants", "fruited", "A_score", "A_wood", "A_frt", "B_score", "B_wood", "B_frt"
    );
    for i in 0..SAMPLE.len() {
        println!(
            "{:>5} {:>8.1} {:>8.1} | {:>8.1} {:>7.1} {:>7.1} | {:>8.1} {:>7.1} {:>7.1}",
            SAMPLE[i],
            nplants[i] / n,
            fruited[i] / n,
            a_score[i] / n,
            a_wood[i] / n,
            a_fruit[i] / n,
            b_score[i] / n,
            b_wood[i] / n,
            b_fruit[i] / n
        );
    }
}
