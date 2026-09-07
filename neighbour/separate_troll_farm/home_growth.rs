//! Compact single-cell home-tree scheduling kernel.
//!
//! Implements the mechanism described in HOME-GROWTH-PROTOCOL-2026-09-05.md: one home door
//! cell, one initially empty-handed unit, one existing tree, actual per-species health and
//! cooldown rules, action-before-growth ordering. Values are future *banked* score deltas
//! only: wood scores 4 when dropped, each future seed PICK costs 1, and the seed already
//! spent on the existing tree is sunk. Nothing here is integrated into the bot.

/// Actual match length; `turns_left` may never exceed it.
pub const TOTAL_TURNS: i32 = 300;
const WOOD_POINTS: i32 = 4;
const SEED_COST: i32 = 1;
const MAX_SIZE: i32 = 4;
const MAX_HEALTH: i32 = 20;
const MAX_CD: i32 = 9;
const STATES: usize = ((MAX_SIZE + 1) * (MAX_HEALTH + 1) * (MAX_CD + 1)) as usize;
const INF: i32 = i32::MAX / 4;

/// Physical tree state on the home cell. Fruits are unmodelled: this kernel never picks fruit.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Tree {
    pub size: i32,
    pub health: i32,
    pub cooldown: i32,
}

/// `chosen_first_bank_turn` counts elapsed turns from now until the DROP that banks the first
/// load completes; it is `-1` when the chosen branch banks nothing before the deadline.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Decision {
    pub wait: bool,
    pub chop_value: i32,
    pub wait_value: i32,
    pub chosen_first_bank_turn: i32,
    pub work: usize,
}

#[derive(Clone, Copy)]
struct Rules {
    base: i32,
    slope: i32,
    reset: i32,
}

fn rules(kind: u8, near_water: bool) -> Option<Rules> {
    let (base, slope, cooldown, boost) = match kind {
        0 | 1 => (4, 2, 8, 5), // PLUM, LEMON
        2 => (8, 3, 9, 7),     // APPLE
        3 => (2, 1, 6, 2),     // BANANA
        _ => return None,
    };
    Some(Rules {
        base,
        slope,
        reset: cooldown - if near_water { boost } else { 0 },
    })
}

impl Rules {
    fn full_health(&self, size: i32) -> i32 {
        self.base + self.slope * size
    }

    /// One end-of-turn growth tick, applied after the unit's action.
    /// A size-4 tree only burns cooldown here (fruit is unmodelled), so its cooldown is
    /// normalized to 0; that is exact for this model and shrinks the state space.
    fn tick(&self, tree: Tree) -> Tree {
        let Tree {
            mut size,
            mut health,
            mut cooldown,
        } = tree;
        if cooldown > 0 {
            cooldown -= 1;
        }
        if cooldown == 0 && size < MAX_SIZE {
            size += 1;
            health += self.slope;
            cooldown = self.reset;
        }
        if size >= MAX_SIZE {
            cooldown = 0;
        }
        Tree {
            size,
            health,
            cooldown,
        }
    }

    /// State of a just-planted tree at the start of the next actionable turn: the PLANT turn's
    /// own growth tick is included, and no first action is forced afterwards.
    fn fresh(&self) -> Tree {
        self.tick(Tree {
            // Actual PLANT creates size zero; this turn's growth produces size
            // one with a FULL reset cooldown, not reset minus one.
            size: 0,
            health: self.base,
            cooldown: 0,
        })
    }

    fn normalize(&self, tree: Tree) -> Tree {
        let mut tree = tree;
        if tree.size >= MAX_SIZE {
            tree.cooldown = 0;
        }
        tree
    }
}

fn encode(tree: Tree) -> usize {
    debug_assert!(tree.size >= 0 && tree.size <= MAX_SIZE);
    debug_assert!(tree.health >= 0 && tree.health <= MAX_HEALTH);
    debug_assert!(tree.cooldown >= 0 && tree.cooldown <= MAX_CD);
    ((tree.size * (MAX_HEALTH + 1) + tree.health) * (MAX_CD + 1) + tree.cooldown) as usize
}

