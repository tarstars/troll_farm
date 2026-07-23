//! D36 resident-anchored constrained repeated joint-option upper bound.

use super::*;

const R_MAX_NONCONTROL_EPOCHS: usize = 4;
const R_LAST_EPOCH_TURN: i32 = 220;
const R_OPPONENT_EXCESS_CEILING: i32 = 65;

#[derive(Clone)]
struct RLive {
    game: GameState,
    resident: SecureOrchardBot,
    opponent_history: Vec<GameState>,
    stall_counter: i32,
    owners: BTreeMap<Cell, PlantOwner>,
    attribution_failures: usize,
    max_own_workers: usize,
    terminal: bool,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct RFinish {
    outcome: Outcome,
    attribution_failures: usize,
    history_mismatch: usize,
    cell_mismatch: usize,
    max_own_workers: usize,
    terminal_hash: u64,
}

struct RCapture {
    live: Option<RLive>,
    prefix_attribution_failures: usize,
    start_history_mismatch: usize,
    start_cell_mismatch: usize,
    resident: RFinish,
    independent_resident_match: bool,
}

struct RExecution {
    live: RLive,
    statuses: String,
    overridden_actions: usize,
    invalid_direct_commands: usize,
    end_turn: i32,
    terminal: bool,
}

struct RSimulation {
    finish: RFinish,
    statuses: String,
    overridden_actions: usize,
    invalid_direct_commands: usize,
    bundle_end_turn: i32,
    execution_terminal: bool,
}

struct ROption {
    epoch: usize,
    epoch_turn: i32,
    option: usize,
    plan: Option<CPlan>,
    simulation: RSimulation,
    feasible: bool,
    selected: bool,
    unconstrained_selected: bool,
    executed_end_turn: i32,
    execution_statuses: String,
    execution_overridden_actions: usize,
    execution_invalid_direct_commands: usize,
    execution_terminal: bool,
    execution_prefix_match: bool,
    selected_rollout_replay_match: bool,
    root_plan_count: usize,
    generic_plan_count: usize,
    competitive_plan_count: usize,
    owner_counts: [usize; 4],
    attribution_cell_mismatch: usize,
    history_mismatch: usize,
}

struct RManifest {
    task: Task,
    eligible: bool,
    start_turn: i32,
    prefix_attribution_failures: usize,
    start_history_mismatch: usize,
    start_cell_mismatch: usize,
    independent_resident_match: bool,
    resident: RFinish,
}

struct RTaskResult {
    task: Task,
    options: Vec<ROption>,
    manifest: RManifest,
    one_shot: Option<RFinish>,
    one_shot_catalog: String,
    one_shot_key: String,
    unconstrained: Option<RFinish>,
    unconstrained_catalog: String,
    unconstrained_key: String,
    repeated: Option<RFinish>,
    selected_noncontrol_epochs: usize,
    selected_competitive_epochs: usize,
    stop_reason: String,
    infeasible_selection_failures: usize,
    replay_mismatches: usize,
    strict_advance_failures: usize,
    execution_prefix_mismatches: usize,
}

fn r_history_mismatch(live: &RLive) -> usize {
    live.opponent_history
        .len()
        .abs_diff((live.game.turn - 1).max(0) as usize)
}

fn r_cell_mismatch(game: &GameState, owners: &BTreeMap<Cell, PlantOwner>) -> usize {
    let live_cells: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    let owner_cells: BTreeSet<_> = owners.keys().copied().collect();
    live_cells.symmetric_difference(&owner_cells).count()
}

fn r_finish_snapshot(live: &RLive, task: Task) -> RFinish {
    RFinish {
        outcome: Outcome::from_game(&live.game, task.seat),
        attribution_failures: live.attribution_failures,
        history_mismatch: r_history_mismatch(live),
        cell_mismatch: r_cell_mismatch(&live.game, &live.owners),
        max_own_workers: live.max_own_workers,
        terminal_hash: d_terminal_hash(&live.game, &live.owners),
    }
}

fn r_warmed_opponent(history: &[GameState], index: usize, player: usize) -> Opponent {
    let mut policy = opponent(index);
    for historical in history {
        let _ = policy.commands(historical, 1 - player);
    }
    policy
}

fn r_capture_start(task: Task) -> RCapture {
    let mut game = generate_official(task.seed);
    let mut resident = SecureOrchardBot::new();
    let mut rival = opponent(task.opponent_index);
    let mut stall_counter = 0;
    let mut opponent_history = Vec::new();
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), PlantOwner::Natural))
        .collect();
    let mut attribution_failures = 0;
    let mut max_own_workers = worker_count(&game, task.seat);
    let mut live = None;
    let mut prefix_attribution_failures = 0;
    let mut start_history_mismatch = 0;
    let mut start_cell_mismatch = 0;

    while game.turn <= TOTAL_TURNS {
        let resident_before = resident.clone();
        let ours = resident.commands(&yamo_view(&game, task.seat));
        if live.is_none() && game.turn >= 50 && worker_count(&game, task.seat) == 2 {
            prefix_attribution_failures = attribution_failures;
            let snapshot = RLive {
                game: game.clone(),
                resident: resident_before,
                opponent_history: opponent_history.clone(),
                stall_counter,
                owners: owners.clone(),
                attribution_failures,
                max_own_workers,
                terminal: false,
            };
            start_history_mismatch = r_history_mismatch(&snapshot);
            start_cell_mismatch = r_cell_mismatch(&snapshot.game, &snapshot.owners);
            live = Some(snapshot);
        }
        let theirs = rival.commands(&game, 1 - task.seat);
        opponent_history.push(game.clone());
        attribution_failures +=
            apply_with_provenance(&mut game, task.seat, &ours, &theirs, &mut owners);
        max_own_workers = max_own_workers.max(worker_count(&game, task.seat));
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    let terminal_live = RLive {
        game,
        resident,
        opponent_history,
        stall_counter,
        owners,
        attribution_failures,
        max_own_workers,
        terminal: true,
    };
    let resident_finish = r_finish_snapshot(&terminal_live, task);
    RCapture {
        live,
        prefix_attribution_failures,
        start_history_mismatch,
        start_cell_mismatch,
        resident: resident_finish,
        independent_resident_match: resident_finish.outcome == resident_reference(task),
    }
}

