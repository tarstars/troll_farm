struct MoisanBot;
impl MoisanBot {
            fn move_command(command: &str) -> Option<(i32, Cell)> {
                let fields: Vec<&str> = command.split_whitespace().collect();
                if fields.len() != 4 || !fields[0].eq_ignore_ascii_case("MOVE") {
                    return None;
                }
                Some((
                    fields[1].parse().ok()?,
                    (fields[2].parse().ok()?, fields[3].parse().ok()?),
                ))
            }
            fn resolve_move_conflicts(view: &GameState, commands: &mut [String]) {
                Self::resolve_move_conflicts_with_priority(view, commands, &BTreeSet::new());
            }
            fn resolve_move_conflicts_with_priority(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
            ) {
                Self::resolve_move_conflicts_with_priority_and_forbidden(
                    view,
                    commands,
                    priority_ids,
                    &BTreeSet::new(),
                );
            }
            fn resolve_move_conflicts_with_priority_and_forbidden(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
            ) {
                Self::resolve_move_conflicts_with_egress(
                    view,
                    commands,
                    priority_ids,
                    forbidden_for_non_priority,
                    None,
                );
            }
            // The optional egress unit is served before every other mover: its landing
            // cell is what frees the shack for a same-turn purchase.
            fn resolve_move_conflicts_with_egress(
                view: &GameState,
                commands: &mut [String],
                priority_ids: &BTreeSet<i32>,
                forbidden_for_non_priority: &BTreeSet<Cell>,
                egress: Option<i32>,
            ) {
                let command_by_id: BTreeMap<i32, usize> = commands
                    .iter()
                    .enumerate()
                    .filter_map(|(index, command)| {
                        Self::move_command(command).map(|(id, _)| (id, index))
                    })
                    .collect();
                let projections: Vec<(i32, usize, Cell, Cell, Cell)> = command_by_id
                    .iter()
                    .filter_map(|(id, index)| {
                        let unit = view.unit(*id)?;
                        let (_, target) = Self::move_command(&commands[*index])?;
                        let landing =
                            next_cell(&view.walkable, unit.cell, target, unit.stats.movement_speed);
                        Some((*id, *index, unit.cell, target, landing))
                    })
                    .collect();
                let moving_ids: BTreeSet<i32> = projections
                    .iter()
                    .filter(|(_, _, current, _, landing)| landing != current)
                    .map(|(id, _, _, _, _)| *id)
                    .collect();
                let occupied_now: BTreeSet<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .map(|unit| unit.cell)
                    .collect();
                let mut reserved: BTreeSet<Cell> = view
                    .units
                    .iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                for (_, index, current, _, landing) in &projections {
                    if landing == current {
                        commands[*index] = "WAIT".to_string();
                    }
                }
                let mut movers: Vec<(i32, usize, Cell, Cell)> = projections
                    .into_iter()
                    .filter(|(_, _, current, _, landing)| landing != current)
                    .map(|(id, index, _, target, landing)| (id, index, target, landing))
                    .collect();
                movers.sort_by(|a, b| {
                    let rank = |id: i32| (egress == Some(id), priority_ids.contains(&id));
                    rank(b.0).cmp(&rank(a.0)).then_with(|| b.0.cmp(&a.0))
                });
                for (id, index, target, landing) in movers {
                    let Some(unit) = view.unit(id) else { continue };
                    let landing_forbidden = !priority_ids.contains(&id)
                        && forbidden_for_non_priority.contains(&landing);
                    if !landing_forbidden && !reserved.contains(&landing) {
                        reserved.insert(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                        continue;
                    }
                    let toward_goal = bfs_distances(&view.walkable, &[target]);
                    let detour = ortho_neighbors(unit.cell)
                        .into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| !reserved.contains(cell))
                        .filter(|cell| !occupied_now.contains(cell))
                        .filter(|cell| {
                            priority_ids.contains(&id) || !forbidden_for_non_priority.contains(cell)
                        })
                        .min_by_key(|cell| {
                            (
                                toward_goal
                                    .get(cell)
                                    .copied()
                                    .unwrap_or_else(|| manhattan(*cell, target)),
                                *cell,
                            )
                        });
                    commands[index] = if let Some(cell) = detour {
                        reserved.insert(cell);
                        format!("MOVE {} {} {}", id, cell.0, cell.1)
                    } else {
                        "WAIT".to_string()
                    };
                }
            }
        }
