//! Implementation child of D35b so it can reuse the frozen private executor.

use super::*;

const MAX_COMPETITIVE_BASES: usize = 64;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum PlantOwner {
    Natural,
    Own,
    Opponent,
    Ambiguous,
}

impl PlantOwner {
    fn label(self) -> &'static str {
        match self {
            Self::Natural => "natural",
            Self::Own => "own",
            Self::Opponent => "opponent",
            Self::Ambiguous => "ambiguous",
        }
    }

    fn competitive(self) -> bool {
        matches!(self, Self::Opponent | Self::Ambiguous)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Catalog {
    Generic,
    Competitive,
}

impl Catalog {
    fn label(self) -> &'static str {
        match self {
            Self::Generic => "generic",
            Self::Competitive => "competitive",
        }
    }
}

#[derive(Clone)]
struct CPlan {
    plan: JointPlan,
    catalog: Catalog,
    owners: [Option<PlantOwner>; 2],
}

impl CPlan {
    fn opponent_targets(&self) -> usize {
        self.owners
            .iter()
            .filter(|owner| **owner == Some(PlantOwner::Opponent))
            .count()
    }

    fn ambiguous_targets(&self) -> usize {
        self.owners
            .iter()
            .filter(|owner| **owner == Some(PlantOwner::Ambiguous))
            .count()
    }

    fn competitive_targets(&self) -> usize {
        self.owners
            .iter()
            .filter(|owner| owner.map_or(false, PlantOwner::competitive))
            .count()
    }

    fn owner_tuple(&self) -> String {
        self.owners
            .iter()
            .map(|owner| owner.map_or("none", PlantOwner::label))
            .collect::<Vec<_>>()
            .join("+")
    }
}

#[derive(Clone)]
struct CRoot {
    root: Root,
    owners: BTreeMap<Cell, PlantOwner>,
    owner_counts: [usize; 4],
    plans: Vec<CPlan>,
    generic_plan_count: usize,
    competitive_plan_count: usize,
    has_competitive_target: bool,
    has_opponent_fell: bool,
    has_opponent_renew_or_harvest: bool,
    attribution_cell_mismatch: usize,
}

struct CManifest {
    task: Task,
    baseline: Outcome,
    resident: Outcome,
    roots: Vec<(i32, i32)>,
    attribution_failures: usize,
}

struct CRow {
    task: Task,
    checkpoint: i32,
    root_turn: i32,
    option: usize,
    plan: Option<CPlan>,
    simulation: Simulation,
    control: Outcome,
    baseline: Outcome,
    resident: Outcome,
    root_plan_count: usize,
    generic_plan_count: usize,
    competitive_plan_count: usize,
    has_competitive_target: bool,
    has_opponent_fell: bool,
    has_opponent_renew_or_harvest: bool,
    attribution_cell_mismatch: usize,
    owner_counts: [usize; 4],
}

struct CTaskResult {
    rows: Vec<CRow>,
    manifest: CManifest,
}

fn c_plant_attempts(game: &GameState, player: usize, commands: &[String]) -> BTreeSet<Cell> {
    commands
        .iter()
        .filter_map(|command| {
            let mut fields = command.split_whitespace();
            (fields.next()? == "PLANT").then_some(())?;
            let id = fields.next()?.parse::<i32>().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == player)
                .map(|unit| unit.pos())
        })
        .collect()
}

fn apply_with_provenance(
    game: &mut GameState,
    seat: usize,
    ours: &[String],
    theirs: &[String],
    owners: &mut BTreeMap<Cell, PlantOwner>,
) -> usize {
    let before: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    let our_attempts = c_plant_attempts(game, seat, ours);
    let their_attempts = c_plant_attempts(game, 1 - seat, theirs);
    apply_commands(game, seat, ours, theirs);
    let after: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    owners.retain(|cell, _| after.contains(cell));
    let mut failures = 0;
    for cell in after.difference(&before) {
        let owner = match (our_attempts.contains(cell), their_attempts.contains(cell)) {
            (true, false) => Some(PlantOwner::Own),
            (false, true) => Some(PlantOwner::Opponent),
            (true, true) => Some(PlantOwner::Ambiguous),
            (false, false) => None,
        };
        if let Some(owner) = owner {
            owners.insert(*cell, owner);
        } else {
            failures += 1;
        }
    }
    failures
        + owners
            .keys()
            .copied()
            .collect::<BTreeSet<_>>()
            .symmetric_difference(&after)
            .count()
}

fn plant_owner_counts(owners: &BTreeMap<Cell, PlantOwner>) -> [usize; 4] {
    let mut counts = [0; 4];
    for owner in owners.values() {
        counts[match owner {
            PlantOwner::Natural => 0,
            PlantOwner::Own => 1,
            PlantOwner::Opponent => 2,
            PlantOwner::Ambiguous => 3,
        }] += 1;
    }
    counts
}

fn owner_for_job(job: &JobSpec, owners: &BTreeMap<Cell, PlantOwner>) -> Option<PlantOwner> {
    match job.kind {
        JobKind::FellBank | JobKind::HarvestBank | JobKind::Renew => {
            job.target.and_then(|target| owners.get(&target).copied())
        }
        JobKind::Keep | JobKind::Bank | JobKind::MineBank => None,
    }
}

fn owners_for_jobs(
    jobs: &[JobSpec],
    owners: &BTreeMap<Cell, PlantOwner>,
) -> [Option<PlantOwner>; 2] {
    assert_eq!(jobs.len(), 2);
    [
        owner_for_job(&jobs[0], owners),
        owner_for_job(&jobs[1], owners),
    ]
}

fn generic_cplans(
    game: &GameState,
    player: usize,
    owners: &BTreeMap<Cell, PlantOwner>,
) -> Vec<CPlan> {
    joint_plans(game, player)
        .into_iter()
        .filter(|plan| plan.train_goal == TrainGoal::None)
        .map(|plan| CPlan {
            owners: owners_for_jobs(&plan.jobs, owners),
            plan,
            catalog: Catalog::Generic,
        })
        .collect()
}

fn competitive_jobs_for_owner(
    game: &GameState,
    player: usize,
    unit: &EngineUnit,
    owners: &BTreeMap<Cell, PlantOwner>,
    wanted: PlantOwner,
) -> Vec<JobSpec> {
    assert!(matches!(
        wanted,
        PlantOwner::Opponent | PlantOwner::Ambiguous
    ));
    let from_unit = bfs_distances(&game.walkable, &[unit.pos()]);
    let mut jobs = Vec::new();
    if unit.chop > 0 && unit.free() > 0 {
        let mut fell: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter(|plant| owners.get(&plant.pos()) == Some(&wanted))
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let chop = ceil_div(plant.health, unit.chop);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = 4 * plant.size.min(unit.free());
                Some((travel + chop + bank, -reward, plant.pos(), reward))
            })
            .collect();
        fell.sort_unstable();
        jobs.extend(
            fell.into_iter()
                .take(MAX_TARGETS_PER_KIND)
                .map(|(eta, _, target, reward)| JobSpec {
                    kind: JobKind::FellBank,
                    unit_id: unit.id,
                    target: Some(target),
                    plant_cell: None,
                    fruit_kind: None,
                    predicted_eta: eta,
                    predicted_reward: reward,
                }),
        );
    }
    if unit.hp > 0 && unit.free() > 0 {
        let mut harvest: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0 && plant.fruits > 0)
            .filter(|plant| owners.get(&plant.pos()) == Some(&wanted))
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = plant.fruits.min(unit.hp).min(unit.free());
                Some((
                    travel + 1 + bank,
                    -reward,
                    plant.pos(),
                    reward,
                    fruit_index(&plant.plant_type)?,
                ))
            })
            .collect();
        harvest.sort_unstable();
        jobs.extend(harvest.iter().take(MAX_TARGETS_PER_KIND).map(
            |(eta, _, target, reward, kind)| JobSpec {
                kind: JobKind::HarvestBank,
                unit_id: unit.id,
                target: Some(*target),
                plant_cell: None,
                fruit_kind: Some(*kind),
                predicted_eta: *eta,
                predicted_reward: *reward,
            },
        ));
        jobs.extend(harvest.into_iter().take(MAX_TARGETS_PER_KIND).filter_map(
            |(harvest_eta, _, target, reward, kind)| {
                let plant_cell = player_favored_plant_cell(game, player, target)?;
                let travel_to_plant = bfs_distances(&game.walkable, &[target])
                    .get(&plant_cell)
                    .copied()?;
                let (_, bank_distance) = nearest_door(game, player, plant_cell)?;
                Some(JobSpec {
                    kind: JobKind::Renew,
                    unit_id: unit.id,
                    target: Some(target),
                    plant_cell: Some(plant_cell),
                    fruit_kind: Some(kind),
                    predicted_eta: harvest_eta
                        + ceil_div(travel_to_plant, unit.ms)
                        + 1
                        + ceil_div(bank_distance, unit.ms)
                        + 1,
                    predicted_reward: reward + 16,
                })
            },
        ));
    }
    jobs.retain(|job| game.turn + job.predicted_eta <= TOTAL_TURNS);
    jobs.sort_by_key(|job| {
        (
            job.kind,
            job.predicted_eta,
            -job.predicted_reward,
            job.target,
            job.plant_cell,
        )
    });
    jobs.dedup_by_key(|job| (job.kind, job.target, job.plant_cell, job.fruit_kind));
    jobs
}

