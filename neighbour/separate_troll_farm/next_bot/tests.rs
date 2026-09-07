fn world() -> GameState {
    let rows = vec![".........".to_string(), "0.......1".to_string(), ".........".to_string()];
    let map = crate::candidate::game::protocol::parse_static_map(9, 3, &rows);
    let worker = |id, cell, cc, chop| Unit {
        id, player: 0, cell,
        stats: Stats { movement_speed: 1, carry_capacity: cc, harvest_power: 1, chop_power: chop },
        carry: [0; 6],
    };
    GameState {
        width: 9, height: 3, walkable: map.walkable, shacks: map.shacks,
        inventories: [[15, 0, 20, 5, 2, 0], [0; 6]],
        units: vec![worker(0, (1, 0), 1, 1), worker(2, (1, 1), 3, 3)],
        plants: vec![
            Plant { kind: PlantKind::Apple, cell: (1, 0), size: 4, health: 20, fruits: 3, cooldown: 0 },
            Plant { kind: PlantKind::Banana, cell: (1, 1), size: 4, health: 6, fruits: 3, cooldown: 0 },
        ],
        scores: [40, 0], turn: 150, next_id: 3,
        iron: BTreeSet::from([(3, 2)]), water: BTreeSet::new(),
    }
}

#[test]
fn lost_training_resource_does_not_prevent_existing_axe_chopping() {
    let view = world();
    let mut bot = R1faBot::new();
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
    assert!(!commands.iter().any(|c| c.starts_with("TRAIN")));
}

#[test]
fn funded_worker_is_not_bought_when_game_is_almost_over() {
    let mut view = world();
    view.turn = 299;
    view.inventories[0] = [100, 100, 100, 100, 100, 0];
    let commands = R1faBot::new().commands(&view);
    assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
}

#[test]
fn an_existing_harvest_goal_is_released_when_capital_becomes_impossible() {
    let view = world();
    let mut bot = R1faBot::new();
    bot.goals.insert(2, R1faGoal { job: R1faJob::Harvest(PlantKind::Banana), cell: (1, 1) });
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
}

#[test]
fn carried_wood_is_deposited_without_starting_another_job() {
    let mut view = world();
    view.units[1].carry[WOOD] = 3;
    let commands = R1faBot::new().commands(&view);
    assert!(commands.iter().any(|c| c == "DROP 2"), "{commands:?}");
}

#[test]
fn a_carried_seed_transaction_survives_capital_abandonment() {
    let mut view = world();
    view.units[1].cell = (2, 1);
    view.units[1].carry[BANANA] = 1;
    let mut bot = R1faBot::new();
    bot.goals.insert(2, R1faGoal { job: R1faJob::Plant(PlantKind::Banana), cell: (2, 1) });
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "PLANT 2 BANANA"), "{commands:?}");
}

#[test]
fn chop_choice_accounts_for_free_carry_and_complete_trip() {
    let mut view = world();
    view.units = vec![view.units[1].clone()];
    view.units[0].stats.carry_capacity = 1;
    view.plants = vec![
        Plant { kind: PlantKind::Banana, cell: (1, 1), size: 1, health: 3, fruits: 0, cooldown: 2 },
        Plant { kind: PlantKind::Banana, cell: (6, 1), size: 4, health: 6, fruits: 3, cooldown: 0 },
    ];
    let chosen = R1faBot::new().production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    assert_eq!(chosen, Some(R1faGoal { job: R1faJob::Chop, cell: (1, 1) }));
}

#[test]
fn paid_fruit_trip_fills_carry_before_returning() {
    let mut view = world();
    view.turn = 280; // no new planting transaction
    view.units[1].carry[BANANA] = 1;
    let mut bot = R1faBot::new();
    bot.goals.insert(2, R1faGoal { job: R1faJob::Harvest(PlantKind::Banana), cell: (1, 1) });
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "HARVEST 2"), "{commands:?}");
}

