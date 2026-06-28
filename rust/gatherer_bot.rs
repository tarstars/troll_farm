// CodinGame Troll Farm — standalone GATHERER bot (self-contained, paste-ready).
// Fruit economy: expand to strong balanced trolls, harvest the nearest fruit with
// distinct targets, never chop. (Same strategy as the tournament's `gatherer`.)
#![allow(dead_code, unused)]
use std::collections::HashSet;
use std::io::{self, BufRead, Write};

fn training_cost(n: i32, t: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = t;
    let mut c = [0i32; 6];
    c[0] = n + ms * ms; // PLUM <- movementSpeed
    c[1] = n + cc * cc; // LEMON <- carryCapacity
    c[2] = n + hp * hp; // APPLE <- harvestPower
    c[4] = n + chop * chop; // IRON <- chopPower
    c
}

fn dist(a: (i32, i32), b: (i32, i32)) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

struct Troll {
    id: i32,
    x: i32,
    y: i32,
    cc: i32,
    carry: [i32; 6],
}
impl Troll {
    fn pos(&self) -> (i32, i32) {
        (self.x, self.y)
    }
    fn total(&self) -> i32 {
        self.carry.iter().sum()
    }
}
struct Tree {
    x: i32,
    y: i32,
    fruits: i32,
}

fn bank(id: i32, pos: (i32, i32), shack: (i32, i32)) -> String {
    if dist(pos, shack) == 1 {
        format!("DROP {}", id)
    } else {
        format!("MOVE {} {} {}", id, shack.0, shack.1)
    }
}

fn decide(mine: &[Troll], inv: &[i32], trees: &[Tree], shack: (i32, i32), iron: bool, turn: i32) -> Vec<String> {
    let mut cmds: Vec<String> = Vec::new();
    if turn == 1 {
        cmds.push("MSG gatherer".to_string());
    }
    let n = mine.len() as i32;
    let any_fruit = trees.iter().any(|t| t.fruits > 0);
    let mut reserved: HashSet<(i32, i32)> = HashSet::new();
    for u in mine {
        let on_fruit = trees.iter().any(|t| (t.x, t.y) == u.pos() && t.fruits > 0);
        if on_fruit && u.total() < u.cc {
            cmds.push(format!("HARVEST {}", u.id));
            continue;
        }
        if u.total() >= u.cc || (u.total() > 0 && !any_fruit) {
            cmds.push(bank(u.id, u.pos(), shack));
            continue;
        }
        let mut best: Option<(i32, (i32, i32))> = None;
        for t in trees.iter().filter(|t| t.fruits > 0) {
            let p = (t.x, t.y);
            if reserved.contains(&p) {
                continue;
            }
            let d = dist(u.pos(), p);
            if best.is_none() || d < best.unwrap().0 {
                best = Some((d, p));
            }
        }
        if let Some((_, tp)) = best {
            reserved.insert(tp);
            cmds.push(if u.pos() == tp {
                format!("HARVEST {}", u.id)
            } else {
                format!("MOVE {} {} {}", u.id, tp.0, tp.1)
            });
        } else if u.total() > 0 {
            cmds.push(bank(u.id, u.pos(), shack));
        }
    }
    // Expand to strong balanced trolls when affordable (and shack free).
    if n < 4 && !mine.iter().any(|u| u.pos() == shack) {
        let pay: &[usize] = if iron { &[0, 1, 2, 4] } else { &[0, 1, 2] };
        for &spec in [(2, 2, 2, 2), (1, 2, 2, 0), (1, 1, 1, 0)].iter() {
            let cost = training_cost(n, spec);
            if pay.iter().all(|&i| inv[i] >= cost[i]) {
                cmds.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
                break;
            }
        }
    }
    if cmds.is_empty() {
        cmds.push("WAIT".to_string());
    }
    cmds
}

fn rd(r: &mut impl BufRead) -> String {
    let mut s = String::new();
    r.read_line(&mut s).unwrap();
    s
}

fn main() {
    let stdin = io::stdin();
    let mut r = io::BufReader::new(stdin.lock());
    let stdout = io::stdout();
    let mut out = io::BufWriter::new(stdout.lock());

    let header = rd(&mut r);
    let mut it = header.split_whitespace();
    let _w: i32 = it.next().unwrap().parse().unwrap();
    let h: i32 = it.next().unwrap().parse().unwrap();
    let mut my_shack = (0, 0);
    let mut iron_present = false;
    for y in 0..h {
        let row = rd(&mut r);
        for (x, ch) in row.trim_end().chars().enumerate() {
            if ch == '0' {
                my_shack = (x as i32, y);
            } else if ch == '+' {
                iron_present = true;
            }
        }
    }

    let mut turn = 0;
    loop {
        turn += 1;
        let inv_line = rd(&mut r);
        if inv_line.trim().is_empty() {
            break;
        }
        let my_inv: Vec<i32> = inv_line.split_whitespace().map(|v| v.parse().unwrap()).collect();
        let _opp = rd(&mut r); // opponent inventory (unused)

        let tree_count: usize = rd(&mut r).trim().parse().unwrap();
        let mut trees: Vec<Tree> = Vec::new();
        for _ in 0..tree_count {
            let tl = rd(&mut r);
            let f: Vec<&str> = tl.split_whitespace().collect();
            trees.push(Tree {
                x: f[1].parse().unwrap(),
                y: f[2].parse().unwrap(),
                fruits: f[5].parse().unwrap(),
            });
        }

        let troll_count: usize = rd(&mut r).trim().parse().unwrap();
        let mut mine: Vec<Troll> = Vec::new();
        for _ in 0..troll_count {
            let ul = rd(&mut r);
            let f: Vec<i32> = ul.split_whitespace().map(|v| v.parse().unwrap()).collect();
            if f[1] == 0 {
                mine.push(Troll {
                    id: f[0],
                    x: f[2],
                    y: f[3],
                    cc: f[5],
                    carry: [f[8], f[9], f[10], f[11], f[12], f[13]],
                });
            }
        }

        let cmds = decide(&mine, &my_inv, &trees, my_shack, iron_present, turn);
        writeln!(out, "{}", cmds.join(";")).unwrap();
        out.flush().unwrap();
    }
}