fn combined_unit_jobs(
    game: &GameState,
    player: usize,
    unit: &EngineUnit,
    owners: &BTreeMap<Cell, PlantOwner>,
) -> Vec<JobSpec> {
    let mut jobs = jobs_for_unit(game, player, unit);
    for wanted in [PlantOwner::Opponent, PlantOwner::Ambiguous] {
        jobs.extend(competitive_jobs_for_owner(
            game, player, unit, owners, wanted,
        ));
    }
    jobs.sort_by_key(JobSpec::key);
    jobs.dedup();
    jobs
}

fn cplan_from_jobs(
    jobs: Vec<JobSpec>,
    catalog: Catalog,
    owners: &BTreeMap<Cell, PlantOwner>,
) -> CPlan {
    let predicted_reward: i32 = jobs.iter().map(|job| job.predicted_reward).sum();
    let predicted_eta = jobs.iter().map(|job| job.predicted_eta).max().unwrap_or(0);
    let rate_score: i32 = jobs
        .iter()
        .map(|job| 1000 * job.predicted_reward / job.predicted_eta.max(1))
        .sum();
    let key = jobs.iter().map(JobSpec::key).collect::<Vec<_>>().join("+");
    let plan = JointPlan {
        jobs,
        train_goal: TrainGoal::None,
        key: format!("{key}|train=none"),
        rate_score,
        predicted_eta,
        predicted_reward,
    };
    CPlan {
        owners: owners_for_jobs(&plan.jobs, owners),
        plan,
        catalog,
    }
}

fn cplans(game: &GameState, player: usize, owners: &BTreeMap<Cell, PlantOwner>) -> Vec<CPlan> {
    let units = own_units(game, player);
    if units.len() != 2 {
        return Vec::new();
    }
    let generic = generic_cplans(game, player, owners);
    let generic_keys: BTreeSet<_> = generic.iter().map(|plan| plan.plan.key.clone()).collect();
    let first = combined_unit_jobs(game, player, units[0], owners);
    let second = combined_unit_jobs(game, player, units[1], owners);
    let mut competitive = Vec::new();
    for left in &first {
        for right in &second {
            if jobs_collide(left, right) {
                continue;
            }
            let plan = cplan_from_jobs(
                vec![left.clone(), right.clone()],
                Catalog::Competitive,
                owners,
            );
            if plan.competitive_targets() == 0 || generic_keys.contains(&plan.plan.key) {
                continue;
            }
            competitive.push(plan);
        }
    }
    competitive.sort_by(|left, right| {
        (
            -(left.opponent_targets() as i32),
            -(left.ambiguous_targets() as i32),
            -left.plan.rate_score,
            left.plan.predicted_eta,
            &left.plan.key,
        )
            .cmp(&(
                -(right.opponent_targets() as i32),
                -(right.ambiguous_targets() as i32),
                -right.plan.rate_score,
                right.plan.predicted_eta,
                &right.plan.key,
            ))
    });
    competitive.dedup_by(|left, right| left.plan.key == right.plan.key);
    competitive.truncate(MAX_COMPETITIVE_BASES);
    generic.into_iter().chain(competitive).collect()
}

fn capture_croots(task: Task) -> (Vec<CRoot>, Outcome, usize) {
    let mut game = generate_official(task.seed);
    let farm = productive_farm();
    let mut rival = opponent(task.opponent_index);
    let mut stall_counter = 0;
    let mut opponent_history = Vec::new();
    let mut captured = [false; CHECKPOINTS.len()];
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), PlantOwner::Natural))
        .collect();
    let mut attribution_failures = 0;
    let mut roots = Vec::new();
    while game.turn <= TOTAL_TURNS {
        let farm_before = farm.clone();
        let ours = farm.decide(&game, task.seat);
        for (index, checkpoint) in CHECKPOINTS.iter().copied().enumerate() {
            if !captured[index] && game.turn >= checkpoint && worker_count(&game, task.seat) == 2 {
                captured[index] = true;
                let plans = cplans(&game, task.seat, &owners);
                let generic_plan_count = plans
                    .iter()
                    .filter(|plan| plan.catalog == Catalog::Generic)
                    .count();
                let competitive_plan_count = plans.len() - generic_plan_count;
                let has_competitive_target =
                    plans.iter().any(|plan| plan.competitive_targets() > 0);
                let has_opponent_fell = plans.iter().any(|plan| {
                    plan.plan.jobs.iter().zip(plan.owners).any(|(job, owner)| {
                        job.kind == JobKind::FellBank && owner == Some(PlantOwner::Opponent)
                    })
                });
                let has_opponent_renew_or_harvest = plans.iter().any(|plan| {
                    plan.plan.jobs.iter().zip(plan.owners).any(|(job, owner)| {
                        matches!(job.kind, JobKind::HarvestBank | JobKind::Renew)
                            && owner == Some(PlantOwner::Opponent)
                    })
                });
                let live_cells: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
                let owner_cells: BTreeSet<_> = owners.keys().copied().collect();
                let attribution_cell_mismatch =
                    live_cells.symmetric_difference(&owner_cells).count();
                let base = Root {
                    checkpoint,
                    game: game.clone(),
                    farm: farm_before.clone(),
                    opponent_history: opponent_history.clone(),
                    stall_counter,
                    plans: Vec::new(),
                    has_renew: plans
                        .iter()
                        .any(|plan| plan.plan.jobs.iter().any(|job| job.kind == JobKind::Renew)),
                    has_fell: plans.iter().any(|plan| {
                        plan.plan
                            .jobs
                            .iter()
                            .any(|job| job.kind == JobKind::FellBank)
                    }),
                    has_mine: plans.iter().any(|plan| {
                        plan.plan
                            .jobs
                            .iter()
                            .any(|job| job.kind == JobKind::MineBank)
                    }),
                    has_train_goal: false,
                };
                roots.push(CRoot {
                    root: base,
                    owners: owners.clone(),
                    owner_counts: plant_owner_counts(&owners),
                    plans,
                    generic_plan_count,
                    competitive_plan_count,
                    has_competitive_target,
                    has_opponent_fell,
                    has_opponent_renew_or_harvest,
                    attribution_cell_mismatch,
                });
            }
        }
        let theirs = rival.commands(&game, 1 - task.seat);
        opponent_history.push(game.clone());
        attribution_failures +=
            apply_with_provenance(&mut game, task.seat, &ours, &theirs, &mut owners);
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    (
        roots,
        Outcome::from_game(&game, task.seat),
        attribution_failures,
    )
}

