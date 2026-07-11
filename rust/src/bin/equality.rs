//! R1 EQUALITY HARNESS (docs/refactor-goal.md): prove the refactored bot behaves EXACTLY
//! like the frozen v1.20.0 baseline. Drives two compiled BOT BINARIES through the CG
//! stdin/stdout protocol over the same simulated games and asserts identical per-turn
//! command lines. Black-box: covers parsing + decision + formatting, i.e. the whole
//! artifact. Referee-fidelity of listing order is NOT required — both bots see the same
//! serializer, so any self-consistent order is a valid equality probe.
//!
//! The bot's protocol (mirrored from main.rs): header `width height` + `height` grid rows
//! ('0' my shack, '1' opp shack, '.' walkable, '+' iron, '~' water, '#' rock); per turn:
//! my inventory (6 ints), opp inventory (6 ints), tree count + `TYPE x y size health
//! fruits cooldown` each, troll count + `id player x y ms cc hp chop carry0..5` each
//! (player 0 = the bot). Output: one `;`-joined line of commands per turn.
//!
//! Usage: equality <botA> <botB> <seeds> [max_turns=300]
//!   Plays every seed with the bot in BOTH seats (opponent = roster "goldelite", falling
//!   back to "silverboss"). Reports the first divergence (seed/seat/turn + both lines) and
//!   a summary. Exit code 0 iff all games identical.

use troll_farm::game::driver::play;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 4 {
        eprintln!("usage: equality <botA> <botB> <seeds> [max_turns=300] [opp=WAIT|<path>]");
        std::process::exit(2);
    }
    let (bot_a, bot_b) = (&args[1], &args[2]);
    let seeds: u64 = args[3].parse().unwrap();
    let max_turns: i32 = args.get(4).map(|s| s.parse().unwrap()).unwrap_or(300);
    let opp = args.get(5).cloned().unwrap_or_else(|| "WAIT".to_string());

    let mut games = 0u64;
    let mut divergent = 0u64;
    for seed in 0..seeds {
        for seat in 0..2usize {
            let la = play(bot_a, &opp, seed, seat, max_turns);
            let lb = play(bot_b, &opp, seed, seat, max_turns);
            games += 1;
            if la != lb {
                divergent += 1;
                let t = la
                    .iter()
                    .zip(lb.iter())
                    .position(|(a, b)| a != b)
                    .unwrap_or_else(|| la.len().min(lb.len()));
                eprintln!(
                    "DIVERGE seed={seed} seat={seat} turn={} ({} vs {} turns)",
                    t + 1,
                    la.len(),
                    lb.len()
                );
                eprintln!("  A: {}", la.get(t).map(String::as_str).unwrap_or("<none>"));
                eprintln!("  B: {}", lb.get(t).map(String::as_str).unwrap_or("<none>"));
                if divergent >= 5 {
                    eprintln!("(stopping after 5 divergences)");
                    println!("NOT EQUAL: {divergent}+ of {games} games diverged");
                    std::process::exit(1);
                }
            }
        }
        if (seed + 1) % 50 == 0 {
            eprintln!(
                "  … {} seeds done ({} games), divergent so far: {}",
                seed + 1,
                games,
                divergent
            );
        }
    }
    if divergent == 0 {
        println!("EQUAL: {games} games ({seeds} seeds x 2 seats), all command streams identical");
    } else {
        println!("NOT EQUAL: {divergent} of {games} games diverged");
        std::process::exit(1);
    }
}