fn r_execute_bundle(mut live: RLive, task: Task, plan: &JointPlan) -> RExecution {
    assert!(!live.terminal, "cannot execute D36 bundle after terminal");
    let mut rival = r_warmed_opponent(&live.opponent_history, task.opponent_index, task.seat);
    let mut active = BTreeMap::new();
    let mut status = BTreeMap::new();
    for spec in &plan.jobs {
        if spec.kind == JobKind::Keep {
            status.insert(spec.unit_id, "keep");
        } else {
            active.insert(spec.unit_id, ActiveJob::new(spec.clone(), &live.game));
            status.insert(spec.unit_id, "active");
        }
    }
    assert!(!active.is_empty(), "D36 never executes all-KEEP control");
    let mut overridden_actions = 0;
    let mut invalid_direct_commands = 0;
    loop {
        if live.game.turn > TOTAL_TURNS {
            live.terminal = true;
            break;
        }
        let resident_before = live.resident.clone();
        let mut ours = live.resident.commands(&yamo_view(&live.game, task.seat));
        let ids: Vec<_> = active.keys().copied().collect();
        for id in ids {
            let result = active
                .get_mut(&id)
                .expect("D36 active job")
                .command(&live.game, task.seat);
            match result {
                JobCommand::Command(command) => {
                    if !direct_command_is_valid(&live.game, task.seat, &command) {
                        invalid_direct_commands += 1;
                        active.remove(&id);
                        status.insert(id, "direct_command_invalid");
                        continue;
                    }
                    overridden_actions += usize::from(replace_unit_action(
                        &live.game, task.seat, &mut ours, id, command,
                    ));
                }
                JobCommand::Complete => {
                    active.remove(&id);
                    status.insert(id, "completed");
                }
                JobCommand::Invalid(reason) => {
                    active.remove(&id);
                    status.insert(id, reason);
                }
            }
        }
        if active.is_empty() {
            live.resident = resident_before;
            break;
        }
        let theirs = rival.commands(&live.game, 1 - task.seat);
        live.opponent_history.push(live.game.clone());
        live.attribution_failures +=
            apply_with_provenance(&mut live.game, task.seat, &ours, &theirs, &mut live.owners);
        live.max_own_workers = live
            .max_own_workers
            .max(worker_count(&live.game, task.seat));
        if has_stalled(&live.game, &mut live.stall_counter) {
            live.terminal = true;
            break;
        }
    }
    if live.game.turn > TOTAL_TURNS {
        live.terminal = true;
    }
    let statuses = status
        .iter()
        .map(|(id, value)| format!("{id}:{value}"))
        .collect::<Vec<_>>()
        .join(",");
    RExecution {
        end_turn: live.game.turn,
        terminal: live.terminal,
        live,
        statuses,
        overridden_actions,
        invalid_direct_commands,
    }
}

fn r_finish(mut live: RLive, task: Task) -> RFinish {
    if !live.terminal {
        let mut rival = r_warmed_opponent(&live.opponent_history, task.opponent_index, task.seat);
        while live.game.turn <= TOTAL_TURNS {
            let ours = live.resident.commands(&yamo_view(&live.game, task.seat));
            let theirs = rival.commands(&live.game, 1 - task.seat);
            live.opponent_history.push(live.game.clone());
            live.attribution_failures +=
                apply_with_provenance(&mut live.game, task.seat, &ours, &theirs, &mut live.owners);
            live.max_own_workers = live
                .max_own_workers
                .max(worker_count(&live.game, task.seat));
            if has_stalled(&live.game, &mut live.stall_counter) {
                live.terminal = true;
                break;
            }
        }
        if live.game.turn > TOTAL_TURNS {
            live.terminal = true;
        }
    }
    r_finish_snapshot(&live, task)
}

