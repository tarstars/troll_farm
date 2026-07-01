//! Deep single-game probe: for a seed + player, dump each of that player's trolls
//! (id, pos, carry, free, cmd) plus a fruit summary over a turn range, so we can
//! see EXACTLY why trolls go idle / wedge. Usage: probe [A] [B] [seed] [who] [lo] [hi]
use troll_farm::game::engine::step;
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::roster;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let na = args.get(1).cloned().unwrap_or_else(|| "planner".into());
    let nb = args.get(2).cloned().unwrap_or_else(|| "boss4".into());
    let seed: u64 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(78);
    let who: usize = args.get(4).and_then(|s| s.parse().ok()).unwrap_or(0);
    let lo: i32 = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(195);
    let hi: i32 = args.get(6).and_then(|s| s.parse().ok()).unwrap_or(215);

    let bots = roster();
    let a = &*bots[bots.iter().position(|x| x.name() == na).expect("bad A")];
    let b = &*bots[bots.iter().position(|x| x.name() == nb).expect("bad B")];
    let wi = who as i32;

    let mut g = generate_bronze(seed);
    for t in 0..300 {
        let c0 = a.decide(&g, 0);
        let c1 = b.decide(&g, 1);
        let cw = if who == 0 { &c0 } else { &c1 };
        let turn = t + 1;
        if turn >= lo && turn <= hi {
            let fruited = g.plants.iter().filter(|p| p.fruits > 0).count();
            let total_fruit: i32 = g.plants.iter().map(|p| p.fruits).sum();
            println!("--- t{} score={} nplants={} fruited={} totfruit={} ---",
                turn, g.scores[who], g.plants.len(), fruited, total_fruit);
            let mut mine: Vec<_> = g.units.iter().filter(|u| u.player == wi).collect();
            mine.sort_by_key(|u| u.id);
            for u in &mine {
                let cmd = cw.iter().find(|c| {
                    c.split_whitespace().nth(1).and_then(|s| s.parse::<i32>().ok()) == Some(u.id)
                        || (c.as_str() == "WAIT")
                }).cloned().unwrap_or_else(|| "(none)".into());
                // is this troll standing on a plant?
                let on = g.plants.iter().find(|p| p.pos() == u.pos());
                let on_s = match on {
                    Some(p) => format!("ON {} f{} cd{} sz{}", p.plant_type, p.fruits, p.cooldown, p.size),
                    None => "-".into(),
                };
                println!("  troll {:>2} @({:>2},{:>2}) carry{:?} free{} cc{} chop{} | {}  [{}]",
                    u.id, u.x, u.y, u.carry, u.free(), u.cc, u.chop, cmd, on_s);
            }
            // nearest few fruited trees to shack
            let shack = g.shacks[who];
            let mut fr: Vec<_> = g.plants.iter().filter(|p| p.fruits > 0).collect();
            fr.sort_by_key(|p| (p.x - shack.0).abs() + (p.y - shack.1).abs());
            let show: Vec<String> = fr.iter().take(5)
                .map(|p| format!("({},{})f{}", p.x, p.y, p.fruits)).collect();
            if !show.is_empty() {
                println!("    fruited near shack{:?}: {}", shack, show.join(" "));
            }
        }
        step(&mut g, &c0, &c1);
    }
}
