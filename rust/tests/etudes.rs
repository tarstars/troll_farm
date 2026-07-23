use troll_farm::etudes::actions::{joint_actions, troll_actions};
use troll_farm::etudes::oracle::{forced_verdict, Verdict};
use troll_farm::etudes::situation::{from_text, to_text, Situation};

#[test]
fn situation_roundtrip() {
    let text = "\
MAP 5 3
.0..1
.....
..+..
INV0 0 0 0 2 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 3 1 2 4 0 0
TURN 10
SCORES 0 0
HORIZON 6
PROVE -";
    let s = from_text(text);
    assert_eq!(s.horizon, 6);
    assert_eq!(s.prove_side, None);
    assert_eq!(s.state.units.len(), 1);
    assert_eq!(s.state.plants.len(), 1);
    assert_eq!(s.state.units[0].chop, 2);
    // round-trip: parsing the re-serialized text yields the same fields
    let s2 = from_text(&to_text(&s));
    assert_eq!(s2.state.units, s.state.units);
    assert_eq!(s2.state.plants, s.state.plants);
    assert_eq!(s2.state.inventories, s.state.inventories);
    assert_eq!(s2.state.turn, s.state.turn);
    assert_eq!(s2.horizon, s.horizon);
}

#[test]
fn actions_pruned_and_canonical() {
    let s = from_text(
        "\
MAP 5 3
.0..1
.....
..B..
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 4
PROVE -",
    )
    .state;
    let acts = troll_actions(&s, &s.units[0]);
    // sensible only: WAIT + a MOVE toward the tree + a MOVE toward the shack; NOT 8 blind dirs;
    // no CHOP (not on the tree). canonical (sorted, deduped).
    assert!(acts.contains(&"WAIT 0".to_string()));
    assert!(acts.iter().any(|a| a.starts_with("MOVE 0 ")));
    assert!(!acts.contains(&"CHOP 0".to_string())); // unit not on a tree
    assert_eq!(acts, {
        let mut v = acts.clone();
        v.sort();
        v.dedup();
        v
    }); // canonical
        // one-unit player → joint == each single action wrapped
    let j = joint_actions(&s, 0);
    assert_eq!(j.len(), acts.len());
    assert!(j.iter().all(|c| c.len() == 1));
}

#[test]
fn oracle_forced_win_by_felling() {
    // our troll (chop 2) starts ON a size-2 banana (health 4 = 2 chops); opponent has no unit.
    // PLANT cooldown=6 (a settled, freshly-at-this-size tree — NOT 0: cooldown==0 is a
    // "grow on the very next tick" trigger in tick_plants, not a quiescent state, and would
    // regrow the tree — size 2->3, health increases from 2 to 3 — after the first chop,
    // forcing a 3rd chop and
    // leaving no turns to bank the wood; confirmed by direct engine replay during development).
    // H=4 is enough for CHOP,CHOP (fells it, +2 wood carried, capped by cc=2) then MOVE,DROP
    // (bank it into inventory — recompute_scores reads inventories, not carry) — score-diff > 0
    // forced.
    let s = from_text(
        "\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0",
    );
    assert!(matches!(
        forced_verdict(&s),
        Verdict::ForcedWin { side: 0, .. }
    ));
}

#[test]
fn oracle_proof_replays_valid() {
    // same fixture as oracle_forced_win_by_felling: the extracted proof must independently
    // replay valid against a brute-force opponent that tries every possible response at every
    // ply (not just the search's own pruned/memoized path) — every leaf strictly favors side 0.
    let s = from_text(
        "\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0",
    );
    let v = forced_verdict(&s);
    assert!(matches!(v, Verdict::ForcedWin { .. }));
    assert!(troll_farm::etudes::oracle::replay_proof(&s, &v));
}

#[test]
fn oracle_replay_proof_rejects_a_bogus_line() {
    // extra (not in the plan): replay_proof must not be vacuously true. Same fixture, but a
    // bogus proof line (WAIT the whole time: never fells the tree, banks nothing) must fail —
    // otherwise replay_proof would be a no-op check that always returns true.
    use troll_farm::etudes::oracle::{replay_proof, Proof, Verdict};
    let s = from_text(
        "\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0",
    );
    let bogus = Verdict::ForcedWin {
        side: 0,
        proof: Proof {
            line: vec![
                ("WAIT 0".to_string(), 0),
                ("WAIT 0".to_string(), 0),
                ("WAIT 0".to_string(), 0),
                ("WAIT 0".to_string(), 0),
            ],
        },
    };
    assert!(
        !replay_proof(&s, &bogus),
        "a bogus all-WAIT proof must NOT replay valid"
    );
}

