//! One scored A/B match between two bot binaries on a seeded generated map.
//! usage: playmatch <bot0|WAIT> <bot1|WAIT> <seed> [max_turns=300]
//! stdout (ONE line, versioned interface consumed by cgauto/abgate.py):
//!   seed turns score0 score1 fruit0 wood0 fruit1 wood1 crash0 crash1

use troll_farm::game::driver::play_match;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 4 {
        eprintln!("usage: playmatch <bot0|WAIT> <bot1|WAIT> <seed> [max_turns=300]");
        std::process::exit(2);
    }
    let seed: u64 = a[3].parse().expect("seed must be a u64");
    let max_turns: i32 = a.get(4).map(|s| s.parse().expect("max_turns")).unwrap_or(300);
    let r = play_match(&a[1], &a[2], seed, max_turns);
    println!(
        "{} {} {} {} {} {} {} {} {} {}",
        seed,
        r.turns,
        r.scores[0],
        r.scores[1],
        r.fruit[0],
        r.wood[0],
        r.fruit[1],
        r.wood[1],
        r.crashed[0] as u8,
        r.crashed[1] as u8
    );
}
