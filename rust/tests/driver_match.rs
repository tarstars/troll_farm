use troll_farm::game::driver::play_match;

#[test]
fn wait_vs_wait_full_run_scores_starting_inventory() {
    // Nobody acts: game runs all turns (plants never chopped away); score = starting
    // inventory (mapgen randomizes the 4 fruit counts per seed; seed=1 -> 5+4+5+7=21)
    // + 0 wood = 21 for both sides; no crashes.
    let r = play_match("WAIT", "WAIT", 1, 40);
    assert_eq!(r.turns, 40);
    assert_eq!(r.scores, [21, 21]);
    assert_eq!(r.fruit, [21, 21]);
    assert_eq!(r.wood, [0, 0]);
    assert_eq!(r.crashed, [false, false]);
    // deterministic: same seed twice, identical result
    let r2 = play_match("WAIT", "WAIT", 1, 40);
    assert_eq!((r.scores, r.turns), (r2.scores, r2.turns));
}

#[test]
fn crashed_side_is_flagged_and_plays_wait() {
    // /bin/false exits immediately -> EOF/broken pipe on first exchange -> crash flag,
    // game still completes with that side WAITing.
    let r = play_match("/bin/false", "WAIT", 2, 10);
    assert!(r.crashed[0]);
    assert!(!r.crashed[1]);
    assert_eq!(r.turns, 10);
    assert_eq!(r.scores, [24, 24]); // nobody acted (seed=2 starting inventory 2+5+9+8=24)
}