#[test]
fn oracle_toolarge() {
    // 2 units/side on an open map with 4 trees (rich branching: each troll has ~5-6 sensible
    // MOVE targets + WAIT) and H=8 — the (x-action, y-action) transition count blows well past
    // NODE_BUDGET long before depth 0, so the search must abort and report TooLarge rather than
    // exhaustively completing (or hanging).
    let s = from_text(
        "\
MAP 9 7
0.......1
.........
..B...B..
.........
..B...B..
.........
.........
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 0 0 1 2 1 2 0 0 0 0 0 0
UNIT 1 0 8 6 1 2 1 2 0 0 0 0 0 0
UNIT 2 1 8 0 1 2 1 2 0 0 0 0 0 0
UNIT 3 1 0 6 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 6
PLANT BANANA 6 2 2 4 0 6
PLANT BANANA 2 4 2 4 0 6
PLANT BANANA 6 4 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 8
PROVE 0",
    );
    assert!(matches!(forced_verdict(&s), Verdict::TooLarge));
}

#[test]
fn oracle_unresolved_or_symmetric() {
    // no reachable resource for either side in H turns → nobody forces a positive diff.
    let s = from_text(
        "\
MAP 5 3
.0..1
.....
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 1 0 1 2 1 2 0 0 0 0 0 0
UNIT 3 1 3 0 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 2 2 4 0 0
TURN 5
SCORES 0 0
HORIZON 2
PROVE -",
    );
    assert!(matches!(forced_verdict(&s), Verdict::Unresolved));
}

#[test]
fn oracle_deterministic() {
    // forced_verdict must be a pure function of the Situation: no HashSet/HashMap-iteration
    // nondeterminism (memo tables and terrain sets are only ever used via point lookups /
    // existence checks / canonical-sorted aggregation, never iterated straight into a decision)
    // may leak into the verdict OR the proof line. Reuse the felling fixture since it exercises
    // the richest output (a real ForcedWin + a 4-ply proof), not just a trivial Unresolved.
    let s = from_text(
        "\
MAP 5 3
.0..1
..B..
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 0 0 2 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 2 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 0",
    );
    let v1 = forced_verdict(&s);
    let v2 = forced_verdict(&s);
    assert_eq!(v1, v2);
}

#[test]
fn oracle_forced_win_by_felling_side_1_mirror() {
    // extra (not in the plan): every x==0/x==1 role-swap in informed_minimax, extract_line, and
    // replay_from is written as `if x==0 {(xc,yc)} else {(yc,xc)}` when calling engine::step
    // (which always wants (player0_cmds, player1_cmds) in that fixed order) -- the felling
    // fixture above only ever exercises x==0 all the way through a built Proof (PROVE=- in the
    // unresolved fixture DOES run x==1 through informed_minimax, but never reaches extract_line/
    // replay_proof since that verdict stays Unresolved). Mirror the felling geometry onto player
    // 1 (tree moved from x=2 to x=3 so the post-chop dash to shack1 at (4,0) is also exactly one
    // step, keeping the same CHOP,CHOP,MOVE,DROP timing within H=4) to cover the x==1 path
    // through extract_line and replay_proof too, not just informed_minimax.
    let s = from_text(
        "\
MAP 5 3
.0..1
.....
.....
INV0 0 0 0 0 0 0
INV1 0 0 0 0 0 0
UNIT 1 1 3 1 1 2 1 2 0 0 0 0 0 0
PLANT BANANA 3 1 2 4 0 6
TURN 5
SCORES 0 0
HORIZON 4
PROVE 1",
    );
    let v = forced_verdict(&s);
    assert!(matches!(v, Verdict::ForcedWin { side: 1, .. }), "{:?}", v);
    assert!(troll_farm::etudes::oracle::replay_proof(&s, &v));
}