fn r_simulate(live: &RLive, task: Task, plan: Option<&JointPlan>) -> RSimulation {
    let Some(plan) = plan else {
        return RSimulation {
            finish: r_finish(live.clone(), task),
            statuses: String::new(),
            overridden_actions: 0,
            invalid_direct_commands: 0,
            bundle_end_turn: live.game.turn,
            execution_terminal: live.terminal,
        };
    };
    let execution = r_execute_bundle(live.clone(), task, plan);
    let bundle_end_turn = execution.end_turn;
    let execution_terminal = execution.terminal;
    let statuses = execution.statuses;
    let overridden_actions = execution.overridden_actions;
    let invalid_direct_commands = execution.invalid_direct_commands;
    RSimulation {
        finish: r_finish(execution.live, task),
        statuses,
        overridden_actions,
        invalid_direct_commands,
        bundle_end_turn,
        execution_terminal,
    }
}

fn r_rollouts(
    live: &RLive,
    task: Task,
    epoch: usize,
    resident_opponent_score: i32,
) -> Vec<ROption> {
    let plans = cplans(&live.game, task.seat, &live.owners);
    let generic_plan_count = plans
        .iter()
        .filter(|plan| plan.catalog == Catalog::Generic)
        .count();
    let competitive_plan_count = plans.len() - generic_plan_count;
    let owner_counts = plant_owner_counts(&live.owners);
    let attribution_cell_mismatch = r_cell_mismatch(&live.game, &live.owners);
    let history_mismatch = r_history_mismatch(live);
    let mut rows = Vec::with_capacity(plans.len() + 1);
    for option in 0..=plans.len() {
        let plan = option.checked_sub(1).map(|index| plans[index].clone());
        let simulation = r_simulate(live, task, plan.as_ref().map(|value| &value.plan));
        let feasible = simulation.finish.outcome.opponent_score
            <= resident_opponent_score + R_OPPONENT_EXCESS_CEILING;
        rows.push(ROption {
            epoch,
            epoch_turn: live.game.turn,
            option,
            plan,
            simulation,
            feasible,
            selected: false,
            unconstrained_selected: false,
            executed_end_turn: -1,
            execution_statuses: String::new(),
            execution_overridden_actions: 0,
            execution_invalid_direct_commands: 0,
            execution_terminal: false,
            execution_prefix_match: false,
            selected_rollout_replay_match: false,
            root_plan_count: plans.len(),
            generic_plan_count,
            competitive_plan_count,
            owner_counts,
            attribution_cell_mismatch,
            history_mismatch,
        });
    }
    rows
}

fn r_key(row: &ROption) -> &str {
    row.plan
        .as_ref()
        .map_or("control", |plan| plan.plan.key.as_str())
}

fn r_constrained_order(row: &ROption) -> (usize, i32, i32, usize, usize, &str) {
    (
        usize::from(!row.feasible),
        -row.simulation.finish.outcome.own_score,
        row.simulation.finish.outcome.opponent_score,
        usize::from(row.option != 0),
        row.simulation.overridden_actions,
        r_key(row),
    )
}

fn r_selected_index(rows: &[ROption]) -> usize {
    (0..rows.len())
        .min_by(|left, right| {
            r_constrained_order(&rows[*left]).cmp(&r_constrained_order(&rows[*right]))
        })
        .expect("D36 epoch has control")
}

fn r_unconstrained_order(row: &ROption) -> (i32, usize, usize, &str) {
    (
        -row.simulation.finish.outcome.margin(),
        usize::from(row.option != 0),
        row.simulation.overridden_actions,
        r_key(row),
    )
}

fn r_unconstrained_index(rows: &[ROption]) -> usize {
    (0..rows.len())
        .min_by(|left, right| {
            r_unconstrained_order(&rows[*left]).cmp(&r_unconstrained_order(&rows[*right]))
        })
        .expect("D36 epoch has control")
}

fn r_identity(row: &ROption) -> (String, String) {
    row.plan.as_ref().map_or_else(
        || ("control".to_string(), "control".to_string()),
        |plan| (plan.catalog.label().to_string(), plan.plan.key.clone()),
    )
}

