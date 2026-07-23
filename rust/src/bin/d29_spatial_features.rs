mod base {
    #![allow(dead_code)]

    include!("d26_policy_pulse.rs");

    const GRID_WIDTH: i32 = 22;
    const GRID_HEIGHT: i32 = 11;
    const CHANNELS: usize = 36;
    const CELLS: usize = GRID_WIDTH as usize * GRID_HEIGHT as usize;

    fn canonical_cell(cell: (i32, i32), width: i32, height: i32, rotate: bool) -> (i32, i32) {
        if rotate {
            (width - 1 - cell.0, height - 1 - cell.1)
        } else {
            cell
        }
    }

    fn plane_index(channel: usize, cell: (i32, i32)) -> usize {
        assert!((0..GRID_WIDTH).contains(&cell.0));
        assert!((0..GRID_HEIGHT).contains(&cell.1));
        channel * CELLS + cell.1 as usize * GRID_WIDTH as usize + cell.0 as usize
    }

    fn add(grid: &mut [i16], channel: usize, cell: (i32, i32), value: i32) {
        let index = plane_index(channel, cell);
        grid[index] = grid[index]
            .checked_add(i16::try_from(value).expect("D29 plane value fits i16"))
            .expect("D29 plane sum fits i16");
    }

    fn plant_channel(kind: &str) -> usize {
        match kind {
            "PLUM" => 6,
            "LEMON" => 7,
            "APPLE" => 8,
            "BANANA" => 9,
            _ => panic!("unknown D29 plant kind: {kind}"),
        }
    }

    fn spatial_planes(game: &GameState, seat: usize) -> (bool, Vec<i16>) {
        assert!(game.width <= GRID_WIDTH && game.height <= GRID_HEIGHT);
        let opponent = 1 - seat;
        let rotate = game.shacks[seat] > game.shacks[opponent];
        let cell = |value| canonical_cell(value, game.width, game.height, rotate);
        let mut grid = vec![0i16; CHANNELS * CELLS];

        for y in 0..game.height {
            for x in 0..game.width {
                add(&mut grid, 0, (x, y), 1);
            }
        }
        for &value in &game.walkable {
            add(&mut grid, 1, cell(value), 1);
        }
        for &value in &game.water {
            add(&mut grid, 2, cell(value), 1);
        }
        for &value in &game.iron {
            add(&mut grid, 3, cell(value), 1);
        }
        add(&mut grid, 4, cell(game.shacks[seat]), 1);
        add(&mut grid, 5, cell(game.shacks[opponent]), 1);

        for plant in &game.plants {
            let target = cell(plant.pos());
            add(&mut grid, plant_channel(&plant.plant_type), target, 1);
            add(&mut grid, 10, target, plant.size);
            add(&mut grid, 11, target, plant.health);
            add(&mut grid, 12, target, plant.fruits);
            add(&mut grid, 13, target, plant.cooldown);
        }
        for unit in &game.units {
            let ours = unit.player as usize == seat;
            let base = if ours { 14 } else { 25 };
            let target = cell(unit.pos());
            add(&mut grid, base, target, 1);
            add(&mut grid, base + 1, target, unit.ms);
            add(&mut grid, base + 2, target, unit.cc);
            add(&mut grid, base + 3, target, unit.hp);
            add(&mut grid, base + 4, target, unit.chop);
            for (item, value) in unit.carry.iter().enumerate() {
                add(&mut grid, base + 5 + item, target, *value);
            }
        }
        (rotate, grid)
    }

    fn grid_hash(grid: &[i16]) -> u64 {
        let mut hash = FNV_OFFSET;
        for value in grid {
            for byte in value.to_le_bytes() {
                hash ^= u64::from(byte);
                hash = hash.wrapping_mul(FNV_PRIME);
            }
        }
        hash
    }

    #[derive(Clone)]
    struct SpatialRow {
        task: Task,
        reached_cut: bool,
        root: GameState,
        rotate: bool,
        grid: Vec<i16>,
    }

    fn spatial_row(task: Task) -> SpatialRow {
        let prefix = resident_prefix(task.seed, task.seat, task.opponent_index);
        let (rotate, grid) = spatial_planes(&prefix.root, task.seat);
        SpatialRow {
            task,
            reached_cut: prefix.reached_cut,
            root: prefix.root,
            rotate,
            grid,
        }
    }

    pub fn run_d29_exporter() {
        let args: Vec<String> = std::env::args().collect();
        let seed_start = args
            .get(1)
            .map_or(0, |value| value.parse::<u64>().expect("numeric seed start"));
        let seed_count = args.get(2).map_or(5, |value| {
            value.parse::<usize>().expect("numeric seed count")
        });
        let output = args
            .get(3)
            .cloned()
            .unwrap_or_else(|| "d29-spatial-features.tsv".to_string());
        let threads = args
            .get(4)
            .map_or(16, |value| {
                value.parse::<usize>().expect("numeric thread count")
            })
            .clamp(1, 64);
        assert!(seed_count > 0, "seed count must be positive");

        let tasks: Vec<_> = (seed_start..seed_start + seed_count as u64)
            .flat_map(|seed| {
                (0..2).flat_map(move |seat| {
                    (0..OPPONENTS.len()).map(move |opponent_index| Task {
                        seed,
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
                    let mut rows = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        rows.push(spatial_row(tasks[index]));
                    }
                    rows
                })
            })
            .collect();
        let mut rows: Vec<_> = handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("D29 worker"))
            .collect();
        rows.sort_by_key(|row| (row.task.seed, row.task.seat, row.task.opponent_index));

        let mut writer = BufWriter::new(File::create(&output).expect("create D29 output"));
        writeln!(
            writer,
            "seed\tseat\topponent\treached_cut\trotated\twidth\theight\troot_turn\troot_my_score\troot_opponent_score\troot_my_wood\troot_opponent_wood\troot_my_workers\troot_opponent_workers\troot_plants\tgrid_channels\tgrid_height\tgrid_width\tgrid_len\tgrid_hash\tgrid"
        )
        .expect("write D29 header");
        for row in &rows {
            let task = row.task;
            let encoded = row
                .grid
                .iter()
                .map(i16::to_string)
                .collect::<Vec<_>>()
                .join(",");
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                task.seed,
                task.seat,
                OPPONENTS[task.opponent_index].0,
                usize::from(row.reached_cut),
                usize::from(row.rotate),
                row.root.width,
                row.root.height,
                row.root.turn,
                row.root.scores[task.seat],
                row.root.scores[1 - task.seat],
                row.root.inventories[task.seat][5],
                row.root.inventories[1 - task.seat][5],
                worker_count(&row.root, task.seat),
                worker_count(&row.root, 1 - task.seat),
                row.root.plants.len(),
                CHANNELS,
                GRID_HEIGHT,
                GRID_WIDTH,
                row.grid.len(),
                grid_hash(&row.grid),
                encoded,
            )
            .expect("write D29 row");
        }
        writer.flush().expect("flush D29 output");
        eprintln!(
            "saved {} rows with {} plane values each in {:.3}s to {output}",
            rows.len(),
            CHANNELS * CELLS,
            started.elapsed().as_secs_f64(),
        );
    }

    #[cfg(test)]
    mod d29_tests {
        use super::*;

        #[test]
        fn plane_shape_is_fixed() {
            let game = generate_bronze(0);
            let (_, planes) = spatial_planes(&game, 0);
            assert_eq!(planes.len(), 36 * 11 * 22);
        }

        #[test]
        fn own_shack_is_canonical() {
            let game = generate_bronze(3);
            for seat in 0..2 {
                let rotate = game.shacks[seat] > game.shacks[1 - seat];
                let ours = canonical_cell(game.shacks[seat], game.width, game.height, rotate);
                let theirs = canonical_cell(game.shacks[1 - seat], game.width, game.height, rotate);
                assert!(ours < theirs);
            }
        }

        #[test]
        fn spatial_hash_is_repeatable() {
            let game = generate_bronze(9);
            let first = spatial_planes(&game, 0).1;
            let second = spatial_planes(&game, 0).1;
            assert_eq!(first, second);
            assert_eq!(grid_hash(&first), grid_hash(&second));
        }
    }
}

pub use base::{bot, game};

fn main() {
    base::run_d29_exporter();
}
