use std::env;
use troll_farm::game::official_mapgen::{generate_official, render_turn_one};

fn main() {
    let mut arguments = env::args().skip(1);
    let seed = arguments
        .next()
        .expect("usage: d33_official_mapgen SEED")
        .parse::<i64>()
        .expect("SEED must be a signed 64-bit integer");
    assert!(arguments.next().is_none(), "expected exactly one seed");
    print!("{}", render_turn_one(&generate_official(seed), 0));
}