fn decode(index: usize) -> Tree {
    let index = index as i32;
    Tree {
        size: index / ((MAX_HEALTH + 1) * (MAX_CD + 1)),
        health: (index / (MAX_CD + 1)) % (MAX_HEALTH + 1),
        cooldown: index % (MAX_CD + 1),
    }
}

/// Earliest elapsed turn at which the tree dies yielding each collected wood amount 1..=4
/// (index `y - 1`), or `INF`. Breadth-first over WAIT/CHOP: every action costs one turn, so
/// the first arrival at a physical state dominates every later arrival at it. `forced` pins
/// the very first action (`Some(true)` = CHOP, `Some(false)` = WAIT).
fn profile(
    r: &Rules,
    start: Tree,
    chop: i32,
    cap: i32,
    horizon: i32,
    forced: Option<bool>,
    work: &mut usize,
) -> [i32; 4] {
    let mut earliest = [INF; 4];
    if horizon < 1 {
        return earliest;
    }
    let mut dist = [INF; STATES];
    let mut queue: Vec<usize> = Vec::with_capacity(64);
    // Apply a forced root action before deduplicating states. In particular,
    // WAIT on a mature tree is a valid one-turn self-loop, not a dead branch.
    let (initial, elapsed) = if let Some(do_chop) = forced {
        let mut next = start;
        if do_chop {
            next.health -= chop;
            if next.health <= 0 {
                earliest[(next.size.min(cap) - 1) as usize] = 1;
                return earliest;
            }
        }
        (r.tick(next), 1)
    } else {
        (r.normalize(start), 0)
    };
    let root = encode(initial);
    dist[root] = elapsed;
    queue.push(root);
    let mut head = 0;
    while head < queue.len() {
        let state = queue[head];
        head += 1;
        *work += 1;
        let elapsed = dist[state];
        if elapsed >= horizon {
            continue;
        }
        let tree = decode(state);
        for do_chop in [false, true] {
            let mut next = tree;
            if do_chop {
                next.health -= chop;
                if next.health <= 0 {
                    // Wood is taken from the size held before the growth tick.
                    let y = (next.size.min(cap) as usize) - 1;
                    if elapsed + 1 < earliest[y] {
                        earliest[y] = elapsed + 1;
                    }
                    continue;
                }
            }
            let next = encode(r.tick(next));
            if dist[next] > elapsed + 1 {
                dist[next] = elapsed + 1;
                queue.push(next);
            }
        }
    }
    earliest
}

/// V439's fixed PICK priority: BANANA, PLUM, LEMON, APPLE. It makes the identity of every
/// future seed deterministic, so no four-dimensional inventory search is needed.
const PRIORITY: [u8; 4] = [3, 0, 1, 2];
/// Every complete cycle costs PICK + PLANT + at least one chop turn + DROP.
const MAX_CYCLES: i32 = TOTAL_TURNS / 4;

/// Cycle cost and banked reward per collected wood amount for one species freshly planted on
/// this same cell, including the PLANT turn's own growth tick.
fn fresh_cycle(r: &Rules, chop: i32, cap: i32, turns_left: i32, work: &mut usize) -> ([i32; 4], [i32; 4]) {
    let fresh = profile(r, r.fresh(), chop, cap, turns_left - 3, None, work);
    let mut cycle = [INF; 4];
    let mut reward = [0i32; 4];
    for y in 0..4 {
        if fresh[y] < INF {
            cycle[y] = fresh[y] + 3; // PICK + PLANT + kill turns + DROP
            reward[y] = WOOD_POINTS * (y as i32 + 1) - SEED_COST;
        }
    }
    (reward, cycle)
}