fn play_ctask(task: Task) -> CTaskResult {
    let resident = resident_reference(task);
    let (roots, baseline, attribution_failures) = capture_croots(task);
    let manifest_roots = roots
        .iter()
        .map(|root| (root.root.checkpoint, root.root.game.turn))
        .collect();
    let mut rows = Vec::new();
    for root in roots {
        let control_simulation = simulate(&root.root, task.seat, task.opponent_index, None);
        let control = control_simulation.outcome;
        rows.push(CRow {
            task,
            checkpoint: root.root.checkpoint,
            root_turn: root.root.game.turn,
            option: 0,
            plan: None,
            simulation: control_simulation,
            control,
            baseline,
            resident,
            root_plan_count: root.plans.len(),
            generic_plan_count: root.generic_plan_count,
            competitive_plan_count: root.competitive_plan_count,
            has_competitive_target: root.has_competitive_target,
            has_opponent_fell: root.has_opponent_fell,
            has_opponent_renew_or_harvest: root.has_opponent_renew_or_harvest,
            attribution_cell_mismatch: root.attribution_cell_mismatch,
            owner_counts: root.owner_counts,
        });
        for (index, plan) in root.plans.iter().cloned().enumerate() {
            rows.push(CRow {
                task,
                checkpoint: root.root.checkpoint,
                root_turn: root.root.game.turn,
                option: index + 1,
                plan: Some(plan.clone()),
                simulation: simulate(&root.root, task.seat, task.opponent_index, Some(&plan.plan)),
                control,
                baseline,
                resident,
                root_plan_count: root.plans.len(),
                generic_plan_count: root.generic_plan_count,
                competitive_plan_count: root.competitive_plan_count,
                has_competitive_target: root.has_competitive_target,
                has_opponent_fell: root.has_opponent_fell,
                has_opponent_renew_or_harvest: root.has_opponent_renew_or_harvest,
                attribution_cell_mismatch: root.attribution_cell_mismatch,
                owner_counts: root.owner_counts,
            });
        }
    }
    CTaskResult {
        rows,
        manifest: CManifest {
            task,
            baseline,
            resident,
            roots: manifest_roots,
            attribution_failures,
        },
    }
}

fn write_cmanifest(manifests: &[CManifest], output: &str) {
    let path = format!("{output}.scenarios.tsv");
    let mut writer = BufWriter::new(File::create(&path).expect("create D35c manifest"));
    writeln!(writer, "seed\tseat\topponent\troot_count\tcaptured_checkpoints\troot_turns\tattribution_failures\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_workers\tfarm_opponent_workers\tfarm_terminal_turn\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn").expect("write D35c manifest header");
    for entry in manifests {
        let checkpoints = entry
            .roots
            .iter()
            .map(|(checkpoint, _)| checkpoint.to_string())
            .collect::<Vec<_>>()
            .join(",");
        let root_turns = entry
            .roots
            .iter()
            .map(|(_, turn)| turn.to_string())
            .collect::<Vec<_>>()
            .join(",");
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            entry.task.seed,
            entry.task.seat,
            OPPONENTS[entry.task.opponent_index],
            entry.roots.len(),
            checkpoints,
            root_turns,
            entry.attribution_failures,
            entry.baseline.own_score,
            entry.baseline.opponent_score,
            entry.baseline.margin(),
            entry.baseline.own_workers,
            entry.baseline.opponent_workers,
            entry.baseline.terminal_turn,
            entry.resident.own_score,
            entry.resident.opponent_score,
            entry.resident.margin(),
            entry.resident.own_workers,
            entry.resident.opponent_workers,
            entry.resident.terminal_turn,
        )
        .expect("write D35c manifest row");
    }
    writer.flush().expect("flush D35c manifest");
}

fn write_crows(rows: &[CRow], output: &str) {
    let mut writer = BufWriter::new(File::create(output).expect("create D35c output"));
    writeln!(writer, "seed\tseat\topponent\tcheckpoint\troot_turn\toption\tcatalog\tplan_key\trole_tuple\ttarget_owners\tpredicted_eta\tpredicted_reward\trate_score\tstatuses\toverridden_actions\tinvalid_direct_commands\ttrain_success\tmax_own_workers\tbundle_end_turn\troot_plan_count\tgeneric_plan_count\tcompetitive_plan_count\tcompetitive_target_count\topponent_target_count\tambiguous_target_count\thas_competitive_target\thas_opponent_fell\thas_opponent_renew_or_harvest\tattribution_cell_mismatch\troot_natural_plants\troot_own_plants\troot_opponent_plants\troot_ambiguous_plants\town_score\topponent_score\tmargin\town_wood\topponent_wood\town_workers\topponent_workers\tterminal_turn\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_wood\tfarm_opponent_wood\tfarm_terminal_turn\tmargin_delta_farm\town_score_delta_farm\topponent_score_delta_farm\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tmargin_delta_resident\town_score_delta_resident\topponent_score_delta_resident\tcontrol_identity_match").expect("write D35c header");
    for row in rows {
        let (catalog, key, roles, owner_tuple, eta, reward, rate, competitive, opponent, ambiguous) =
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
            );
        let terminal = row.simulation.outcome;
        let fields = vec![
            row.task.seed.to_string(),
            row.task.seat.to_string(),
            OPPONENTS[row.task.opponent_index].to_string(),
            row.checkpoint.to_string(),
            row.root_turn.to_string(),
            row.option.to_string(),
            catalog,
            key,
            roles,
            owner_tuple,
            eta.to_string(),
            reward.to_string(),
            rate.to_string(),
            row.simulation.statuses.clone(),
            row.simulation.overridden_actions.to_string(),
            row.simulation.invalid_direct_commands.to_string(),
            usize::from(row.simulation.train_success).to_string(),
            row.simulation.max_own_workers.to_string(),
            row.simulation.bundle_end_turn.to_string(),
            row.root_plan_count.to_string(),
            row.generic_plan_count.to_string(),
            row.competitive_plan_count.to_string(),
            competitive.to_string(),
            opponent.to_string(),
            ambiguous.to_string(),
            usize::from(row.has_competitive_target).to_string(),
            usize::from(row.has_opponent_fell).to_string(),
            usize::from(row.has_opponent_renew_or_harvest).to_string(),
            row.attribution_cell_mismatch.to_string(),
            row.owner_counts[0].to_string(),
            row.owner_counts[1].to_string(),
            row.owner_counts[2].to_string(),
            row.owner_counts[3].to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            terminal.margin().to_string(),
            terminal.own_wood.to_string(),
            terminal.opponent_wood.to_string(),
            terminal.own_workers.to_string(),
            terminal.opponent_workers.to_string(),
            terminal.terminal_turn.to_string(),
            row.control.own_score.to_string(),
            row.control.opponent_score.to_string(),
            row.control.margin().to_string(),
            row.control.own_wood.to_string(),
            row.control.opponent_wood.to_string(),
            row.control.terminal_turn.to_string(),
            (terminal.margin() - row.control.margin()).to_string(),
            (terminal.own_score - row.control.own_score).to_string(),
            (terminal.opponent_score - row.control.opponent_score).to_string(),
            row.resident.own_score.to_string(),
            row.resident.opponent_score.to_string(),
            row.resident.margin().to_string(),
            row.resident.own_wood.to_string(),
            row.resident.opponent_wood.to_string(),
            (terminal.margin() - row.resident.margin()).to_string(),
            (terminal.own_score - row.resident.own_score).to_string(),
            (terminal.opponent_score - row.resident.opponent_score).to_string(),
            usize::from(row.control == row.baseline).to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D35c row");
    }
    writer.flush().expect("flush D35c output");
}