fn r_play_task(task: Task) -> RTaskResult {
    let capture = r_capture_start(task);
    let start_turn = capture.live.as_ref().map_or(-1, |live| live.game.turn);
    let manifest = RManifest {
        task,
        eligible: capture.live.is_some(),
        start_turn,
        prefix_attribution_failures: capture.prefix_attribution_failures,
        start_history_mismatch: capture.start_history_mismatch,
        start_cell_mismatch: capture.start_cell_mismatch,
        independent_resident_match: capture.independent_resident_match,
        resident: capture.resident,
    };
    let Some(mut live) = capture.live else {
        return RTaskResult {
            task,
            options: Vec::new(),
            manifest,
            one_shot: None,
            one_shot_catalog: "none".to_string(),
            one_shot_key: "none".to_string(),
            unconstrained: None,
            unconstrained_catalog: "none".to_string(),
            unconstrained_key: "none".to_string(),
            repeated: None,
            selected_noncontrol_epochs: 0,
            selected_competitive_epochs: 0,
            stop_reason: "ineligible".to_string(),
            infeasible_selection_failures: 0,
            replay_mismatches: 0,
            strict_advance_failures: 0,
            execution_prefix_mismatches: 0,
        };
    };

    let resident_opponent_score = manifest.resident.outcome.opponent_score;
    let mut options = Vec::new();
    let mut epoch = 0usize;
    let mut one_shot = None;
    let mut one_shot_catalog = String::new();
    let mut one_shot_key = String::new();
    let mut unconstrained = None;
    let mut unconstrained_catalog = String::new();
    let mut unconstrained_key = String::new();
    let mut selected_noncontrol_epochs = 0usize;
    let mut selected_competitive_epochs = 0usize;
    let mut infeasible_selection_failures = 0usize;
    let mut replay_mismatches = 0usize;
    let mut strict_advance_failures = 0usize;
    let mut execution_prefix_mismatches = 0usize;
    let stop_reason;

    let repeated = loop {
        if live.terminal {
            stop_reason = "terminal".to_string();
            break r_finish(live, task);
        }
        if selected_noncontrol_epochs >= R_MAX_NONCONTROL_EPOCHS {
            stop_reason = "epoch_cap".to_string();
            break r_finish(live, task);
        }
        if live.game.turn > R_LAST_EPOCH_TURN {
            stop_reason = "turn_cutoff".to_string();
            break r_finish(live, task);
        }

        let mut epoch_rows = r_rollouts(&live, task, epoch, resident_opponent_score);
        let selected_index = r_selected_index(&epoch_rows);
        epoch_rows[selected_index].selected = true;
        infeasible_selection_failures += usize::from(!epoch_rows[selected_index].feasible);
        if epoch == 0 {
            let unconstrained_index = r_unconstrained_index(&epoch_rows);
            epoch_rows[unconstrained_index].unconstrained_selected = true;
            unconstrained = Some(epoch_rows[unconstrained_index].simulation.finish);
            (unconstrained_catalog, unconstrained_key) =
                r_identity(&epoch_rows[unconstrained_index]);
            one_shot = Some(epoch_rows[selected_index].simulation.finish);
            (one_shot_catalog, one_shot_key) = r_identity(&epoch_rows[selected_index]);
        }

        let selected_finish = epoch_rows[selected_index].simulation.finish;
        let Some(selected_plan) = epoch_rows[selected_index].plan.clone() else {
            let finish = r_finish(live.clone(), task);
            let replay_match = finish == selected_finish;
            replay_mismatches += usize::from(!replay_match);
            let selected = &mut epoch_rows[selected_index];
            selected.executed_end_turn = selected.epoch_turn;
            selected.execution_statuses = selected.simulation.statuses.clone();
            selected.execution_overridden_actions = selected.simulation.overridden_actions;
            selected.execution_invalid_direct_commands =
                selected.simulation.invalid_direct_commands;
            selected.execution_terminal = live.terminal;
            selected.execution_prefix_match =
                selected.simulation.bundle_end_turn == selected.epoch_turn;
            selected.selected_rollout_replay_match = replay_match;
            execution_prefix_mismatches += usize::from(!selected.execution_prefix_match);
            options.extend(epoch_rows);
            stop_reason = "control".to_string();
            break finish;
        };

        let epoch_turn = epoch_rows[selected_index].epoch_turn;
        let rollout_statuses = epoch_rows[selected_index].simulation.statuses.clone();
        let rollout_overrides = epoch_rows[selected_index].simulation.overridden_actions;
        let rollout_invalid = epoch_rows[selected_index]
            .simulation
            .invalid_direct_commands;
        let rollout_bundle_end = epoch_rows[selected_index].simulation.bundle_end_turn;
        let rollout_terminal = epoch_rows[selected_index].simulation.execution_terminal;
        let execution = r_execute_bundle(live, task, &selected_plan.plan);
        let prefix_match = execution.end_turn == rollout_bundle_end
            && execution.statuses == rollout_statuses
            && execution.overridden_actions == rollout_overrides
            && execution.invalid_direct_commands == rollout_invalid
            && execution.terminal == rollout_terminal;
        execution_prefix_mismatches += usize::from(!prefix_match);
        strict_advance_failures +=
            usize::from(execution.end_turn <= epoch_turn && !execution.terminal);
        let replay = r_finish(execution.live.clone(), task);
        let replay_match = replay == selected_finish;
        replay_mismatches += usize::from(!replay_match);
        {
            let selected = &mut epoch_rows[selected_index];
            selected.executed_end_turn = execution.end_turn;
            selected.execution_statuses = execution.statuses.clone();
            selected.execution_overridden_actions = execution.overridden_actions;
            selected.execution_invalid_direct_commands = execution.invalid_direct_commands;
            selected.execution_terminal = execution.terminal;
            selected.execution_prefix_match = prefix_match;
            selected.selected_rollout_replay_match = replay_match;
        }
        selected_noncontrol_epochs += 1;
        selected_competitive_epochs += usize::from(selected_plan.catalog == Catalog::Competitive);
        live = execution.live;
        options.extend(epoch_rows);
        epoch += 1;
    };

    RTaskResult {
        task,
        options,
        manifest,
        one_shot,
        one_shot_catalog,
        one_shot_key,
        unconstrained,
        unconstrained_catalog,
        unconstrained_key,
        repeated: Some(repeated),
        selected_noncontrol_epochs,
        selected_competitive_epochs,
        stop_reason,
        infeasible_selection_failures,
        replay_mismatches,
        strict_advance_failures,
        execution_prefix_mismatches,
    }
}