#[test]
fn final_banana_source_is_harvested_when_seed_stock_is_empty() {
    let mut view = world();
    view.inventories[0][BANANA] = 0;
    let mut bot = R1faBot::new();
    bot.planted.insert((1, 1));
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "HARVEST 2"), "{commands:?}");
}

#[test]
fn payable_source_can_be_felled_after_seed_reserve_is_banked() {
    let mut view = world();
    view.inventories[0][BANANA] = 2;
    let mut bot = R1faBot::new();
    bot.planted.insert((1, 1));
    let commands = bot.commands(&view);
    assert!(commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
}

#[test]
fn unfinished_growing_crop_is_not_cut_by_a_secondary_fallback() {
    let mut view = world();
    view.plants = vec![Plant { kind: PlantKind::Banana, cell: (1, 1), size: 1,
                              health: 3, fruits: 0, cooldown: 4 }];
    let mut bot = R1faBot::new();
    bot.planted.insert((1, 1));
    let commands = bot.commands(&view);
    assert!(!commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
}

#[test]
fn two_workers_cannot_withdraw_the_same_last_seed() {
    let mut view = world();
    view.units[0].cell = (0, 0);
    view.inventories[0] = [0, 0, 0, 1, 0, 0];
    view.plants.clear();
    let commands = R1faBot::new().commands(&view);
    assert_eq!(commands.iter().filter(|c| c.starts_with("PICK")).count(), 1, "{commands:?}");
}

#[test]
fn empty_action_set_still_emits_a_valid_wait_line() {
    let mut view = world();
    view.inventories[0] = [0; 6];
    view.plants.clear();
    assert_eq!(R1faBot::new().commands(&view), vec!["WAIT".to_string()]);
}

#[test]
fn planting_can_select_the_requesting_workers_own_cell() {
    let mut view = world();
    view.plants.clear();
    view.units[1].carry[BANANA] = 1;
    // Leave this as the only unoccupied legal planting plot. Other cells need
    // not be present in the walkable graph to demonstrate the old self-veto.
    view.walkable = BTreeSet::from([view.shacks[0], view.units[1].cell]);
    assert_eq!(R1faBot::plant_cell(&view, &view.units[1], PlantKind::Banana,
                                 &BTreeSet::new()), Some(view.units[1].cell));
    let commands = R1faBot::new().commands(&view);
    assert!(commands.iter().any(|c| c == "PLANT 2 BANANA"), "{commands:?}");
}

#[test]
fn planting_never_selects_a_shack_or_another_workers_cell() {
    let mut view = world();
    view.plants.clear();
    view.units[1].cell = view.shacks[0];
    view.units[0].cell = (1, 1);
    view.walkable = BTreeSet::from([view.shacks[0], (1, 1), view.shacks[1]]);
    assert_eq!(R1faBot::plant_cell(&view, &view.units[1], PlantKind::Banana,
                                 &BTreeSet::new()), None);
}

#[test]
fn renewable_bank_plot_can_beat_a_distant_wild_wood_trip() {
    let mut view = world();
    view.plants = vec![Plant { kind: PlantKind::Banana, cell: (7, 1), size: 4,
                              health: 6, fruits: 0, cooldown: 0 }];
    view.units[1].stats.carry_capacity = 1;
    view.units[1].stats.chop_power = 3;
    let goal = R1faBot::new().production_goal(&view, &view.units[1], &[0; 6], &BTreeSet::new());
    assert!(goal.is_some_and(|g| g.job == R1faJob::Seed(PlantKind::Banana)), "{goal:?}");
}

#[test]
fn renewable_cycle_does_not_displace_immediately_payable_wood() {
    let view = world();
    let goal = R1faBot::new().production_goal(&view, &view.units[1], &[0; 6], &BTreeSet::new());
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell: (1, 1) }));
}

fn abundant_capital_world() -> GameState {
    let mut view = world();
    // The whole third-worker bill (6 plum, 11 lemon, 3 apple, 6 iron) is banked.
    view.inventories[0] = [20, 20, 20, 5, 20, 0];
    view
}