pub(crate) fn d35c_main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args.get(1).map_or(9_300_000, |value| {
        value.parse::<i64>().expect("signed seed start")
    });
    let seed_count = args
        .get(2)
        .map_or(1, |value| value.parse::<usize>().expect("seed count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d35c-provenance-competitive-bundle.tsv".to_string());
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
                    results.push(play_ctask(tasks[index]));
                }
                results
            })
        })
        .collect();
    let results: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D35c worker thread"))
        .collect();
    let mut rows = Vec::new();
    let mut manifests = Vec::new();
    for result in results {
        rows.extend(result.rows);
        manifests.push(result.manifest);
    }
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.seat,
            row.task.opponent_index,
            row.checkpoint,
            row.option,
        )
    });
    manifests.sort_by_key(|entry| (entry.task.seed, entry.task.seat, entry.task.opponent_index));
    write_crows(&rows, &output);
    write_cmanifest(&manifests, &output);
    eprintln!(
        "saved {} rows and {} scenario records from {} tasks in {:.3}s to {output}",
        rows.len(),
        manifests.len(),
        tasks.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod ctests {
    use super::*;

    fn empty_walkable(game: &GameState) -> Cell {
        game.walkable
            .iter()
            .copied()
            .find(|cell| !game.plants.iter().any(|plant| plant.pos() == *cell))
            .expect("empty official walkable cell")
    }

    #[test]
    fn simultaneous_same_cell_planting_is_ambiguous() {
        let mut game = generate_official(9_300_000);
        let target = empty_walkable(&game);
        let first = game.units.iter().find(|unit| unit.player == 0).unwrap().id;
        let second = game.units.iter().find(|unit| unit.player == 1).unwrap().id;
        for unit in &mut game.units {
            if unit.id == first || unit.id == second {
                unit.x = target.0;
                unit.y = target.1;
                unit.carry[3] = 1;
            }
        }
        let mut owners: BTreeMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), PlantOwner::Natural))
            .collect();
        let failures = apply_with_provenance(
            &mut game,
            0,
            &[format!("PLANT {first} BANANA")],
            &[format!("PLANT {second} BANANA")],
            &mut owners,
        );
        assert_eq!(failures, 0);
        assert_eq!(owners.get(&target), Some(&PlantOwner::Ambiguous));
        assert_eq!(owners.len(), game.plants.len());
    }

    #[test]
    fn exclusive_planting_respects_analyzed_seat_orientation() {
        let mut game = generate_official(9_300_001);
        let target = empty_walkable(&game);
        let id = game.units.iter().find(|unit| unit.player == 1).unwrap().id;
        let unit = game.units.iter_mut().find(|unit| unit.id == id).unwrap();
        unit.x = target.0;
        unit.y = target.1;
        unit.carry[3] = 1;
        let mut owners: BTreeMap<_, _> = game
            .plants
            .iter()
            .map(|plant| (plant.pos(), PlantOwner::Natural))
            .collect();
        assert_eq!(
            apply_with_provenance(
                &mut game,
                1,
                &[format!("PLANT {id} BANANA")],
                &[],
                &mut owners,
            ),
            0
        );
        assert_eq!(owners.get(&target), Some(&PlantOwner::Own));
    }

    #[test]
    fn generic_catalog_is_exact_subset_and_extension_is_bounded() {
        let task = Task {
            seed: 9_300_000,
            seat: 0,
            opponent_index: 2,
        };
        let (roots, _, failures) = capture_croots(task);
        assert_eq!(failures, 0);
        assert!(!roots.is_empty());
        for root in roots {
            assert_eq!(root.attribution_cell_mismatch, 0);
            let expected: BTreeSet<_> = generic_cplans(&root.root.game, task.seat, &root.owners)
                .into_iter()
                .map(|plan| plan.plan.key)
                .collect();
            let actual: BTreeSet<_> = root
                .plans
                .iter()
                .filter(|plan| plan.catalog == Catalog::Generic)
                .map(|plan| plan.plan.key.clone())
                .collect();
            assert_eq!(actual, expected);
            assert_eq!(root.generic_plan_count, expected.len());
            assert!(root.competitive_plan_count <= MAX_COMPETITIVE_BASES);
            assert!(root
                .plans
                .iter()
                .filter(|plan| plan.catalog == Catalog::Competitive)
                .all(|plan| plan.competitive_targets() > 0));
        }
    }

    #[test]
    fn controls_reproduce_farm_and_attribution_is_complete() {
        let task = Task {
            seed: 9_300_000,
            seat: 1,
            opponent_index: 2,
        };
        let (roots, baseline, failures) = capture_croots(task);
        assert_eq!(failures, 0);
        assert!(!roots.is_empty());
        for root in roots {
            let control = simulate(&root.root, task.seat, task.opponent_index, None);
            assert_eq!(control.outcome, baseline);
            assert_eq!(control.invalid_direct_commands, 0);
            assert_eq!(root.attribution_cell_mismatch, 0);
            assert_eq!(root.owners.len(), root.root.game.plants.len());
        }
    }
}

const D35D_MAX_NONCONTROL_EPOCHS: usize = 4;
const D35D_LAST_EPOCH_TURN: i32 = 220;

#[derive(Clone)]
struct DLive {
    game: GameState,
    farm: GoldElite,
    opponent_history: Vec<GameState>,
    stall_counter: i32,
    owners: BTreeMap<Cell, PlantOwner>,
    attribution_failures: usize,
    max_own_workers: usize,
    terminal: bool,
}

struct DExecution {
    live: DLive,
    statuses: String,
    overridden_actions: usize,
    invalid_direct_commands: usize,
    end_turn: i32,
    terminal: bool,
}

struct DFinish {
    outcome: Outcome,
    attribution_failures: usize,
    history_mismatch: usize,
    max_own_workers: usize,
    terminal_hash: u64,
}

struct DEpochOption {
    epoch: usize,
    epoch_turn: i32,
    option: usize,
    plan: Option<CPlan>,
    outcome: Outcome,
    statuses: String,
    overridden_actions: usize,
    invalid_direct_commands: usize,
    rollout_train_success: bool,
    rollout_max_own_workers: usize,
    rollout_bundle_end_turn: i32,
    selected: bool,
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
    attribution_cell_mismatch: usize,
    owner_counts: [usize; 4],
    history_mismatch: usize,
}

struct DManifest {
    task: Task,
    eligible: bool,
    start_turn: i32,
    prefix_attribution_failures: usize,
    farm_attribution_failures: usize,
    start_history_mismatch: usize,
    start_cell_mismatch: usize,
    farm_max_own_workers: usize,
    farm: Outcome,
    resident: Outcome,
}

struct DTaskResult {
    task: Task,
    options: Vec<DEpochOption>,
    manifest: DManifest,
    one_shot: Option<Outcome>,
    one_shot_catalog: String,
    one_shot_key: String,
    repeated: Option<DFinish>,
    selected_noncontrol_epochs: usize,
    selected_competitive_epochs: usize,
    stop_reason: String,
    selection_mismatches: usize,
    replay_mismatches: usize,
    strict_advance_failures: usize,
    execution_prefix_mismatches: usize,
}

struct DStartCapture {
    live: Option<DLive>,
    prefix_attribution_failures: usize,
    farm_attribution_failures: usize,
    start_history_mismatch: usize,
    start_cell_mismatch: usize,
    farm_max_own_workers: usize,
    farm: Outcome,
}

fn d_history_mismatch(live: &DLive) -> usize {
    live.opponent_history
        .len()
        .abs_diff((live.game.turn - 1).max(0) as usize)
}

fn d_cell_mismatch(game: &GameState, owners: &BTreeMap<Cell, PlantOwner>) -> usize {
    let live_cells: BTreeSet<_> = game.plants.iter().map(|plant| plant.pos()).collect();
    let owner_cells: BTreeSet<_> = owners.keys().copied().collect();
    live_cells.symmetric_difference(&owner_cells).count()
}