fn r_plan_fields(
    row: &ROption,
) -> (
    String,
    String,
    String,
    String,
    i32,
    i32,
    i32,
    usize,
    usize,
    usize,
) {
    row.plan.as_ref().map_or(
        (
            "control".to_string(),
            "control".to_string(),
            "control".to_string(),
            "none+none".to_string(),
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        |plan| {
            (
                plan.catalog.label().to_string(),
                plan.plan.key.clone(),
                plan.plan
                    .jobs
                    .iter()
                    .map(|job| job.kind.label())
                    .collect::<Vec<_>>()
                    .join("+"),
                plan.owner_tuple(),
                plan.plan.predicted_eta,
                plan.plan.predicted_reward,
                plan.plan.rate_score,
                plan.competitive_targets(),
                plan.opponent_targets(),
                plan.ambiguous_targets(),
            )
        },
    )
}

fn write_rmanifest(results: &[RTaskResult], output: &str) {
    let path = format!("{output}.scenarios.tsv");
    let mut writer = BufWriter::new(File::create(&path).expect("create D36 manifest"));
    writeln!(writer, "seed\tseat\topponent\teligible\tstart_turn\tprefix_attribution_failures\tstart_history_mismatch\tstart_cell_mismatch\tindependent_resident_match\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn\tresident_attribution_failures\tresident_history_mismatch\tresident_cell_mismatch\tresident_max_own_workers\tresident_terminal_hash").expect("write D36 manifest header");
    for result in results {
        let entry = &result.manifest;
        let finish = entry.resident;
        let outcome = finish.outcome;
        let fields = vec![
            entry.task.seed.to_string(),
            entry.task.seat.to_string(),
            OPPONENTS[entry.task.opponent_index].to_string(),
            usize::from(entry.eligible).to_string(),
            entry.start_turn.to_string(),
            entry.prefix_attribution_failures.to_string(),
            entry.start_history_mismatch.to_string(),
            entry.start_cell_mismatch.to_string(),
            usize::from(entry.independent_resident_match).to_string(),
            outcome.own_score.to_string(),
            outcome.opponent_score.to_string(),
            outcome.margin().to_string(),
            outcome.own_wood.to_string(),
            outcome.opponent_wood.to_string(),
            outcome.own_workers.to_string(),
            outcome.opponent_workers.to_string(),
            outcome.terminal_turn.to_string(),
            finish.attribution_failures.to_string(),
            finish.history_mismatch.to_string(),
            finish.cell_mismatch.to_string(),
            finish.max_own_workers.to_string(),
            finish.terminal_hash.to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D36 manifest row");
    }
    writer.flush().expect("flush D36 manifest");
}

fn write_rrows(results: &[RTaskResult], output: &str) {
    let mut writer = BufWriter::new(File::create(output).expect("create D36 output"));
    writeln!(writer, "seed\tseat\topponent\tepoch\tepoch_turn\toption\tfeasible\tselected\tunconstrained_selected\tcatalog\tplan_key\trole_tuple\ttarget_owners\tpredicted_eta\tpredicted_reward\trate_score\tcompetitive_target_count\topponent_target_count\tambiguous_target_count\trollout_statuses\trollout_overridden_actions\trollout_invalid_direct_commands\trollout_bundle_end_turn\trollout_execution_terminal\trollout_own_score\trollout_opponent_score\trollout_margin\trollout_own_wood\trollout_opponent_wood\trollout_own_workers\trollout_opponent_workers\trollout_terminal_turn\trollout_attribution_failures\trollout_history_mismatch\trollout_cell_mismatch\trollout_max_own_workers\trollout_terminal_hash\troot_plan_count\tgeneric_plan_count\tcompetitive_plan_count\troot_natural_plants\troot_own_plants\troot_opponent_plants\troot_ambiguous_plants\tattribution_cell_mismatch\thistory_mismatch\texecuted_end_turn\texecution_statuses\texecution_overridden_actions\texecution_invalid_direct_commands\texecution_terminal\texecution_prefix_match\tselected_rollout_replay_match\tone_shot_catalog\tone_shot_key\tone_shot_own_score\tone_shot_opponent_score\tone_shot_margin\tone_shot_own_wood\tone_shot_opponent_wood\tone_shot_own_workers\tone_shot_opponent_workers\tone_shot_terminal_turn\tone_shot_terminal_hash\tunconstrained_catalog\tunconstrained_key\tunconstrained_own_score\tunconstrained_opponent_score\tunconstrained_margin\tunconstrained_own_wood\tunconstrained_opponent_wood\tunconstrained_own_workers\tunconstrained_opponent_workers\tunconstrained_terminal_turn\tunconstrained_terminal_hash\tselected_noncontrol_epochs\tselected_competitive_epochs\tstop_reason\tinfeasible_selection_failures\treplay_mismatches\tstrict_advance_failures\texecution_prefix_mismatches\trepeated_own_score\trepeated_opponent_score\trepeated_margin\trepeated_own_wood\trepeated_opponent_wood\trepeated_own_workers\trepeated_opponent_workers\trepeated_terminal_turn\trepeated_attribution_failures\trepeated_history_mismatch\trepeated_cell_mismatch\trepeated_max_own_workers\trepeated_terminal_hash\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn\tresident_terminal_hash\trepeated_margin_delta_resident\trepeated_own_score_delta_resident\trepeated_opponent_score_delta_resident\tone_shot_margin_delta_resident\tone_shot_own_score_delta_resident\tone_shot_opponent_score_delta_resident\trepeated_margin_delta_one_shot\trepeated_own_score_delta_one_shot\trepeated_opponent_score_delta_one_shot\tunconstrained_margin_delta_resident\tunconstrained_own_score_delta_resident\tunconstrained_opponent_score_delta_resident\trepeated_opponent_excess\tone_shot_opponent_excess\tunconstrained_opponent_excess\topponent_excess_ceiling").expect("write D36 header");
    for result in results {
        if result.options.is_empty() {
            continue;
        }
        let one_shot = result.one_shot.expect("eligible D36 one-shot");
        let unconstrained = result.unconstrained.expect("eligible D36 unconstrained");
        let repeated = result.repeated.expect("eligible D36 repeated");
        let resident = result.manifest.resident;
        for row in &result.options {
            let (catalog, key, roles, owners, eta, reward, rate, competitive, opponent, ambiguous) =
                r_plan_fields(row);
            let rollout = row.simulation.finish;
            let rollout_outcome = rollout.outcome;
            let one = one_shot.outcome;
            let unc = unconstrained.outcome;
            let final_outcome = repeated.outcome;
            let baseline = resident.outcome;
            let fields = vec![
                result.task.seed.to_string(),
                result.task.seat.to_string(),
                OPPONENTS[result.task.opponent_index].to_string(),
                row.epoch.to_string(),
                row.epoch_turn.to_string(),
                row.option.to_string(),
                usize::from(row.feasible).to_string(),
                usize::from(row.selected).to_string(),
                usize::from(row.unconstrained_selected).to_string(),
                catalog,
                key,
                roles,
                owners,
                eta.to_string(),
                reward.to_string(),
                rate.to_string(),
                competitive.to_string(),
                opponent.to_string(),
                ambiguous.to_string(),
                row.simulation.statuses.clone(),
                row.simulation.overridden_actions.to_string(),
                row.simulation.invalid_direct_commands.to_string(),
                row.simulation.bundle_end_turn.to_string(),
                usize::from(row.simulation.execution_terminal).to_string(),
                rollout_outcome.own_score.to_string(),
                rollout_outcome.opponent_score.to_string(),
                rollout_outcome.margin().to_string(),
                rollout_outcome.own_wood.to_string(),
                rollout_outcome.opponent_wood.to_string(),
                rollout_outcome.own_workers.to_string(),
                rollout_outcome.opponent_workers.to_string(),
                rollout_outcome.terminal_turn.to_string(),
                rollout.attribution_failures.to_string(),
                rollout.history_mismatch.to_string(),
                rollout.cell_mismatch.to_string(),
                rollout.max_own_workers.to_string(),
                rollout.terminal_hash.to_string(),
                row.root_plan_count.to_string(),
                row.generic_plan_count.to_string(),
                row.competitive_plan_count.to_string(),
                row.owner_counts[0].to_string(),
                row.owner_counts[1].to_string(),
                row.owner_counts[2].to_string(),
                row.owner_counts[3].to_string(),
                row.attribution_cell_mismatch.to_string(),
                row.history_mismatch.to_string(),
                row.executed_end_turn.to_string(),
                row.execution_statuses.clone(),
                row.execution_overridden_actions.to_string(),
                row.execution_invalid_direct_commands.to_string(),
                usize::from(row.execution_terminal).to_string(),
                usize::from(row.execution_prefix_match).to_string(),
                usize::from(row.selected_rollout_replay_match).to_string(),
                result.one_shot_catalog.clone(),
                result.one_shot_key.clone(),
                one.own_score.to_string(),
                one.opponent_score.to_string(),
                one.margin().to_string(),
                one.own_wood.to_string(),
                one.opponent_wood.to_string(),
                one.own_workers.to_string(),
                one.opponent_workers.to_string(),
                one.terminal_turn.to_string(),
                one_shot.terminal_hash.to_string(),
                result.unconstrained_catalog.clone(),
                result.unconstrained_key.clone(),
                unc.own_score.to_string(),
                unc.opponent_score.to_string(),
                unc.margin().to_string(),
                unc.own_wood.to_string(),
                unc.opponent_wood.to_string(),
                unc.own_workers.to_string(),
                unc.opponent_workers.to_string(),
                unc.terminal_turn.to_string(),
                unconstrained.terminal_hash.to_string(),
                result.selected_noncontrol_epochs.to_string(),
                result.selected_competitive_epochs.to_string(),
                result.stop_reason.clone(),
                result.infeasible_selection_failures.to_string(),
                result.replay_mismatches.to_string(),
                result.strict_advance_failures.to_string(),
                result.execution_prefix_mismatches.to_string(),
                final_outcome.own_score.to_string(),
                final_outcome.opponent_score.to_string(),
                final_outcome.margin().to_string(),
                final_outcome.own_wood.to_string(),
                final_outcome.opponent_wood.to_string(),
                final_outcome.own_workers.to_string(),
                final_outcome.opponent_workers.to_string(),
                final_outcome.terminal_turn.to_string(),
                repeated.attribution_failures.to_string(),
                repeated.history_mismatch.to_string(),
                repeated.cell_mismatch.to_string(),
                repeated.max_own_workers.to_string(),
                repeated.terminal_hash.to_string(),
                baseline.own_score.to_string(),
                baseline.opponent_score.to_string(),
                baseline.margin().to_string(),
                baseline.own_wood.to_string(),
                baseline.opponent_wood.to_string(),
                baseline.own_workers.to_string(),
                baseline.opponent_workers.to_string(),
                baseline.terminal_turn.to_string(),
                resident.terminal_hash.to_string(),
                (final_outcome.margin() - baseline.margin()).to_string(),
                (final_outcome.own_score - baseline.own_score).to_string(),
                (final_outcome.opponent_score - baseline.opponent_score).to_string(),
                (one.margin() - baseline.margin()).to_string(),
                (one.own_score - baseline.own_score).to_string(),
                (one.opponent_score - baseline.opponent_score).to_string(),
                (final_outcome.margin() - one.margin()).to_string(),
                (final_outcome.own_score - one.own_score).to_string(),
                (final_outcome.opponent_score - one.opponent_score).to_string(),
                (unc.margin() - baseline.margin()).to_string(),
                (unc.own_score - baseline.own_score).to_string(),
                (unc.opponent_score - baseline.opponent_score).to_string(),
                (final_outcome.opponent_score - baseline.opponent_score).to_string(),
                (one.opponent_score - baseline.opponent_score).to_string(),
                (unc.opponent_score - baseline.opponent_score).to_string(),
                R_OPPONENT_EXCESS_CEILING.to_string(),
            ];
            writeln!(writer, "{}", fields.join("\t")).expect("write D36 row");
        }
    }
    writer.flush().expect("flush D36 output");
}

pub(crate) fn d36_main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args.get(1).map_or(9_500_000, |value| {
        value.parse::<i64>().expect("signed seed start")
    });
    let seed_count = args
        .get(2)
        .map_or(1, |value| value.parse::<usize>().expect("seed count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d36-resident-constrained-joint-oracle.tsv".to_string());
    let threads = args
        .get(4)
        .map_or(24, |value| value.parse::<usize>().expect("thread count"))
        .clamp(1, 64);
    assert!(seed_count > 0);

    let tasks: Vec<_> = (0..seed_count)
        .flat_map(|offset| {
            (0..2).flat_map(move |seat| {
                (0..OPPONENTS.len()).map(move |opponent_index| Task {
                    seed: seed_start + offset as i64,
                    seat,
                    opponent_index,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads)
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            thread::spawn(move || {
                let mut results = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    results.push(r_play_task(tasks[index]));
                }
                results
            })
        })
        .collect();
    let mut results: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D36 worker thread"))
        .collect();
    results.sort_by_key(|result| {
        (
            result.task.seed,
            result.task.seat,
            result.task.opponent_index,
        )
    });
    let row_count: usize = results.iter().map(|result| result.options.len()).sum();
    write_rrows(&results, &output);
    write_rmanifest(&results, &output);
    eprintln!(
        "saved {row_count} rows and {} scenario records from {} tasks in {:.3}s to {output}",
        results.len(),
        tasks.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn task() -> Task {
        Task {
            seed: 9_500_000,
            seat: 0,
            opponent_index: 2,
        }
    }

    #[test]
    fn resident_capture_control_is_exact_and_clonable() {
        let task = task();
        let capture = r_capture_start(task);
        assert!(capture.independent_resident_match);
        assert_eq!(capture.prefix_attribution_failures, 0);
        assert_eq!(capture.start_history_mismatch, 0);
        assert_eq!(capture.start_cell_mismatch, 0);
        assert_eq!(capture.resident.attribution_failures, 0);
        assert_eq!(capture.resident.history_mismatch, 0);
        assert_eq!(capture.resident.cell_mismatch, 0);
        let live = capture.live.expect("eligible D36 test task");
        assert_eq!(r_finish(live, task), capture.resident);
    }

    #[test]
    fn constrained_order_rejects_infeasible_own_score_and_prefers_control_tie() {
        let task = task();
        let live = r_capture_start(task).live.expect("eligible D36 test task");
        let mut rows = r_rollouts(&live, task, 0, i32::MAX / 4);
        rows.truncate(2);
        assert_eq!(rows.len(), 2);
        rows[0].feasible = true;
        rows[1].feasible = false;
        rows[1].simulation.finish.outcome.own_score =
            rows[0].simulation.finish.outcome.own_score + 1_000;
        assert_eq!(r_selected_index(&rows), 0);
        rows[1].feasible = true;
        assert_eq!(r_selected_index(&rows), 1);
        rows[1].simulation.finish.outcome = rows[0].simulation.finish.outcome;
        rows[1].simulation.overridden_actions = 0;
        assert_eq!(r_selected_index(&rows), 0);
    }

    #[test]
    fn resident_bundle_returns_at_exact_recorded_boundary() {
        let task = task();
        let capture = r_capture_start(task);
        let live = capture.live.expect("eligible D36 test task");
        let rows = r_rollouts(&live, task, 0, capture.resident.outcome.opponent_score);
        let branch = rows
            .iter()
            .find(|row| row.option > 0 && row.simulation.bundle_end_turn > row.epoch_turn)
            .expect("advancing D36 branch");
        let plan = branch.plan.as_ref().unwrap().plan.clone();
        let expected = branch.simulation.finish;
        let execution = r_execute_bundle(live, task, &plan);
        assert_eq!(execution.end_turn, branch.simulation.bundle_end_turn);
        assert_eq!(execution.statuses, branch.simulation.statuses);
        assert_eq!(
            execution.overridden_actions,
            branch.simulation.overridden_actions
        );
        assert_eq!(
            execution.invalid_direct_commands,
            branch.simulation.invalid_direct_commands
        );
        assert_eq!(r_finish(execution.live, task), expected);
    }

    #[test]
    fn repeated_task_respects_constraint_and_exact_epoch_chain() {
        let result = r_play_task(task());
        assert!(result.manifest.eligible);
        assert!(result.one_shot.is_some());
        assert!(result.unconstrained.is_some());
        assert!(result.repeated.is_some());
        assert_eq!(result.infeasible_selection_failures, 0);
        assert_eq!(result.replay_mismatches, 0);
        assert_eq!(result.strict_advance_failures, 0);
        assert_eq!(result.execution_prefix_mismatches, 0);
        assert!(
            result.repeated.unwrap().outcome.opponent_score
                <= result.manifest.resident.outcome.opponent_score + R_OPPONENT_EXCESS_CEILING
        );
        let mut grouped: BTreeMap<usize, Vec<&ROption>> = BTreeMap::new();
        for row in &result.options {
            grouped.entry(row.epoch).or_default().push(row);
        }
        let mut prior_end = None;
        for rows in grouped.values() {
            let selected = rows.iter().find(|row| row.selected).unwrap();
            let expected = rows
                .iter()
                .min_by(|left, right| r_constrained_order(left).cmp(&r_constrained_order(right)))
                .unwrap();
            assert_eq!(selected.option, expected.option);
            assert!(selected.feasible);
            assert!(selected.execution_prefix_match);
            assert!(selected.selected_rollout_replay_match);
            if let Some(end) = prior_end {
                assert_eq!(selected.epoch_turn, end);
            }
            prior_end = (selected.option > 0).then_some(selected.executed_end_turn);
        }
    }
}
