use troll_farm::game::mapgen::generate_bronze;
use troll_farm::strategies::norxondor_research::{
    proposed_spec, resident_three_worker_commands, resident_three_worker_commands_with_profile,
    ResidentFundingProfile,
};

#[test]
fn ladder_waits_for_stage_floor() {
    assert_eq!(proposed_spec(1, &[4, 5, 2, 0, 2, 0], true), None);
}

#[test]
fn ladder_clamps_componentwise_max_affordable_spec() {
    assert_eq!(
        proposed_spec(1, &[20, 10, 10, 0, 17, 0], true),
        Some((3, 3, 2, 2))
    );
    assert_eq!(
        proposed_spec(2, &[18, 30, 6, 0, 11, 0], true),
        Some((4, 5, 2, 2))
    );
}

#[test]
fn no_iron_map_uses_the_stage_chop_cap() {
    assert_eq!(
        proposed_spec(3, &[12, 12, 4, 0, 0, 0], false),
        Some((3, 3, 1, 3))
    );
}

#[test]
fn fifth_worker_is_the_terminal_rung() {
    assert_eq!(proposed_spec(5, &[100; 6], true), None);
}

#[test]
fn resident_wrapper_removes_training_after_worker_three() {
    let mut game = generate_bronze(0);
    let mut extra = game.units[0].clone();
    extra.id = game.next_id;
    game.next_id += 1;
    game.units.push(extra.clone());
    extra.id = game.next_id;
    game.next_id += 1;
    game.units.push(extra);
    let commands = vec!["WAIT".to_string(), "TRAIN 3 3 3 3".to_string()];
    assert_eq!(
        resident_three_worker_commands(commands, &game, 0),
        vec!["WAIT".to_string()]
    );
}

#[test]
fn delayed_profile_preserves_commands_but_suppresses_training() {
    let game = generate_bronze(0);
    let commands = vec!["MOVE 0 1 1".to_string(), "TRAIN 3 3 3 3".to_string()];
    assert_eq!(
        resident_three_worker_commands_with_profile(
            commands,
            &game,
            0,
            ResidentFundingProfile::DelayedTwo { start_turn: 10 },
        ),
        vec!["MOVE 0 1 1".to_string()]
    );
}