fn d_capture_start(task: Task) -> DStartCapture {
    let mut game = generate_official(task.seed);
    let farm = productive_farm();
    let mut rival = opponent(task.opponent_index);
    let mut stall_counter = 0;
    let mut opponent_history = Vec::new();
    let mut owners: BTreeMap<_, _> = game
        .plants
        .iter()
        .map(|plant| (plant.pos(), PlantOwner::Natural))
        .collect();
    let mut attribution_failures = 0;
    let mut farm_max_own_workers = worker_count(&game, task.seat);
    let mut live = None;
    let mut prefix_attribution_failures = 0;
    let mut start_history_mismatch = 0;
    let mut start_cell_mismatch = 0;

    while game.turn <= TOTAL_TURNS {
        let farm_before = farm.clone();
        let ours = farm.decide(&game, task.seat);
        if live.is_none() && game.turn >= 50 && worker_count(&game, task.seat) == 2 {
            prefix_attribution_failures = attribution_failures;
            let snapshot = DLive {
                game: game.clone(),
                farm: farm_before,
                opponent_history: opponent_history.clone(),
                stall_counter,
                owners: owners.clone(),
                attribution_failures,
                max_own_workers: farm_max_own_workers,
                terminal: false,
            };
            start_history_mismatch = d_history_mismatch(&snapshot);
            start_cell_mismatch = d_cell_mismatch(&snapshot.game, &snapshot.owners);
            live = Some(snapshot);
        }
        let theirs = rival.commands(&game, 1 - task.seat);
        opponent_history.push(game.clone());
        attribution_failures +=
            apply_with_provenance(&mut game, task.seat, &ours, &theirs, &mut owners);
        farm_max_own_workers = farm_max_own_workers.max(worker_count(&game, task.seat));
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }

    DStartCapture {
        live,
        prefix_attribution_failures,
        farm_attribution_failures: attribution_failures,
        start_history_mismatch,
        start_cell_mismatch,
        farm_max_own_workers,
        farm: Outcome::from_game(&game, task.seat),
    }
}

fn d_croot(live: &DLive, player: usize, checkpoint: i32) -> CRoot {
    let plans = cplans(&live.game, player, &live.owners);
    let generic_plan_count = plans
        .iter()
        .filter(|plan| plan.catalog == Catalog::Generic)
        .count();
    let competitive_plan_count = plans.len() - generic_plan_count;
    let has_competitive_target = plans.iter().any(|plan| plan.competitive_targets() > 0);
    let has_opponent_fell = plans.iter().any(|plan| {
        plan.plan.jobs.iter().zip(plan.owners).any(|(job, owner)| {
            job.kind == JobKind::FellBank && owner == Some(PlantOwner::Opponent)
        })
    });
    let has_opponent_renew_or_harvest = plans.iter().any(|plan| {
        plan.plan.jobs.iter().zip(plan.owners).any(|(job, owner)| {
            matches!(job.kind, JobKind::HarvestBank | JobKind::Renew)
                && owner == Some(PlantOwner::Opponent)
        })
    });
    let live_cells: BTreeSet<_> = live.game.plants.iter().map(|plant| plant.pos()).collect();
    let owner_cells: BTreeSet<_> = live.owners.keys().copied().collect();
    let attribution_cell_mismatch = live_cells.symmetric_difference(&owner_cells).count();
    CRoot {
        root: Root {
            checkpoint,
            game: live.game.clone(),
            farm: live.farm.clone(),
            opponent_history: live.opponent_history.clone(),
            stall_counter: live.stall_counter,
            plans: Vec::new(),
            has_renew: plans
                .iter()
                .any(|plan| plan.plan.jobs.iter().any(|job| job.kind == JobKind::Renew)),
            has_fell: plans.iter().any(|plan| {
                plan.plan
                    .jobs
                    .iter()
                    .any(|job| job.kind == JobKind::FellBank)
            }),
            has_mine: plans.iter().any(|plan| {
                plan.plan
                    .jobs
                    .iter()
                    .any(|job| job.kind == JobKind::MineBank)
            }),
            has_train_goal: false,
        },
        owners: live.owners.clone(),
        owner_counts: plant_owner_counts(&live.owners),
        plans,
        generic_plan_count,
        competitive_plan_count,
        has_competitive_target,
        has_opponent_fell,
        has_opponent_renew_or_harvest,
        attribution_cell_mismatch,
    }
}

fn d_rollouts(root: &CRoot, task: Task, epoch: usize) -> Vec<DEpochOption> {
    let mut rows = Vec::with_capacity(root.plans.len() + 1);
    let control = simulate(&root.root, task.seat, task.opponent_index, None);
    rows.push(DEpochOption {
        epoch,
        epoch_turn: root.root.game.turn,
        option: 0,
        plan: None,
        outcome: control.outcome,
        statuses: control.statuses,
        overridden_actions: control.overridden_actions,
        invalid_direct_commands: control.invalid_direct_commands,
        rollout_train_success: control.train_success,
        rollout_max_own_workers: control.max_own_workers,
        rollout_bundle_end_turn: control.bundle_end_turn,
        selected: false,
        executed_end_turn: -1,
        execution_statuses: String::new(),
        execution_overridden_actions: 0,
        execution_invalid_direct_commands: 0,
        execution_terminal: false,
        execution_prefix_match: false,
        selected_rollout_replay_match: false,
        root_plan_count: root.plans.len(),
        generic_plan_count: root.generic_plan_count,
        competitive_plan_count: root.competitive_plan_count,
        attribution_cell_mismatch: root.attribution_cell_mismatch,
        owner_counts: root.owner_counts,
        history_mismatch: root
            .root
            .opponent_history
            .len()
            .abs_diff((root.root.game.turn - 1).max(0) as usize),
    });
    for (index, plan) in root.plans.iter().cloned().enumerate() {
        let simulation = simulate(&root.root, task.seat, task.opponent_index, Some(&plan.plan));
        rows.push(DEpochOption {
            epoch,
            epoch_turn: root.root.game.turn,
            option: index + 1,
            plan: Some(plan),
            outcome: simulation.outcome,
            statuses: simulation.statuses,
            overridden_actions: simulation.overridden_actions,
            invalid_direct_commands: simulation.invalid_direct_commands,
            rollout_train_success: simulation.train_success,
            rollout_max_own_workers: simulation.max_own_workers,
            rollout_bundle_end_turn: simulation.bundle_end_turn,
            selected: false,
            executed_end_turn: -1,
            execution_statuses: String::new(),
            execution_overridden_actions: 0,
            execution_invalid_direct_commands: 0,
            execution_terminal: false,
            execution_prefix_match: false,
            selected_rollout_replay_match: false,
            root_plan_count: root.plans.len(),
            generic_plan_count: root.generic_plan_count,
            competitive_plan_count: root.competitive_plan_count,
            attribution_cell_mismatch: root.attribution_cell_mismatch,
            owner_counts: root.owner_counts,
            history_mismatch: root
                .root
                .opponent_history
                .len()
                .abs_diff((root.root.game.turn - 1).max(0) as usize),
        });
    }
    rows
}

fn d_option_order(row: &DEpochOption) -> (i32, usize, usize, &str) {
    (
        -row.outcome.margin(),
        usize::from(row.option != 0),
        row.overridden_actions,
        row.plan
            .as_ref()
            .map_or("control", |plan| plan.plan.key.as_str()),
    )
}

fn d_selected_index(rows: &[DEpochOption]) -> usize {
    (0..rows.len())
        .min_by(|left, right| d_option_order(&rows[*left]).cmp(&d_option_order(&rows[*right])))
        .expect("epoch has control")
}

