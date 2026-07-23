use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

#[test]
fn compact_gold_matches_full_default_on_dynamic_both_seat_streams() {
    for seed in 0..20 {
        for seat in 0..2 {
            let mut game = generate_bronze(seed);
            let full = GoldElite::new();
            let compact = CompactGold::new();
            let opponent = SilverBoss::new();
            let mut turns_until_end = 0;
            while game.turn <= 300 {
                let expected = full.decide(&game, seat);
                let actual = compact.decide(&game, seat);
                assert_eq!(
                    actual, expected,
                    "seed {seed}, seat {seat}, turn {}",
                    game.turn
                );
                let other = opponent.decide(&game, 1 - seat);
                if seat == 0 {
                    step(&mut game, &expected, &other);
                } else {
                    step(&mut game, &other, &expected);
                }
                if has_stalled(&game, &mut turns_until_end) {
                    break;
                }
            }
        }
    }
}