fn deficient_capital_world() -> GameState {
    let mut view = world();
    // Only lemons are missing; one reachable lemon source keeps the bill viable.
    view.inventories[0] = [20, 0, 20, 5, 20, 0];
    view.plants = vec![
        Plant { kind: PlantKind::Banana, cell: (1, 1), size: 4, health: 6, fruits: 0, cooldown: 0 },
        Plant { kind: PlantKind::Lemon, cell: (3, 1), size: 1, health: 4, fruits: 3, cooldown: 0 },
    ];
    // The small worker banks its load, so it reserves no cell and claims no resource.
    view.units[0].carry[WOOD] = 1;
    view.units[0].stats.chop_power = 2; // keeps worker 2 the capital producer in both profiles
    view
}

#[test]
fn planned_spec_stops_exactly_at_the_worker_ceiling() {
    let view = abundant_capital_world();
    assert!(R1faBot::planned_spec(&view, 1).is_some());
    assert_eq!(R1faBot::planned_spec(&view, 2).is_some(), WORKER_LIMIT > 2);
    assert!(R1faBot::planned_spec(&view, WORKER_LIMIT).is_none());
}

#[test]
fn first_hire_is_identical_under_either_ceiling() {
    let mut view = world();
    view.units = vec![view.units[1].clone()];
    view.inventories[0] = [10, 10, 10, 5, 10, 0];
    let commands = R1faBot::new().commands(&view);
    assert!(commands.iter().any(|c| c == "TRAIN 3 3 1 3"), "{commands:?}");
}

#[test]
fn abundant_stock_does_not_buy_a_third_worker_under_the_ceiling() {
    let view = abundant_capital_world();
    let mut bot = R1faBot::new();
    let commands = bot.commands(&view);
    if WORKER_LIMIT > 2 {
        assert!(commands.iter().any(|c| c == "TRAIN 2 3 1 2"), "{commands:?}");
    } else {
        assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
        // The released worker spends the turn on wood instead of banking a bill.
        assert!(commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
        assert_eq!(bot.goals.get(&2), Some(&R1faGoal { job: R1faJob::Chop, cell: (1, 1) }));
    }
}

#[test]
fn capital_only_harvest_is_released_for_wood_under_the_ceiling() {
    let view = deficient_capital_world();
    let mut bot = R1faBot::new();
    bot.goals.insert(2, R1faGoal { job: R1faJob::Harvest(PlantKind::Lemon), cell: (3, 1) });
    let commands = bot.commands(&view);
    assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
    if WORKER_LIMIT > 2 {
        assert_eq!(bot.goals.get(&2),
                   Some(&R1faGoal { job: R1faJob::Harvest(PlantKind::Lemon), cell: (3, 1) }));
        assert!(!commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
    } else {
        assert_eq!(bot.goals.get(&2), Some(&R1faGoal { job: R1faJob::Chop, cell: (1, 1) }));
        assert!(commands.iter().any(|c| c == "CHOP 2"), "{commands:?}");
    }
}

// One released chopper (carry 1, chop 2) between a payable banana under the bank and a
// far wild plum. Ordinary rates from (1, 1): banana 400000/4 = 100000, plum 400000/17 =
// 23529. The plum sits two cells from the enemy shack, so its premium is 360000/3 = 120000.
fn scarce_denial_world() -> GameState {
    let mut view = world();
    view.units = vec![view.units[1].clone()];
    view.units[0].stats.carry_capacity = 1;
    view.units[0].stats.chop_power = 2;
    view.inventories[0] = [15, 0, 20, 0, 2, 0]; // no banked banana: no renewal offer
    view.plants = vec![
        Plant { kind: PlantKind::Banana, cell: (1, 1), size: 4, health: 6, fruits: 0, cooldown: 0 },
        Plant { kind: PlantKind::Plum, cell: (6, 1), size: 4, health: 12, fruits: 0, cooldown: 0 },
    ];
    view
}

fn add_three_enemy_workers(view: &mut GameState) {
    for (index, cell) in [(7, 0), (7, 1), (7, 2)].into_iter().enumerate() {
        view.units.push(Unit {
            id: 10 + index as i32, player: 1, cell,
            stats: Stats { movement_speed: 1, carry_capacity: 2, harvest_power: 1, chop_power: 1 },
            carry: [0; 6],
        });
    }
}

#[test]
fn scarce_denial_changes_the_live_production_comparison() {
    let view = scarce_denial_world();
    let mut bot = R1faBot::new();
    bot.focus = Some(PlantKind::Plum);
    let goal = bot.production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    let cell = if RESOURCE_DENIAL { (6, 1) } else { (1, 1) };
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell }), "{goal:?}");
}