/// `F[0][t]`: best banked score obtainable in `t` turns from the whole fixed seed `sequence`.
/// `F[i][t]` may only complete a cycle of `sequence[i]` and continue with `F[i + 1]`, or stop
/// and bank nothing further; `F[n] = 0`. Rows are built in reverse with two rolling buffers.
fn stock_dp(
    profiles: &[Option<([i32; 4], [i32; 4])>; 4],
    sequence: &[u8],
    t_max: i32,
    work: &mut usize,
) -> Vec<i32> {
    let width = (t_max + 1) as usize;
    let mut next = vec![0i32; width];
    let mut cur = vec![0i32; width];
    for &k in sequence.iter().rev() {
        let (reward, cycle) = profiles[k as usize].expect("profile for every queued seed");
        // Each row starts at zero, never at a copy of the following row: copying would let the
        // unit skip this higher-priority seed to reach a later, faster species.
        for v in cur.iter_mut() {
            *v = 0;
        }
        for t in 0..width {
            for y in 0..4 {
                *work += 1;
                let c = cycle[y];
                if c < INF && (c as usize) <= t {
                    let value = reward[y] + next[t - c as usize];
                    if value > cur[t] {
                        cur[t] = value;
                    }
                }
            }
        }
        std::mem::swap(&mut cur, &mut next);
    }
    next
}

/// Best (value, first bank turn) for one root branch. A later kill of the same yield is
/// dominated because `f` is non-decreasing in remaining time, so only earliest kills are tried.
fn root_best(earliest: &[i32; 4], f: &[i32], turns_left: i32) -> (i32, i32) {
    let mut best = 0;
    let mut bank = -1;
    for y in 0..4 {
        if earliest[y] >= INF {
            continue;
        }
        let drop_at = earliest[y] + 1;
        if drop_at > turns_left {
            continue;
        }
        let value = WOOD_POINTS * (y as i32 + 1) + f[(turns_left - drop_at) as usize];
        if value > best || (value == best && bank >= 0 && drop_at < bank) {
            best = value;
            bank = drop_at;
        }
    }
    (best, bank)
}

/// Decide WAIT vs CHOP for the existing home tree against the finite four-species seed bank
/// `seeds`, indexed PLUM, LEMON, APPLE, BANANA. Returns `None` for unsupported or physically
/// unreachable inputs; callers must fall back to unchanged baseline behaviour.
pub fn choose_stock(
    kind: u8,
    near_water: bool,
    chop: i32,
    capacity: i32,
    tree: Tree,
    seeds: [i32; 4],
    turns_left: i32,
) -> Option<Decision> {
    let r = rules(kind, near_water)?;
    if chop <= 0 || capacity <= 0 || seeds.iter().any(|&s| s < 0) {
        return None;
    }
    if turns_left <= 0 || turns_left > TOTAL_TURNS {
        return None;
    }
    if tree.size < 1 || tree.size > MAX_SIZE {
        return None;
    }
    if tree.health < 1 || tree.health > r.full_health(tree.size) {
        return None;
    }
    if tree.cooldown < 0 || tree.cooldown > r.reset {
        return None;
    }
    let cap = capacity.min(MAX_SIZE);
    let mut work = 0usize;

    // Fixed future seed identity sequence, bounded by the deadline and by 75 whole cycles.
    // Widened to i64 so arbitrarily large stocks cannot overflow the sum.
    let total: i64 = seeds.iter().map(|&s| s as i64).sum();
    let n = total.min((turns_left / 4) as i64).min(MAX_CYCLES as i64) as usize;
    let mut sequence: Vec<u8> = Vec::with_capacity(n);
    for k in PRIORITY {
        let mut left = seeds[k as usize] as i64;
        while left > 0 && sequence.len() < n {
            sequence.push(k);
            left -= 1;
        }
    }
    let mut profiles: [Option<([i32; 4], [i32; 4])>; 4] = [None; 4];
    for &k in &sequence {
        if profiles[k as usize].is_none() {
            let rk = rules(k, near_water)?;
            profiles[k as usize] = Some(fresh_cycle(&rk, chop, cap, turns_left, &mut work));
        }
    }
    let f = stock_dp(&profiles, &sequence, turns_left, &mut work);

    let start = r.normalize(tree);
    let waiting = profile(&r, start, chop, cap, turns_left - 1, Some(false), &mut work);
    let chopping = profile(&r, start, chop, cap, turns_left - 1, Some(true), &mut work);
    let (wait_value, wait_bank) = root_best(&waiting, &f, turns_left);
    let (chop_value, chop_bank) = root_best(&chopping, &f, turns_left);

    let wait = wait_value >= chop_value + 1; // strict gain required; CHOP on ties
    Some(Decision {
        wait,
        chop_value,
        wait_value,
        chosen_first_bank_turn: if wait { wait_bank } else { chop_bank },
        work,
    })
}

