//! Compact initial-map features for already-consumed half-size development seeds.

use troll_farm::game::a2_referee_parity;
use troll_farm::game::engine::bfs_distances;
use troll_farm::game::state::Cell;

fn neighbors((x, y): Cell) -> [Cell; 4] {
    [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
}

fn main() {
    let mut arguments = std::env::args().skip(1);
    let start = arguments.next().and_then(|value| value.parse().ok()).unwrap_or(9_854_000);
    let maps = arguments.next().and_then(|value| value.parse().ok()).unwrap_or(43);
    println!("seed\tseat\tdoors\ttrees\tfruit\tbank_plum\tbank_lemon\tbank_apple\tbank_banana\tbank_iron\tbank_wood\tplum\tlemon\tapple\tbanana\tnearest_tree\tnearest_enemy_tree\tmedian_home\tdoor_tree\twater_mothers\tbest_mother_enemy\torchard_active");
    for seed in start..start + maps {
        let game = a2_referee_parity::generate_official(seed).game;
        for seat in 0..2 {
            let doors: Vec<Cell> = neighbors(game.shacks[seat])
                .into_iter()
                .filter(|cell| game.walkable.contains(cell))
                .collect();
            let enemy_doors: Vec<Cell> = neighbors(game.shacks[1 - seat])
                .into_iter()
                .filter(|cell| game.walkable.contains(cell))
                .collect();
            let distance = bfs_distances(&game.walkable, &doors);
            let enemy_distance = bfs_distances(&game.walkable, &enemy_doors);
            let nearest_tree = game
                .plants
                .iter()
                .filter_map(|plant| distance.get(&plant.pos()).copied())
                .min()
                .unwrap_or(10_000);
            let nearest_enemy_tree = game
                .plants
                .iter()
                .filter_map(|plant| enemy_distance.get(&plant.pos()).copied())
                .min()
                .unwrap_or(10_000);
            let mut home_distances: Vec<i32> = game
                .plants
                .iter()
                .filter_map(|plant| distance.get(&plant.pos()).copied())
                .collect();
            home_distances.sort_unstable();
            let median_home = if home_distances.len() % 2 == 0 {
                (home_distances[home_distances.len() / 2 - 1]
                    + home_distances[home_distances.len() / 2]) as f64
                    / 2.0
            } else {
                home_distances[home_distances.len() / 2] as f64
            };
            let water_mothers: Vec<Cell> = doors
                .iter()
                .copied()
                .filter(|door| !game.plants.iter().any(|plant| plant.pos() == *door))
                .filter(|door| game.water.iter().any(|water| neighbors(*water).contains(door)))
                .filter(|door| enemy_distance.get(door).copied().unwrap_or(10_000) >= 11)
                .collect();
            let door_tree = game.plants.iter().any(|plant| doors.contains(&plant.pos()));
            let best_mother_enemy = water_mothers
                .iter()
                .filter_map(|door| enemy_distance.get(door).copied())
                .max()
                .unwrap_or(-1);
            let count = |kind: &str| {
                game.plants
                    .iter()
                    .filter(|plant| plant.plant_type == kind)
                    .count()
            };
            println!(
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.1}\t{}\t{}\t{}\t{}",
                seed,
                seat,
                doors.len(),
                game.plants.len(),
                game.plants.iter().map(|plant| plant.fruits).sum::<i32>(),
                game.inventories[seat][0],
                game.inventories[seat][1],
                game.inventories[seat][2],
                game.inventories[seat][3],
                game.inventories[seat][4],
                game.inventories[seat][5],
                count("PLUM"),
                count("LEMON"),
                count("APPLE"),
                count("BANANA"),
                nearest_tree,
                nearest_enemy_tree,
                median_home,
                usize::from(door_tree),
                water_mothers.len(),
                best_mother_enemy,
                usize::from(doors.len() >= 2 && !door_tree && !water_mothers.is_empty()),
            );
        }
    }
}