#[test]
fn a_kind_outside_the_latched_focus_earns_no_denial_premium() {
    let view = scarce_denial_world();
    let mut bot = R1faBot::new();
    bot.focus = Some(PlantKind::Lemon);
    let goal = bot.production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell: (1, 1) }), "{goal:?}");
}

#[test]
fn an_owned_scarce_source_earns_no_denial_premium() {
    let view = scarce_denial_world();
    let mut bot = R1faBot::new();
    bot.focus = Some(PlantKind::Plum);
    bot.planted.insert((6, 1));
    let goal = bot.production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell: (1, 1) }), "{goal:?}");
}

#[test]
fn a_third_enemy_worker_suppresses_the_premium_away_from_the_tree() {
    let mut view = scarce_denial_world();
    add_three_enemy_workers(&mut view);
    let mut bot = R1faBot::new();
    bot.focus = Some(PlantKind::Plum);
    let goal = bot.production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell: (1, 1) }), "{goal:?}");
}

#[test]
fn a_worker_already_on_the_scarce_tree_keeps_the_premium() {
    let mut view = scarce_denial_world();
    add_three_enemy_workers(&mut view);
    view.units[0].cell = (6, 1);
    let mut bot = R1faBot::new();
    bot.focus = Some(PlantKind::Plum);
    let goal = bot.production_goal(&view, &view.units[0], &[0; 6], &BTreeSet::new());
    // From the plum the ordinary rates are 33333 here against 44444 for the banana.
    let cell = if RESOURCE_DENIAL { (6, 1) } else { (1, 1) };
    assert_eq!(goal, Some(R1faGoal { job: R1faJob::Chop, cell }), "{goal:?}");
}

#[test]
fn two_workers_cannot_claim_the_same_scarce_tree() {
    let mut view = scarce_denial_world();
    let chopper = |id, cell| Unit {
        id, player: 0, cell,
        stats: Stats { movement_speed: 1, carry_capacity: 1, harvest_power: 1, chop_power: 2 },
        carry: [0; 6],
    };
    view.units = vec![chopper(0, (2, 0)), chopper(2, (2, 1))];
    let mut bot = R1faBot::new();
    let commands = bot.commands(&view);
    let first = bot.goals.get(&0).map(|goal| goal.cell);
    let second = bot.goals.get(&2).map(|goal| goal.cell);
    assert_ne!(first, second, "{commands:?}");
    // The reservation makes the earlier worker take the premium and the later one
    // fall back, which reverses the pair when denial is enabled.
    if RESOURCE_DENIAL {
        assert_eq!((first, second), (Some((6, 1)), Some((1, 1))), "{commands:?}");
    } else {
        assert_eq!((first, second), (Some((1, 1)), Some((6, 1))), "{commands:?}");
    }
}

