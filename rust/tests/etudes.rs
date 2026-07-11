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
