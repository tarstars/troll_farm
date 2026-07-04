//! Profile the fast-sim rollout cost: isolate engine vs policy.
use std::time::Instant;
use troll_farm::game::fast::{FCmds, FastState, NavTable};
use troll_farm::game::mapgen::generate_bronze;

fn main() {
    let g = generate_bronze(7);
    let nav = NavTable::build(&g);
    let fs = FastState::from_game(&g);
    let horizon = 40;

    // (A) bare engine: 40-turn rollout with trivial (all-idle) commands.
    let idle = [FCmds::default(), FCmds::default()];
    let reps = 200_000u64;
    let t0 = Instant::now();
    let mut sink = 0i64;
    for _ in 0..reps {
        let mut s = fs;
        for _ in 0..horizon {
            troll_farm::game::fast::step_fast(&mut s, &nav, &idle);
        }
        sink += s.score(0) as i64;
    }
    let dt = t0.elapsed().as_secs_f64();
    println!(
        "(A) BARE ENGINE: {} rollouts of {} turns in {:.3}s = {:.0} rollouts/sec, {:.2} us/rollout  (sink {})",
        reps, horizon, dt, reps as f64 / dt, 1e6 * dt / reps as f64, sink
    );
    println!(
        "    -> in a 45ms budget: ~{:.0} bare rollouts/turn",
        0.045 * reps as f64 / dt
    );

    // (B) NavTable build cost (done once per game, but measure it).
    let t1 = Instant::now();
    for _ in 0..200 {
        let _ = NavTable::build(&g);
    }
    println!("(B) NavTable::build: {:.2} ms each", 1000.0 * t1.elapsed().as_secs_f64() / 200.0);

    // (C) FastState clone cost (every rollout starts with a copy).
    let t2 = Instant::now();
    let mut acc = 0i64;
    for _ in 0..5_000_000 {
        let s = fs;
        acc += s.turn as i64;
    }
    println!("(C) FastState copy: {:.1} ns each ({} bytes) (acc {})",
        1e9 * t2.elapsed().as_secs_f64() / 5_000_000.0, std::mem::size_of::<FastState>(), acc);
}