#[test]
fn the_scarce_focus_is_latched_once_and_reset_for_a_new_game() {
    let mut view = scarce_denial_world();
    let mut bot = R1faBot::new();
    assert_eq!(bot.focus, None);
    bot.commands(&view);
    assert_eq!(bot.focus, Some(PlantKind::Plum));
    // A mid-game view cannot re-select: this one would have chosen the near lemons.
    view.turn = 200;
    view.plants = vec![
        Plant { kind: PlantKind::Lemon, cell: (1, 1), size: 4, health: 12, fruits: 0, cooldown: 0 },
        Plant { kind: PlantKind::Plum, cell: (6, 1), size: 4, health: 12, fruits: 0, cooldown: 0 },
        Plant { kind: PlantKind::Plum, cell: (6, 0), size: 4, health: 12, fruits: 0, cooldown: 0 },
    ];
    bot.commands(&view);
    assert_eq!(bot.focus, Some(PlantKind::Plum));
    // Turn 1 is a new game, so the same view now selects the lemons.
    view.turn = 1;
    bot.commands(&view);
    assert_eq!(bot.focus, Some(PlantKind::Lemon));
}

fn enemy_worker(id: i32, cell: Cell) -> Unit {
    Unit {
        id, player: 1, cell,
        stats: Stats { movement_speed: 1, carry_capacity: 2, harvest_power: 1, chop_power: 1 },
        carry: [0; 6],
    }
}

// One worker and a fully banked first hire: 10 plum, 10 lemon, 2 apple, 10 iron.
fn funded_first_hire_world() -> GameState {
    let mut view = world();
    view.units = vec![view.units[1].clone()];
    view.inventories[0] = [10, 10, 10, 5, 10, 0];
    view
}

#[test]
fn a_shack_occupant_with_a_legal_exit_trains_on_the_same_turn() {
    let mut view = funded_first_hire_world();
    view.units[0].cell = view.shacks[0];
    let commands = R1faBot::new().commands(&view);
    assert!(commands.iter().any(|c| c == "MOVE 2 0 0"), "{commands:?}");
    assert!(commands.iter().any(|c| c == "TRAIN 3 3 1 3"), "{commands:?}");
}

#[test]
fn a_shack_occupant_without_a_legal_exit_does_not_train() {
    let mut view = funded_first_hire_world();
    view.units[0].cell = view.shacks[0];
    view.plants.clear();
    // The single exit left in the graph is held by an opponent worker.
    view.walkable = BTreeSet::from([(1, 1)]);
    view.units.push(enemy_worker(10, (1, 1)));
    let commands = R1faBot::new().commands(&view);
    assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
}

#[test]
fn an_opponent_standing_on_our_shack_blocks_the_purchase() {
    let mut view = funded_first_hire_world();
    view.units.push(enemy_worker(10, view.shacks[0]));
    let commands = R1faBot::new().commands(&view);
    assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
}

// A one-column corridor with the shack between the worker and its cached tree. The
// shack cell is walkable here so that the single step toward the tree is expressible.
fn corridor_world() -> GameState {
    let rows = vec!["...".to_string(), "0.1".to_string(), "...".to_string()];
    let map = crate::candidate::game::protocol::parse_static_map(3, 3, &rows);
    GameState {
        width: 3, height: 3,
        walkable: BTreeSet::from([(0, 0), (0, 1), (0, 2)]),
        shacks: map.shacks,
        inventories: [[10, 10, 10, 5, 10, 0], [0; 6]],
        units: vec![Unit {
            id: 0, player: 0, cell: (0, 0),
            stats: Stats { movement_speed: 1, carry_capacity: 3, harvest_power: 1, chop_power: 3 },
            carry: [0; 6],
        }],
        plants: vec![Plant { kind: PlantKind::Banana, cell: (0, 2), size: 4,
                             health: 6, fruits: 0, cooldown: 0 }],
        scores: [0, 0], turn: 2, next_id: 1,
        iron: BTreeSet::new(), water: BTreeSet::new(),
    }
}

#[test]
fn a_step_onto_an_initially_empty_shack_withholds_the_purchase() {
    let view = corridor_world();
    assert!(R1faBot::planned_spec(&view, 1).is_some());
    let mut bot = R1faBot::new();
    bot.goals.insert(0, R1faGoal { job: R1faJob::Chop, cell: (0, 2) });
    let commands = bot.commands(&view);
    assert_eq!(commands, vec!["MOVE 0 0 1".to_string()], "{commands:?}");
}