/// Single-species compatibility case: the whole bank is `seeds` of the planted tree's own kind.
pub fn choose(
    kind: u8,
    near_water: bool,
    chop: i32,
    capacity: i32,
    tree: Tree,
    seeds: i32,
    turns_left: i32,
) -> Option<Decision> {
    rules(kind, near_water)?;
    if seeds < 0 {
        return None;
    }
    let mut stock = [0i32; 4];
    stock[kind as usize] = seeds;
    choose_stock(kind, near_water, chop, capacity, tree, stock, turns_left)
}

/// Minimal test-only surface for later differential checks against the planning model.
/// The production path never exposes or embeds a forward model.
#[cfg(test)]
pub(crate) mod hooks {
    use super::*;

    pub fn tick(kind: u8, near_water: bool, tree: Tree) -> Option<Tree> {
        rules(kind, near_water).map(|r| r.tick(tree))
    }

    pub fn fresh(kind: u8, near_water: bool) -> Option<Tree> {
        rules(kind, near_water).map(|r| r.fresh())
    }

    pub fn kill_profile(
        kind: u8,
        near_water: bool,
        start: Tree,
        chop: i32,
        cap: i32,
        horizon: i32,
        forced: Option<bool>,
    ) -> Option<[i32; 4]> {
        let r = rules(kind, near_water)?;
        let mut work = 0;
        Some(profile(
            &r,
            start,
            chop,
            cap.min(MAX_SIZE),
            horizon,
            forced,
            &mut work,
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeMap;

    // Independent copy of the engine table (base, slope, cooldown, water boost) so the naive
    // reference simulation never borrows production arithmetic.
    const P: [(i32, i32, i32, i32); 4] = [(4, 2, 8, 5), (4, 2, 8, 5), (8, 3, 9, 7), (2, 1, 6, 2)];

    fn params(kind: u8, water: bool) -> (i32, i32, i32) {
        let (b, s, c, w) = P[kind as usize];
        (b, s, c - if water { w } else { 0 })
    }

    fn t_tick(p: (i32, i32, i32), t: (i32, i32, i32)) -> (i32, i32, i32) {
        let (mut sz, mut h, mut cd) = t;
        if cd > 0 {
            cd -= 1;
        }
        if cd == 0 && sz < 4 {
            sz += 1;
            h += p.1;
            cd = p.2;
        }
        if sz >= 4 {
            cd = 0;
        }
        (sz, h, cd)
    }

    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct N {
        tree: Option<(i32, i32, i32)>,
        wood: i32,
        held: bool,
        seeds: i32,
        t: i32,
    }

    /// Exhaustive per-turn action search over the same single-cell model, with no reference to
    /// `profile` or `seed_dp`. Unbanked wood is worth nothing.
    fn naive(p: (i32, i32, i32), chop: i32, cap: i32, s: N, m: &mut BTreeMap<N, i32>) -> i32 {
        if s.t <= 0 {
            return 0;
        }
        if let Some(v) = m.get(&s) {
            return *v;
        }
        let mut best = naive(p, chop, cap, N { t: s.t - 1, ..s }, m); // WAIT / idle
        if let Some((sz, h, cd)) = s.tree {
            best = naive(p, chop, cap, N { tree: Some(t_tick(p, (sz, h, cd))), t: s.t - 1, ..s }, m);
            let hurt = h - chop;
            let after = if hurt <= 0 {
                N { tree: None, wood: sz.min(cap), t: s.t - 1, ..s }
            } else {
                N { tree: Some(t_tick(p, (sz, hurt, cd))), t: s.t - 1, ..s }
            };
            best = best.max(naive(p, chop, cap, after, m));
        } else if s.wood > 0 {
            best = best.max(4 * s.wood + naive(p, chop, cap, N { wood: 0, t: s.t - 1, ..s }, m));
        } else if s.held {
            let f = t_tick(p, (0, p.0, 0));
            best = best.max(naive(p, chop, cap, N { tree: Some(f), held: false, t: s.t - 1, ..s }, m));
        } else if s.seeds > 0 {
            best = best.max(-1 + naive(p, chop, cap, N { held: true, seeds: s.seeds - 1, t: s.t - 1, ..s }, m));
        }
        m.insert(s, best);
        best
    }

    fn naive_root(p: (i32, i32, i32), chop: i32, cap: i32, tr: (i32, i32, i32), seeds: i32, t: i32, do_chop: bool) -> i32 {
        let (sz, h, cd) = tr;
        let s = if do_chop && h - chop <= 0 {
            N { tree: None, wood: sz.min(cap), held: false, seeds, t: t - 1 }
        } else {
            let next = if do_chop { (sz, h - chop, cd) } else { (sz, h, cd) };
            N { tree: Some(t_tick(p, next)), wood: 0, held: false, seeds, t: t - 1 }
        };
        naive(p, chop, cap, s, &mut BTreeMap::new())
    }

    #[test]
    fn plant_tick_and_growth_ordering_match_engine_rules() {
        // PLANT creates size zero; the same-turn growth resets its cooldown.
        assert_eq!(hooks::fresh(3, false).unwrap(), Tree { size: 1, health: 3, cooldown: 6 });
        // Apple near water resets to 2 and gains base 8 + slope 3.
        assert_eq!(hooks::fresh(2, true).unwrap(), Tree { size: 1, health: 11, cooldown: 2 });
        // Cooldown reaching zero grows the tree and adds slope health.
        assert_eq!(
            hooks::tick(0, false, Tree { size: 1, health: 6, cooldown: 1 }).unwrap(),
            Tree { size: 2, health: 8, cooldown: 8 }
        );
        // Mature trees only burn cooldown, normalized to zero.
        assert_eq!(
            hooks::tick(0, false, Tree { size: 4, health: 12, cooldown: 3 }).unwrap(),
            Tree { size: 4, health: 12, cooldown: 0 }
        );
        for kind in 0..4u8 {
            for water in [false, true] {
                let (b, s, reset) = params(kind, water);
                assert_eq!(hooks::fresh(kind, water).unwrap(), Tree { size: 1, health: b + s, cooldown: reset });
            }
        }
    }

    #[test]
    fn wood_is_taken_before_the_growth_tick_and_capped_by_capacity() {
        let dying = Tree { size: 1, health: 3, cooldown: 1 };
        // Chopping first kills at size 1 even though the tick would have grown it.
        let chop_first = hooks::kill_profile(3, false, dying, 3, 2, 20, Some(true)).unwrap();
        assert_eq!(chop_first[0], 1);
        assert_eq!(chop_first[1], INF);
        // Waiting first grows it, and the size-2 kill lands on turn 3.
        let wait_first = hooks::kill_profile(3, false, dying, 3, 2, 20, Some(false)).unwrap();
        assert_eq!(wait_first[0], INF);
        assert_eq!(wait_first[1], 3);
        // Capacity clamps the credited yield, never the physical size.
        let capped = hooks::kill_profile(3, false, dying, 3, 1, 20, Some(false)).unwrap();
        assert_eq!(capped[0], 3);
        assert_eq!(capped[1], INF);
    }

    #[test]
    fn unsupported_or_unreachable_inputs_are_rejected() {
        let ok = Tree { size: 1, health: 3, cooldown: 1 };
        assert!(choose(4, false, 2, 2, ok, 0, 50).is_none());
        assert!(choose(3, false, 0, 2, ok, 0, 50).is_none());
        assert!(choose(3, false, 2, 0, ok, 0, 50).is_none());
        assert!(choose(3, false, 2, 2, ok, -1, 50).is_none());
        assert!(choose(3, false, 2, 2, ok, 0, 0).is_none());
        assert!(choose(3, false, 2, 2, ok, 0, TOTAL_TURNS + 1).is_none());
        assert!(choose(3, false, 2, 2, Tree { size: 5, health: 3, cooldown: 0 }, 0, 50).is_none());
        assert!(choose(3, false, 2, 2, Tree { size: 1, health: 0, cooldown: 0 }, 0, 50).is_none());
        assert!(choose(3, false, 2, 2, Tree { size: 1, health: 4, cooldown: 0 }, 0, 50).is_none());
        assert!(choose(3, false, 2, 2, Tree { size: 1, health: 3, cooldown: 7 }, 0, 50).is_none());
        assert!(choose(3, false, 2, 2, ok, 0, 50).is_some());
    }

    #[test]
    fn unbanked_wood_earns_nothing_and_the_deadline_is_the_actual_one() {
        // One turn is enough to kill but not to DROP.
        let d = choose(3, false, 3, 2, Tree { size: 1, health: 3, cooldown: 5 }, 0, 1).unwrap();
        assert_eq!((d.chop_value, d.wait_value, d.chosen_first_bank_turn), (0, 0, -1));
        assert!(!d.wait);
        // Two turns bank exactly one load and nothing more.
        let d = choose(3, false, 3, 2, Tree { size: 1, health: 3, cooldown: 5 }, 5, 2).unwrap();
        assert_eq!((d.chop_value, d.chosen_first_bank_turn), (4, 2));
    }

    #[test]
    fn extra_seeds_add_value_monotonically_and_never_overdraft() {
        let tree = Tree { size: 1, health: 3, cooldown: 5 };
        let v = |seeds| choose(3, false, 3, 2, tree, seeds, 40).unwrap().chop_value;
        let (z, one, two, many) = (v(0), v(1), v(2), v(50));
        assert!(one > z && two > one);
        // Time, not the seed count, binds once enough seeds are held.
        assert_eq!(many, v(9));
        // Each future cycle nets at most 4*4 - 1 points, so seeds cannot be double-spent.
        assert!(one - z <= 15 && two - one <= 15);
    }

    #[test]
    fn root_branch_values_match_independent_exhaustive_simulation() {
        let mut checked = 0;
        for kind in 0..4u8 {
            for water in [false, true] {
                let p = params(kind, water);
                let states = [(1, p.0 + p.1, p.2), (2, 1, 1), (3, p.0 + 3 * p.1, 0)];
                for chop in [1, 3] {
                    for cap in [1, 2, 3] {
                        for seeds in [0, 2] {
                            for t in [9, 13] {
                                for tr in states {
                                    let tree = Tree { size: tr.0, health: tr.1, cooldown: tr.2 };
                                    let d = choose(kind, water, chop, cap, tree, seeds, t).unwrap();
                                    assert_eq!(d.chop_value, naive_root(p, chop, cap, tr, seeds, t, true));
                                    assert_eq!(d.wait_value, naive_root(p, chop, cap, tr, seeds, t, false));
                                    assert_eq!(d.wait, d.wait_value > d.chop_value);
                                    assert!(d.work > 0);
                                    checked += 1;
                                }
                            }
                        }
                    }
                }
            }
        }
        assert_eq!(checked, 4 * 2 * 2 * 3 * 2 * 2 * 3);
    }

    #[test]
    fn waiting_is_strictly_better_in_an_executed_example() {
        // Dry banana, size 1, one turn from growing, chop power 3 kills it outright now.
        let tree = Tree { size: 1, health: 3, cooldown: 1 };
        let d = choose(3, false, 3, 2, tree, 0, 10).unwrap();
        assert_eq!(d.chop_value, 4); // kill at turn 1, bank 1 wood at turn 2
        assert_eq!(d.wait_value, 8); // grow, kill at turn 3, bank 2 wood at turn 4
        assert!(d.wait);
        assert_eq!(d.chosen_first_bank_turn, 4);
        assert_eq!(d.wait_value, naive_root(params(3, false), 3, 2, (1, 3, 1), 0, 10, false));
    }

    #[test]
    fn ties_prefer_chop_and_report_the_earlier_bank_turn() {
        // A mature tree gains nothing from waiting, so both branches tie and CHOP wins.
        let tree = Tree { size: 4, health: 6, cooldown: 0 };
        let d = choose(3, false, 6, 3, tree, 0, 30).unwrap();
        assert_eq!(d.wait_value, d.chop_value);
        assert!(!d.wait);
        assert_eq!(d.chosen_first_bank_turn, 2);
    }

    const ORDER: [usize; 4] = [3, 0, 1, 2];

    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
    struct M {
        tree: Option<(u8, i32, i32, i32)>,
        wood: i32,
        held: Option<u8>,
        seeds: [i32; 4],
        t: i32,
    }

    /// Multi-species reference enumeration. It re-derives species growth from its own table and
    /// may only PICK the highest-priority stocked seed, never a later one.
    fn naive_stock(water: bool, chop: i32, cap: i32, s: M, m: &mut BTreeMap<M, i32>) -> i32 {
        if s.t <= 0 {
            return 0;
        }
        if let Some(v) = m.get(&s) {
            return *v;
        }
        let mut best = naive_stock(water, chop, cap, M { t: s.t - 1, ..s }, m);
        if let Some((k, sz, h, cd)) = s.tree {
            let p = params(k, water);
            let (a, b, c) = t_tick(p, (sz, h, cd));
            best = naive_stock(water, chop, cap, M { tree: Some((k, a, b, c)), t: s.t - 1, ..s }, m);
            let hurt = h - chop;
            let after = if hurt <= 0 {
                M { tree: None, wood: sz.min(cap), t: s.t - 1, ..s }
            } else {
                let (a, b, c) = t_tick(p, (sz, hurt, cd));
                M { tree: Some((k, a, b, c)), t: s.t - 1, ..s }
            };
            best = best.max(naive_stock(water, chop, cap, after, m));
        } else if s.wood > 0 {
            best = best.max(4 * s.wood + naive_stock(water, chop, cap, M { wood: 0, t: s.t - 1, ..s }, m));
        } else if let Some(k) = s.held {
            let p = params(k, water);
            let (a, b, c) = t_tick(p, (0, p.0, 0));
            best = best.max(naive_stock(water, chop, cap, M { tree: Some((k, a, b, c)), held: None, t: s.t - 1, ..s }, m));
        } else if let Some(&k) = ORDER.iter().find(|&&k| s.seeds[k] > 0) {
            let mut seeds = s.seeds;
            seeds[k] -= 1;
            best = best.max(-1 + naive_stock(water, chop, cap, M { held: Some(k as u8), seeds, t: s.t - 1, ..s }, m));
        }
        m.insert(s, best);
        best
    }

    fn naive_stock_root(kind: u8, water: bool, chop: i32, cap: i32, tr: (i32, i32, i32), seeds: [i32; 4], t: i32, do_chop: bool) -> i32 {
        let p = params(kind, water);
        let (sz, h, cd) = tr;
        let s = if do_chop && h - chop <= 0 {
            M { tree: None, wood: sz.min(cap), held: None, seeds, t: t - 1 }
        } else {
            let next = if do_chop { (sz, h - chop, cd) } else { (sz, h, cd) };
            let (a, b, c) = t_tick(p, next);
            M { tree: Some((kind, a, b, c)), wood: 0, held: None, seeds, t: t - 1 }
        };
        naive_stock(water, chop, cap, s, &mut BTreeMap::new())
    }

    #[test]
    fn zero_and_single_species_stocks_reproduce_the_compatibility_wrapper() {
        let tree = Tree { size: 1, health: 3, cooldown: 5 };
        assert_eq!(choose_stock(3, false, 3, 2, tree, [0; 4], 40), choose(3, false, 3, 2, tree, 0, 40));
        assert_eq!(choose_stock(3, false, 3, 2, tree, [0, 0, 0, 4], 40), choose(3, false, 3, 2, tree, 4, 40));
    }

    #[test]
    fn huge_stocks_saturate_at_the_cycle_cap_and_negative_stocks_are_rejected() {
        let tree = Tree { size: 1, health: 3, cooldown: 5 };
        let huge = choose_stock(3, false, 3, 2, tree, [i32::MAX; 4], 40).unwrap();
        // Only the highest-priority species is ever reached, and only floor(T / 4) cycles fit.
        assert_eq!(huge, choose_stock(3, false, 3, 2, tree, [0, 0, 0, i32::MAX], 40).unwrap());
        assert_eq!(huge, choose_stock(3, false, 3, 2, tree, [0, 0, 0, 40 / 4], 40).unwrap());
        assert!(choose_stock(3, false, 3, 2, tree, [0, -1, 0, 0], 40).is_none());
        assert!(choose_stock(4, false, 3, 2, tree, [0; 4], 40).is_none());
        assert!(choose_stock(4, false, 3, 2, tree, [0, -1, 0, 0], 40).is_none());
    }

    #[test]
    fn a_slow_preferred_seed_may_not_be_skipped_for_a_faster_later_species() {
        // Near water APPLE resets in 2 turns and BANANA in 4, so the lower-priority APPLE is the
        // faster grower here; the stocked BANANA must still be picked first.
        let tree = Tree { size: 4, health: 20, cooldown: 0 };
        let apple_only = choose_stock(2, true, 20, 4, tree, [0, 0, 1, 0], 12).unwrap();
        let banana_first = choose_stock(2, true, 20, 4, tree, [0, 0, 1, 1], 12).unwrap();
        assert!(banana_first.chop_value < apple_only.chop_value);
        assert_eq!(apple_only.chop_value, naive_stock_root(2, true, 20, 4, (4, 20, 0), [0, 0, 1, 0], 12, true));
        assert_eq!(banana_first.chop_value, naive_stock_root(2, true, 20, 4, (4, 20, 0), [0, 0, 1, 1], 12, true));
    }

    #[test]
    fn mixed_finite_banks_match_the_independent_priority_ordered_enumeration() {
        let mut checked = 0;
        for (kind, water, bank) in [(2u8, true, [0, 0, 1, 1]), (3u8, false, [0, 1, 0, 2]), (1u8, false, [0, 2, 1, 0])] {
            let p = params(kind, water);
            for tr in [(1, p.0 + p.1, p.2), (2, 1, 0)] {
                for chop in [2, 5] {
                    for cap in [1, 3] {
                        for t in 9..=16 {
                            let tree = Tree { size: tr.0, health: tr.1, cooldown: tr.2 };
                            let d = choose_stock(kind, water, chop, cap, tree, bank, t).unwrap();
                            assert_eq!(d.chop_value, naive_stock_root(kind, water, chop, cap, tr, bank, t, true));
                            assert_eq!(d.wait_value, naive_stock_root(kind, water, chop, cap, tr, bank, t, false));
                            checked += 1;
                        }
                    }
                }
            }
        }
        assert_eq!(checked, 3 * 2 * 2 * 2 * 8);
    }
}