fn d_execute_bundle(mut live: DLive, task: Task, plan: &JointPlan) -> DExecution {
    assert!(
        !live.terminal,
        "cannot execute a D35d bundle after terminal"
    );
    let root = Root {
        checkpoint: live.game.turn,
        game: live.game.clone(),
        farm: live.farm.clone(),
        opponent_history: live.opponent_history.clone(),
        stall_counter: live.stall_counter,
        plans: Vec::new(),
        has_renew: false,
        has_fell: false,
        has_mine: false,
        has_train_goal: false,
    };
    let mut rival = warmed_opponent(&root, task.opponent_index, task.seat);
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
    assert!(!active.is_empty(), "D35d never executes all-KEEP control");
    let mut overridden_actions = 0;
    let mut invalid_direct_commands = 0;
    loop {
        if live.game.turn > TOTAL_TURNS {
            live.terminal = true;
            break;
        }
        let farm_before = live.farm.clone();
        let mut ours = live.farm.decide(&live.game, task.seat);
        let ids: Vec<_> = active.keys().copied().collect();
        for id in ids {
            let result = active
                .get_mut(&id)
                .expect("D35d active job")
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
            live.farm = farm_before;
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
    let terminal = live.terminal;
    let statuses = status
        .iter()
        .map(|(id, value)| format!("{id}:{value}"))
        .collect::<Vec<_>>()
        .join(",");
    DExecution {
        end_turn: live.game.turn,
        live,
        statuses,
        overridden_actions,
        invalid_direct_commands,
        terminal,
    }
}

const D_HASH_OFFSET: u64 = 0xcbf29ce484222325;
const D_HASH_PRIME: u64 = 0x100000001b3;

fn d_hash_bytes(hash: &mut u64, bytes: &[u8]) {
    for byte in bytes {
        *hash ^= u64::from(*byte);
        *hash = hash.wrapping_mul(D_HASH_PRIME);
    }
    *hash ^= 0xff;
    *hash = hash.wrapping_mul(D_HASH_PRIME);
}

fn d_hash_i32(hash: &mut u64, value: i32) {
    d_hash_bytes(hash, &value.to_le_bytes());
}

fn d_terminal_hash(game: &GameState, owners: &BTreeMap<Cell, PlantOwner>) -> u64 {
    let mut hash = D_HASH_OFFSET;
    for value in [game.width, game.height, game.turn, game.next_id] {
        d_hash_i32(&mut hash, value);
    }
    for cell in game.shacks {
        d_hash_i32(&mut hash, cell.0);
        d_hash_i32(&mut hash, cell.1);
    }
    for values in game.inventories {
        for value in values {
            d_hash_i32(&mut hash, value);
        }
    }
    for value in game.scores {
        d_hash_i32(&mut hash, value);
    }
    let mut units = game.units.clone();
    units.sort_by_key(|unit| unit.id);
    for unit in units {
        for value in [
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ] {
            d_hash_i32(&mut hash, value);
        }
        for value in unit.carry {
            d_hash_i32(&mut hash, value);
        }
    }
    let mut plants = game.plants.clone();
    plants.sort_by_key(|plant| (plant.pos(), plant.plant_type.clone()));
    for plant in plants {
        d_hash_bytes(&mut hash, plant.plant_type.as_bytes());
        for value in [
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ] {
            d_hash_i32(&mut hash, value);
        }
    }
    for cells in [&game.walkable, &game.iron, &game.water] {
        let mut sorted: Vec<_> = cells.iter().copied().collect();
        sorted.sort_unstable();
        for cell in sorted {
            d_hash_i32(&mut hash, cell.0);
            d_hash_i32(&mut hash, cell.1);
        }
    }
    for (cell, owner) in owners {
        d_hash_i32(&mut hash, cell.0);
        d_hash_i32(&mut hash, cell.1);
        d_hash_bytes(&mut hash, owner.label().as_bytes());
    }
    hash
}

fn d_finish(mut live: DLive, task: Task) -> DFinish {
    let root = Root {
        checkpoint: live.game.turn,
        game: live.game.clone(),
        farm: live.farm.clone(),
        opponent_history: live.opponent_history.clone(),
        stall_counter: live.stall_counter,
        plans: Vec::new(),
        has_renew: false,
        has_fell: false,
        has_mine: false,
        has_train_goal: false,
    };
    if !live.terminal {
        let mut rival = warmed_opponent(&root, task.opponent_index, task.seat);
        while live.game.turn <= TOTAL_TURNS {
            let ours = live.farm.decide(&live.game, task.seat);
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
    DFinish {
        outcome: Outcome::from_game(&live.game, task.seat),
        attribution_failures: live.attribution_failures,
        history_mismatch: d_history_mismatch(&live),
        max_own_workers: live.max_own_workers,
        terminal_hash: d_terminal_hash(&live.game, &live.owners),
    }
}

fn d_identity(row: &DEpochOption) -> (String, String) {
    row.plan.as_ref().map_or_else(
        || ("control".to_string(), "control".to_string()),
        |plan| (plan.catalog.label().to_string(), plan.plan.key.clone()),
    )
}

fn d_play_task(task: Task) -> DTaskResult {
    let resident = resident_reference(task);
    let capture = d_capture_start(task);
    let start_turn = capture.live.as_ref().map_or(-1, |live| live.game.turn);
    let manifest = DManifest {
        task,
        eligible: capture.live.is_some(),
        start_turn,
        prefix_attribution_failures: capture.prefix_attribution_failures,
        farm_attribution_failures: capture.farm_attribution_failures,
        start_history_mismatch: capture.start_history_mismatch,
        start_cell_mismatch: capture.start_cell_mismatch,
        farm_max_own_workers: capture.farm_max_own_workers,
        farm: capture.farm,
        resident,
    };
    let Some(mut live) = capture.live else {
        return DTaskResult {
            task,
            options: Vec::new(),
            manifest,
            one_shot: None,
            one_shot_catalog: "none".to_string(),
            one_shot_key: "none".to_string(),
            repeated: None,
            selected_noncontrol_epochs: 0,
            selected_competitive_epochs: 0,
            stop_reason: "ineligible".to_string(),
            selection_mismatches: 0,
            replay_mismatches: 0,
            strict_advance_failures: 0,
            execution_prefix_mismatches: 0,
        };
    };

    let mut options = Vec::new();
    let mut epoch = 0usize;
    let mut one_shot = None;
    let mut one_shot_catalog = String::new();
    let mut one_shot_key = String::new();
    let mut selected_noncontrol_epochs = 0usize;
    let mut selected_competitive_epochs = 0usize;
    let selection_mismatches = 0usize;
    let mut replay_mismatches = 0usize;
    let mut strict_advance_failures = 0usize;
    let mut execution_prefix_mismatches = 0usize;
    let mut stop_reason = String::new();

    let repeated = loop {
        if live.terminal {
            stop_reason = "terminal".to_string();
            break d_finish(live, task);
        }
        if selected_noncontrol_epochs >= D35D_MAX_NONCONTROL_EPOCHS {
            stop_reason = "epoch_cap".to_string();
            break d_finish(live, task);
        }
        if live.game.turn > D35D_LAST_EPOCH_TURN {
            stop_reason = "turn_cutoff".to_string();
            break d_finish(live, task);
        }

        let root = d_croot(&live, task.seat, live.game.turn);
        let mut epoch_rows = d_rollouts(&root, task, epoch);
        let selected_index = d_selected_index(&epoch_rows);
        epoch_rows[selected_index].selected = true;
        let selected_outcome = epoch_rows[selected_index].outcome;
        let (selected_catalog, selected_key) = d_identity(&epoch_rows[selected_index]);
        if epoch == 0 {
            one_shot = Some(selected_outcome);
            one_shot_catalog = selected_catalog.clone();
            one_shot_key = selected_key.clone();
        }

        let Some(selected_plan) = epoch_rows[selected_index].plan.clone() else {
            let finish = d_finish(live.clone(), task);
            let replay_match = finish.outcome == selected_outcome;
            replay_mismatches += usize::from(!replay_match);
            let selected = &mut epoch_rows[selected_index];
            selected.executed_end_turn = selected.epoch_turn;
            selected.execution_statuses = selected.statuses.clone();
            selected.execution_overridden_actions = selected.overridden_actions;
            selected.execution_invalid_direct_commands = selected.invalid_direct_commands;
            selected.execution_terminal = live.terminal;
            selected.execution_prefix_match =
                selected.rollout_bundle_end_turn == selected.epoch_turn;
            selected.selected_rollout_replay_match = replay_match;
            execution_prefix_mismatches += usize::from(!selected.execution_prefix_match);
            options.extend(epoch_rows);
            stop_reason = "control".to_string();
            break finish;
        };

        let epoch_turn = epoch_rows[selected_index].epoch_turn;
        let rollout_statuses = epoch_rows[selected_index].statuses.clone();
        let rollout_overrides = epoch_rows[selected_index].overridden_actions;
        let rollout_invalid = epoch_rows[selected_index].invalid_direct_commands;
        let rollout_bundle_end = epoch_rows[selected_index].rollout_bundle_end_turn;
        let execution = d_execute_bundle(live, task, &selected_plan.plan);
        let prefix_match = execution.end_turn == rollout_bundle_end
            && execution.statuses == rollout_statuses
            && execution.overridden_actions == rollout_overrides
            && execution.invalid_direct_commands == rollout_invalid;
        execution_prefix_mismatches += usize::from(!prefix_match);
        strict_advance_failures +=
            usize::from(execution.end_turn <= epoch_turn && !execution.terminal);
        let replay = d_finish(execution.live.clone(), task);
        let replay_match = replay.outcome == selected_outcome;
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

    DTaskResult {
        task,
        options,
        manifest,
        one_shot,
        one_shot_catalog,
        one_shot_key,
        repeated: Some(repeated),
        selected_noncontrol_epochs,
        selected_competitive_epochs,
        stop_reason,
        selection_mismatches,
        replay_mismatches,
        strict_advance_failures,
        execution_prefix_mismatches,
    }
}

fn write_dmanifest(results: &[DTaskResult], output: &str) {
    let path = format!("{output}.scenarios.tsv");
    let mut writer = BufWriter::new(File::create(&path).expect("create D35d manifest"));
    writeln!(writer, "seed\tseat\topponent\teligible\tstart_turn\tprefix_attribution_failures\tfarm_attribution_failures\tstart_history_mismatch\tstart_cell_mismatch\tfarm_max_own_workers\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_wood\tfarm_opponent_wood\tfarm_own_workers\tfarm_opponent_workers\tfarm_terminal_turn\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn").expect("write D35d manifest header");
    for result in results {
        let entry = &result.manifest;
        let farm = entry.farm;
        let resident = entry.resident;
        let fields = vec![
            entry.task.seed.to_string(),
            entry.task.seat.to_string(),
            OPPONENTS[entry.task.opponent_index].to_string(),
            usize::from(entry.eligible).to_string(),
            entry.start_turn.to_string(),
            entry.prefix_attribution_failures.to_string(),
            entry.farm_attribution_failures.to_string(),
            entry.start_history_mismatch.to_string(),
            entry.start_cell_mismatch.to_string(),
            entry.farm_max_own_workers.to_string(),
            farm.own_score.to_string(),
            farm.opponent_score.to_string(),
            farm.margin().to_string(),
            farm.own_wood.to_string(),
            farm.opponent_wood.to_string(),
            farm.own_workers.to_string(),
            farm.opponent_workers.to_string(),
            farm.terminal_turn.to_string(),
            resident.own_score.to_string(),
            resident.opponent_score.to_string(),
            resident.margin().to_string(),
            resident.own_wood.to_string(),
            resident.opponent_wood.to_string(),
            resident.own_workers.to_string(),
            resident.opponent_workers.to_string(),
            resident.terminal_turn.to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D35d manifest row");
    }
    writer.flush().expect("flush D35d manifest");
}

fn d_plan_fields(
    row: &DEpochOption,
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

fn write_drows(results: &[DTaskResult], output: &str) {
    let mut writer = BufWriter::new(File::create(output).expect("create D35d output"));
    writeln!(writer, "seed\tseat\topponent\tepoch\tepoch_turn\toption\tselected\tcatalog\tplan_key\trole_tuple\ttarget_owners\tpredicted_eta\tpredicted_reward\trate_score\tcompetitive_target_count\topponent_target_count\tambiguous_target_count\trollout_statuses\trollout_overridden_actions\trollout_invalid_direct_commands\trollout_train_success\trollout_max_own_workers\trollout_bundle_end_turn\trollout_own_score\trollout_opponent_score\trollout_margin\trollout_own_wood\trollout_opponent_wood\trollout_own_workers\trollout_opponent_workers\trollout_terminal_turn\troot_plan_count\tgeneric_plan_count\tcompetitive_plan_count\troot_natural_plants\troot_own_plants\troot_opponent_plants\troot_ambiguous_plants\tattribution_cell_mismatch\thistory_mismatch\texecuted_end_turn\texecution_statuses\texecution_overridden_actions\texecution_invalid_direct_commands\texecution_terminal\texecution_prefix_match\tselected_rollout_replay_match\tone_shot_catalog\tone_shot_key\tone_shot_own_score\tone_shot_opponent_score\tone_shot_margin\tone_shot_own_wood\tone_shot_opponent_wood\tone_shot_own_workers\tone_shot_opponent_workers\tone_shot_terminal_turn\tselected_noncontrol_epochs\tselected_competitive_epochs\tstop_reason\tselection_mismatches\treplay_mismatches\tstrict_advance_failures\texecution_prefix_mismatches\trepeated_own_score\trepeated_opponent_score\trepeated_margin\trepeated_own_wood\trepeated_opponent_wood\trepeated_own_workers\trepeated_opponent_workers\trepeated_terminal_turn\trepeated_attribution_failures\trepeated_history_mismatch\trepeated_max_own_workers\trepeated_terminal_hash\tfarm_own_score\tfarm_opponent_score\tfarm_margin\tfarm_own_wood\tfarm_opponent_wood\tfarm_own_workers\tfarm_opponent_workers\tfarm_terminal_turn\tresident_own_score\tresident_opponent_score\tresident_margin\tresident_own_wood\tresident_opponent_wood\tresident_own_workers\tresident_opponent_workers\tresident_terminal_turn\trepeated_margin_delta_farm\trepeated_own_score_delta_farm\trepeated_opponent_score_delta_farm\trepeated_margin_delta_resident\trepeated_own_score_delta_resident\trepeated_opponent_score_delta_resident\trepeated_margin_delta_one_shot\trepeated_own_score_delta_one_shot\trepeated_opponent_score_delta_one_shot\tone_shot_margin_delta_farm\tone_shot_own_score_delta_farm\tone_shot_opponent_score_delta_farm\tone_shot_margin_delta_resident\tone_shot_own_score_delta_resident\tone_shot_opponent_score_delta_resident").expect("write D35d header");
    for result in results {
        if result.options.is_empty() {
            continue;
        }
        let one_shot = result.one_shot.expect("eligible D35d one-shot");
        let repeated = result.repeated.as_ref().expect("eligible D35d repeated");
        let final_outcome = repeated.outcome;
        let farm = result.manifest.farm;
        let resident = result.manifest.resident;
        for row in &result.options {
            let (catalog, key, roles, owners, eta, reward, rate, competitive, opponent, ambiguous) =
                d_plan_fields(row);
            let rollout = row.outcome;
            let fields = vec![
                result.task.seed.to_string(),
                result.task.seat.to_string(),
                OPPONENTS[result.task.opponent_index].to_string(),
                row.epoch.to_string(),
                row.epoch_turn.to_string(),
                row.option.to_string(),
                usize::from(row.selected).to_string(),
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
                row.statuses.clone(),
                row.overridden_actions.to_string(),
                row.invalid_direct_commands.to_string(),
                usize::from(row.rollout_train_success).to_string(),
                row.rollout_max_own_workers.to_string(),
                row.rollout_bundle_end_turn.to_string(),
                rollout.own_score.to_string(),
                rollout.opponent_score.to_string(),
                rollout.margin().to_string(),
                rollout.own_wood.to_string(),
                rollout.opponent_wood.to_string(),
                rollout.own_workers.to_string(),
                rollout.opponent_workers.to_string(),
                rollout.terminal_turn.to_string(),
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
                one_shot.own_score.to_string(),
                one_shot.opponent_score.to_string(),
                one_shot.margin().to_string(),
                one_shot.own_wood.to_string(),
                one_shot.opponent_wood.to_string(),
                one_shot.own_workers.to_string(),
                one_shot.opponent_workers.to_string(),
                one_shot.terminal_turn.to_string(),
                result.selected_noncontrol_epochs.to_string(),
                result.selected_competitive_epochs.to_string(),
                result.stop_reason.clone(),
                result.selection_mismatches.to_string(),
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
                repeated.max_own_workers.to_string(),
                repeated.terminal_hash.to_string(),
                farm.own_score.to_string(),
                farm.opponent_score.to_string(),
                farm.margin().to_string(),
                farm.own_wood.to_string(),
                farm.opponent_wood.to_string(),
                farm.own_workers.to_string(),
                farm.opponent_workers.to_string(),
                farm.terminal_turn.to_string(),
                resident.own_score.to_string(),
                resident.opponent_score.to_string(),
                resident.margin().to_string(),
                resident.own_wood.to_string(),
                resident.opponent_wood.to_string(),
                resident.own_workers.to_string(),
                resident.opponent_workers.to_string(),
                resident.terminal_turn.to_string(),
                (final_outcome.margin() - farm.margin()).to_string(),
                (final_outcome.own_score - farm.own_score).to_string(),
                (final_outcome.opponent_score - farm.opponent_score).to_string(),
                (final_outcome.margin() - resident.margin()).to_string(),
                (final_outcome.own_score - resident.own_score).to_string(),
                (final_outcome.opponent_score - resident.opponent_score).to_string(),
                (final_outcome.margin() - one_shot.margin()).to_string(),
                (final_outcome.own_score - one_shot.own_score).to_string(),
                (final_outcome.opponent_score - one_shot.opponent_score).to_string(),
                (one_shot.margin() - farm.margin()).to_string(),
                (one_shot.own_score - farm.own_score).to_string(),
                (one_shot.opponent_score - farm.opponent_score).to_string(),
                (one_shot.margin() - resident.margin()).to_string(),
                (one_shot.own_score - resident.own_score).to_string(),
                (one_shot.opponent_score - resident.opponent_score).to_string(),
            ];
            writeln!(writer, "{}", fields.join("\t")).expect("write D35d row");
        }
    }
    writer.flush().expect("flush D35d output");
}

pub(crate) fn d35d_main() {
    let args: Vec<String> = std::env::args().collect();
    let seed_start = args.get(1).map_or(9_400_000, |value| {
        value.parse::<i64>().expect("signed seed start")
    });
    let seed_count = args
        .get(2)
        .map_or(1, |value| value.parse::<usize>().expect("seed count"));
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "d35d-repeated-job-boundary-oracle.tsv".to_string());
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
                    results.push(d_play_task(tasks[index]));
                }
                results
            })
        })
        .collect();
    let mut results: Vec<_> = handles
        .into_iter()
        .flat_map(|handle| handle.join().expect("D35d worker thread"))
        .collect();
    results.sort_by_key(|result| {
        (
            result.task.seed,
            result.task.seat,
            result.task.opponent_index,
        )
    });
    let row_count: usize = results.iter().map(|result| result.options.len()).sum();
    write_drows(&results, &output);
    write_dmanifest(&results, &output);
    eprintln!(
        "saved {row_count} rows and {} scenario records from {} tasks in {:.3}s to {output}",
        results.len(),
        tasks.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod dtests {
    use super::*;

    fn task() -> Task {
        Task {
            seed: 9_400_000,
            seat: 0,
            opponent_index: 2,
        }
    }

    #[test]
    fn start_matches_frozen_croot_and_farm_control() {
        let task = task();
        let capture = d_capture_start(task);
        assert_eq!(capture.prefix_attribution_failures, 0);
        assert_eq!(capture.farm_attribution_failures, 0);
        assert_eq!(capture.start_history_mismatch, 0);
        assert_eq!(capture.start_cell_mismatch, 0);
        let live = capture.live.expect("eligible D35d test task");
        let (roots, farm, failures) = capture_croots(task);
        assert_eq!(failures, 0);
        let frozen = roots
            .iter()
            .find(|root| root.root.checkpoint == 50)
            .expect("frozen checkpoint-50 root");
        assert_eq!(live.game.turn, frozen.root.game.turn);
        assert_eq!(
            d_terminal_hash(&live.game, &live.owners),
            d_terminal_hash(&frozen.root.game, &frozen.owners)
        );
        assert_eq!(capture.farm, farm);
        assert_eq!(d_finish(live, task).outcome, farm);
    }

    #[test]
    fn executor_returns_before_exact_farm_continuation_boundary() {
        let task = task();
        let live = d_capture_start(task).live.expect("eligible D35d test task");
        let root = d_croot(&live, task.seat, live.game.turn);
        let rows = d_rollouts(&root, task, 0);
        let branch = rows
            .iter()
            .find(|row| row.option > 0 && row.rollout_bundle_end_turn > row.epoch_turn)
            .expect("advancing D35d branch");
        let plan = branch.plan.as_ref().expect("noncontrol plan").plan.clone();
        let expected = branch.outcome;
        let statuses = branch.statuses.clone();
        let overrides = branch.overridden_actions;
        let invalid = branch.invalid_direct_commands;
        let boundary = branch.rollout_bundle_end_turn;
        let execution = d_execute_bundle(live, task, &plan);
        assert_eq!(execution.end_turn, boundary);
        assert_eq!(execution.statuses, statuses);
        assert_eq!(execution.overridden_actions, overrides);
        assert_eq!(execution.invalid_direct_commands, invalid);
        assert_eq!(d_history_mismatch(&execution.live), 0);
        assert_eq!(d_finish(execution.live, task).outcome, expected);
    }

    #[test]
    fn frozen_tie_break_prefers_control() {
        let task = task();
        let live = d_capture_start(task).live.expect("eligible D35d test task");
        let root = d_croot(&live, task.seat, live.game.turn);
        let mut rows = d_rollouts(&root, task, 0);
        rows.truncate(2);
        assert_eq!(rows.len(), 2);
        rows[1].outcome = rows[0].outcome;
        rows[1].overridden_actions = 0;
        assert_eq!(d_selected_index(&rows), 0);
    }

    #[test]
    fn repeated_task_records_exact_epoch_chain() {
        let result = d_play_task(task());
        assert!(result.manifest.eligible);
        assert!(result.one_shot.is_some());
        assert!(result.repeated.is_some());
        assert!(result.selected_noncontrol_epochs <= D35D_MAX_NONCONTROL_EPOCHS);
        assert_eq!(result.selection_mismatches, 0);
        assert_eq!(result.replay_mismatches, 0);
        assert_eq!(result.strict_advance_failures, 0);
        assert_eq!(result.execution_prefix_mismatches, 0);
        assert_eq!(result.repeated.as_ref().unwrap().attribution_failures, 0);
        assert_eq!(result.repeated.as_ref().unwrap().history_mismatch, 0);

        let mut by_epoch: BTreeMap<usize, Vec<&DEpochOption>> = BTreeMap::new();
        for row in &result.options {
            by_epoch.entry(row.epoch).or_default().push(row);
        }
        let mut prior_end = None;
        for (epoch, rows) in by_epoch {
            assert_eq!(rows.iter().filter(|row| row.selected).count(), 1);
            let expected = rows
                .iter()
                .min_by(|left, right| d_option_order(left).cmp(&d_option_order(right)))
                .unwrap();
            let selected = rows.iter().find(|row| row.selected).unwrap();
            assert_eq!(selected.option, expected.option);
            assert!(selected.execution_prefix_match);
            assert!(selected.selected_rollout_replay_match);
            if let Some(end) = prior_end {
                assert_eq!(selected.epoch_turn, end);
            }
            prior_end = (selected.option > 0).then_some(selected.executed_end_turn);
            assert!(epoch < D35D_MAX_NONCONTROL_EPOCHS + 1);
        }
    }
}

#[path = "d36_resident_anchored_constrained_joint_oracle_impl.rs"]
mod d36_extension;
pub(crate) use d36_extension::d36_main;