#[test]
fn a_reserved_training_bill_is_not_withdrawn_as_a_seed() {
    let mut view = world();
    // Worker 0 wants the last billed plum from the bank; worker 2 vacates the shack.
    view.units[0].cell = (0, 0);
    view.units[1].cell = view.shacks[0];
    view.inventories[0] = [6, 20, 20, 5, 20, 0];
    let mut bot = R1faBot::new();
    bot.goals.insert(0, R1faGoal { job: R1faJob::Seed(PlantKind::Plum), cell: view.shacks[0] });
    let commands = bot.commands(&view);
    if WORKER_LIMIT > 2 {
        assert!(!commands.iter().any(|c| c.starts_with("PICK")), "{commands:?}");
        // The bill is exactly the banked plum, so the seed waits and the hire lands.
        assert!(commands.iter().any(|c| c == "MOVE 2 0 2"), "{commands:?}");
        assert!(commands.iter().any(|c| c == "TRAIN 2 3 1 2"), "{commands:?}");
    } else {
        assert!(!commands.iter().any(|c| c.starts_with("TRAIN")), "{commands:?}");
        // No hire is intended at the ceiling; unrelated renewable seed work is legal.
        assert!(commands.iter().any(|c| c == "PICK 0 BANANA"), "{commands:?}");
    }
}

#[test]
fn the_first_hire_bill_is_reserved_under_either_worker_ceiling() {
    let mut view = funded_first_hire_world();
    view.units[0].cell = (0, 0);
    view.inventories[0][PLUM] = 2; // exactly the first hire's movement-speed-1 bill
    let mut bot = R1faBot::new();
    bot.goals.insert(2, R1faGoal { job: R1faJob::Seed(PlantKind::Plum), cell: view.shacks[0] });
    let commands = bot.commands(&view);
    assert!(!commands.iter().any(|c| c.starts_with("PICK")), "{commands:?}");
    assert!(commands.iter().any(|c| c == "TRAIN 1 3 1 3"), "{commands:?}");
}

#[test]
fn uncertain_move_predictions_fail_closed() {
    let view = funded_first_hire_world();
    for invalid in ["MOVE 2", "MOVE x 0 0", "MOVE 999 0 0", "MOVE 2 8 2",
                    "MOVE 2 0 0 extra"] {
        assert!(!R1faBot::shack_clear_after_moves(&view, &[invalid.to_string()]), "{invalid}");
    }
    assert!(!R1faBot::shack_clear_after_moves(&view,
        &["MOVE 2 1 0".to_string(), "MOVE 2 1 2".to_string()]));
    let mut view = view;
    view.units.push(enemy_worker(10, (2, 1)));
    assert!(!R1faBot::shack_clear_after_moves(&view, &["MOVE 10 2 0".to_string()]));
}

#[test]
fn endpoint_collision_cannot_certify_shack_egress() {
    let mut view = world();
    view.units[0].cell = view.shacks[0];
    view.units[1].cell = (0, 0);
    assert!(!R1faBot::shack_clear_after_moves(&view, &["MOVE 0 0 0".to_string()]));
    assert!(R1faBot::shack_clear_after_moves(&view,
        &["MOVE 0 0 0".to_string(), "MOVE 2 1 0".to_string()]));
}

#[test]
fn training_egress_has_priority_over_other_movement() {
    let mut view = world();
    view.units[0].cell = view.shacks[0];
    view.units[1].cell = (1, 0);
    let mut commands = vec!["MOVE 0 0 0".to_string(), "MOVE 2 0 0".to_string()];
    MoisanBot::resolve_move_conflicts_with_egress(
        &view, &mut commands, &BTreeSet::from([0, 2]), &BTreeSet::new(), Some(0));
    assert_eq!(commands[0], "MOVE 0 0 0");
    assert_ne!(commands[1], "MOVE 2 0 0");
    assert!(R1faBot::shack_clear_after_moves(&view, &commands));
}
