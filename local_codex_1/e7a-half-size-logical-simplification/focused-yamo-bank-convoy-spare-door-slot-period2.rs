mod game{pub mod types{use std::collections::BTreeSet;pub type Cell=(i32,i32);pub const PLUM:usize=0;pub const LEMON:usize=1;pub const APPLE:usize=2;pub const BANANA:usize=3;pub const IRON:usize=4;pub const WOOD:usize=5;pub type Stock=[i32;6];#[derive(Clone,Copy,PartialEq)]pub enum PlantKind{Plum,Lemon,Apple,Banana,}impl PlantKind{pub fn parse(value:&str)->Option<PlantKind>{match value{"PLUM"=>Some(PlantKind::Plum),"LEMON"=>Some(PlantKind::Lemon),"APPLE"=>Some(PlantKind::Apple),"BANANA"=>Some(PlantKind::Banana),_=>None}}pub fn as_str(self)->&'static str{match self{PlantKind::Plum=>"PLUM",PlantKind::Lemon=>"LEMON",PlantKind::Apple=>"APPLE",PlantKind::Banana=>"BANANA",}}}#[derive(Clone,Copy)]pub struct Stats{pub movement_speed:i32,pub carry_capacity:i32,pub chop_power:i32,}pub struct Unit{pub id:i32,pub player:usize,pub cell:Cell,pub stats:Stats,pub carry:Stock,}impl Unit{pub fn total_carried(&self)->i32{self.carry.iter().sum()}pub fn free_capacity(&self)->i32{self.stats.carry_capacity-self.total_carried()}}pub struct Plant{pub kind:PlantKind,pub cell:Cell,pub size:i32,pub health:i32,pub fruits:i32,pub cooldown:i32,}pub struct GameState{pub walkable:BTreeSet<Cell>,pub shacks:[Cell;2],pub inventories:[Stock;2],pub units:Vec<Unit>,pub plants:Vec<Plant>,pub turn:i32,pub iron:BTreeSet<Cell>,pub water:BTreeSet<Cell>,}impl GameState{pub fn plant_at(&self,cell:Cell)->Option<usize>{self.plants.iter().position(|plant|plant.cell==cell)}}}pub mod rules{use super::types::{PlantKind};pub const TOTAL_TURNS:i32=300;pub fn tree_health(kind: PlantKind, size: i32) -> i32 {
            match kind {
                PlantKind::Plum | PlantKind::Lemon => 4 + 2 * size,
                PlantKind::Apple => 8 + 3 * size,
                PlantKind::Banana => 2 + size,
            }
        }}pub mod nav{use super::types::Cell;use std::collections::{BTreeMap,BTreeSet,VecDeque};pub const NEIGHBORS:[Cell;4]=[(0,1),(1,0),(0,-1),(-1,0)];pub fn manhattan(a:Cell,b:Cell)->i32{(a.0-b.0).abs()+(a.1-b.1).abs()}pub fn ortho_neighbors(cell:Cell)->[Cell;4]{[(cell.0,cell.1+1),(cell.0+1,cell.1),(cell.0,cell.1-1),(cell.0-1,cell.1),]}pub fn is_adjacent(a:Cell,b:Cell)->bool{manhattan(a,b)==1}pub fn bfs_distances(walkable:&BTreeSet<Cell>,sources:&[Cell])->BTreeMap<Cell,i32>{let mut dist=BTreeMap::new();let mut queue=VecDeque::new();for&cell in sources{if dist.insert(cell,0).is_none(){queue.push_back(cell);}}while let Some(cell)=queue.pop_front(){let d=dist[&cell];for delta in NEIGHBORS{let next=(cell.0+delta.0,cell.1+delta.1);if walkable.contains(&next)&&!dist.contains_key(&next){dist.insert(next,d+1);queue.push_back(next);}}}dist}pub fn next_cell(
                walkable: &BTreeSet<Cell>,
                current: Cell,
                target: Cell,
                speed: i32,
            ) -> Cell {
                let from_current = bfs_distances(walkable, &[current]);
                let to_target = bfs_distances(walkable, &[target]);
                from_current.iter()
                    .filter(|(cell, distance)| {
                        **distance <= speed && to_target.contains_key(*cell)
                    })
                    .map(|(cell, _)| *cell)
                    .min_by_key(|cell| (to_target[cell], *cell))
                    .unwrap_or(current)
            }}pub mod protocol{use super::types::{Cell,GameState,Plant,PlantKind,Stats,Unit};use std::collections::BTreeSet;use std::io::BufRead;pub struct StaticMap{pub walkable:BTreeSet<Cell>,pub shacks:[Cell;2],pub iron:BTreeSet<Cell>,pub water:BTreeSet<Cell>,}pub fn read_line(reader:&mut impl BufRead)->Option<String>{let mut line=String::new();match reader.read_line(&mut line){Ok(0)=>None,Ok(_)=>Some(line.trim_end_matches('\n').trim_end_matches('\r').to_string(),),Err(_)=>None,}}pub fn read_static_map(reader:&mut impl BufRead)->Option<StaticMap>{let header=read_line(reader)?;let mut parts=header.split_whitespace();let _width:i32=parts.next()?.parse().ok()?;let height=parts.next()?.parse().ok()?;let mut rows=Vec::new();for _ in 0..height{rows.push(read_line(reader)?);}Some(parse_static_map(&rows))}pub fn parse_static_map(rows:&[String])->StaticMap{let mut walkable=BTreeSet::new();let mut shacks=[(0,0),(0,0)];let mut iron=BTreeSet::new();let mut water=BTreeSet::new();for(y,row)in rows.iter().enumerate(){for(x,ch)in row.chars().enumerate(){let cell=(x as i32,y as i32);match ch{'0'=>shacks[0]=cell,'1'=>shacks[1]=cell,'.'=>{walkable.insert(cell);}'+'=>{iron.insert(cell);}'~'=>{water.insert(cell);}_=>{}}}}StaticMap{walkable,shacks,iron,water,}}pub fn read_turn(reader:&mut impl BufRead,map:&StaticMap,turn:i32)->Option<GameState>{let mut inventories=[[0;6];2];for inv in&mut inventories{let line=read_line(reader)?;let values:Vec<i32> =line.split_whitespace().map(|value|value.parse().ok()).collect::<Option<Vec<i32>>>()?;if values.len()!=6{return None;}inv.copy_from_slice(&values);}let tree_count:usize=read_line(reader)?.trim().parse().ok()?;let mut plants=Vec::with_capacity(tree_count);for _ in 0..tree_count{let line=read_line(reader)?;let fields:Vec<&str> =line.split_whitespace().collect();if fields.len()!=7{return None;}plants.push(Plant{kind:PlantKind::parse(fields[0])?,cell:(fields[1].parse().ok()?,fields[2].parse().ok()?),size:fields[3].parse().ok()?,health:fields[4].parse().ok()?,fruits:fields[5].parse().ok()?,cooldown:fields[6].parse().ok()?,});}let unit_count:usize=read_line(reader)?.trim().parse().ok()?;let mut units=Vec::with_capacity(unit_count);for _ in 0..unit_count{let line=read_line(reader)?;let values:Vec<i32> =line.split_whitespace().map(|value|value.parse().ok()).collect::<Option<Vec<i32>>>()?;if values.len()!=14{return None;}units.push(Unit{id:values[0],player:values[1]as usize,cell:(values[2],values[3]),stats:Stats{movement_speed:values[4],carry_capacity:values[5],chop_power:values[7],},carry:[values[8],values[9],values[10],values[11],values[12],values[13],],});}Some(GameState{walkable:map.walkable.clone(),shacks:map.shacks,inventories,units,plants,turn,iron:map.iron.clone(),water:map.water.clone(),})}}pub use types::GameState;}mod bot{pub mod moisan{use super::Bot;use crate::game::nav::{bfs_distances,is_adjacent,manhattan,next_cell,ortho_neighbors};use crate::game::rules::{tree_health,TOTAL_TURNS,};use crate::game::types::{Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,WOOD,};use std::collections::BTreeMap;type Target=Option<Cell>;struct Candidate{command:String,score:f64,target:Target,}struct MoisanBot;pub struct YamoBot {
            type_to_cut: Option<PlantKind>,
            desired_second: Option<Stats>,
            orchard_mother: Option<Cell>,
            move_history: [(i32, Cell, Cell); 2],
        }impl MoisanBot{fn focus_type(view: &GameState) -> PlantKind {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let sum = |kind| view.plants.iter()
                    .filter(|plant| plant.kind == kind)
                    .map(|plant| distance.get(&plant.cell).copied().unwrap_or(10_000))
                    .sum::<i32>();
                if sum(PlantKind::Plum) - sum(PlantKind::Lemon) <= 8 {
                    PlantKind::Plum
                } else {
                    PlantKind::Lemon
                }
            }fn ceil_div(a:i32,b:i32)->i32{if b<=0{10_000}else{(a+b-1)/b}}fn bank_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{let dist=bfs_distances(&view.walkable,&[unit.cell]);let mut out:Vec<Candidate> =ortho_neighbors(view.shacks[0]).into_iter().filter(|cell|view.walkable.contains(cell)&&dist.contains_key(cell)).map(|cell|{let at_drop=unit.cell==cell;Candidate{command:if at_drop{format!("DROP {}",unit.id)}else{format!("MOVE {} {} {}",unit.id,cell.0,cell.1)},score:if at_drop{8_000.0}else{7_000.0-dist[&cell]as f64},target:Some(cell),}}).collect();out.push(Self::wait());out}fn can_train(view: &GameState, stats: Stats) -> bool {
                if view.units.iter().filter(|unit| unit.player == 0).count() >= 2
                    || TOTAL_TURNS - view.turn <= 20
                {
                    return false;
                }
                let inventory = &view.inventories[0];
                inventory[PLUM] >= 1 + stats.movement_speed * stats.movement_speed
                    && inventory[LEMON] >= 1 + stats.carry_capacity * stats.carry_capacity
                    && (view.iron.is_empty()
                        || inventory[IRON] >= 1 + stats.chop_power * stats.chop_power)
            }fn ticks_until_fruit(view: &GameState, plant: &Plant) -> i32 {
                if plant.fruits > 0 {
                    return 0;
                }
                let near_water = view.water.iter().any(|water| {
                    is_adjacent(*water, plant.cell)
                });
                let reset = match plant.kind {
                    PlantKind::Plum | PlantKind::Lemon => if near_water { 3 } else { 8 },
                    PlantKind::Apple => if near_water { 2 } else { 9 },
                    PlantKind::Banana => if near_water { 4 } else { 6 },
                };
                plant.cooldown.max(1)
                    + reset * (4 - plant.size).max(0)
            }fn early_candidates(
                view: &GameState,
                unit: &Unit,
                desired: Stats,
            ) -> Vec<Candidate> {
                let mut out = vec![Self::wait()];
                if unit.total_carried() > 0 || unit.free_capacity() <= 0 {
                    out.extend(Self::bank_candidates(view, unit));
                    return out;
                }
                let needs = [
                    (PLUM, 1 + desired.movement_speed * desired.movement_speed),
                    (LEMON, 1 + desired.carry_capacity * desired.carry_capacity),
                    (IRON, 1 + desired.chop_power * desired.chop_power),
                ];
                for (item, required) in needs {
                    if required <= view.inventories[0][item] {
                        continue;
                    }
                    if item == IRON {
                        out.extend(Self::iron_candidates(view, unit, 6_100.0));
                    } else {
                        let kind = if item == PLUM {
                            PlantKind::Plum
                        } else {
                            PlantKind::Lemon
                        };
                        out.extend(Self::fruit_candidates(view, unit, kind, 6_000.0));
                    }
                }
                if out.len() == 1 {
                    out.extend(Self::chop_candidates(view, unit, None));
                }
                out
            }fn fruit_candidates(view:&GameState,unit:&Unit,kind:PlantKind,base_score:f64,)->Vec<Candidate>{let mut out=Vec::new();if view.plants.iter().any(|plant|plant.cell==unit.cell&&plant.kind==kind&&plant.fruits>0){out.push(Candidate{command:format!("HARVEST {}",unit.id),score:base_score+900.0,target:Some(unit.cell),});}let dist=bfs_distances(&view.walkable,&[unit.cell]);for plant in&view.plants{if plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell){continue;}let travel=Self::ceil_div(dist[&plant.cell],unit.stats.movement_speed);let wait=(Self::ticks_until_fruit(view,plant)-travel).max(0);out.push(Candidate{command:format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1),score:base_score-(travel+wait)as f64,target:Some(plant.cell),});}out}fn iron_candidates(view:&GameState,unit:&Unit,base_score:f64)->Vec<Candidate>{let mut out=Vec::new();if view.iron.iter().any(|iron|is_adjacent(*iron,unit.cell)){out.push(Candidate{command:format!("MINE {}",unit.id),score:base_score+900.0,target:Some(unit.cell),});}let dist=bfs_distances(&view.walkable,&[unit.cell]);for iron in&view.iron{for cell in ortho_neighbors(*iron){if!view.walkable.contains(&cell){continue;}if let Some(d)=dist.get(&cell){out.push(Candidate{command:format!("MOVE {} {} {}",unit.id,cell.0,cell.1),score:base_score-*d as f64,target:Some(cell),});}}}out}fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>{let mut out=Vec::new();if unit.stats.chop_power<=0||unit.free_capacity()<=0{return out;}let from_unit=bfs_distances(&view.walkable,&[unit.cell]);let shack_starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).iter().filter(|cell|view.walkable.contains(cell)).copied().collect();let to_shack=bfs_distances(&view.walkable,&shack_starts);let opponent_trolls=view.units.iter().filter(|unit|unit.player==1).count();for plant in&view.plants{if plant.health<=0||!from_unit.contains_key(&plant.cell){continue;}let travel_turns=Self::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);let chop_turns=Self::ceil_div(plant.health,unit.stats.chop_power);let return_turns=Self::ceil_div(to_shack[&plant.cell],unit.stats.movement_speed);let turns=travel_turns+chop_turns+return_turns+1;if turns>TOTAL_TURNS-view.turn+1{continue;}let wood=plant.size.min(unit.free_capacity());let mut score=1000.0*wood as f64/turns as f64;if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{let opponent_distance=manhattan(plant.cell,view.shacks[1]);score+=900.0/(1+opponent_distance)as f64;}let command=if plant.cell==unit.cell{format!("CHOP {}",unit.id)}else{format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1)};out.push(Candidate{command,score,target:Some(plant.cell),});}out}fn wait()->Candidate{Candidate{command:"WAIT".to_string(),score:0.0,target:None,}}fn compatible(a:Target,b:Target)->bool{a.is_none()||b.is_none()||a!=b}fn picked_item(command:&str)->Option<usize>{let item=command.strip_prefix("PICK ")?.split_whitespace().nth(1)?;match item{"PLUM"=>Some(PLUM),"LEMON"=>Some(LEMON),"APPLE"=>Some(APPLE),"BANANA"=>Some(BANANA),"IRON"=>Some(IRON),"WOOD"=>Some(WOOD),_=>None}}fn stock_compatible(a:&Candidate,b:&Candidate,inventory:&[i32;6])->bool{match(Self::picked_item(&a.command),Self::picked_item(&b.command)){(Some(a),Some(b))if a==b=>inventory[a]>=2,_=>true,}}fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;6],)->Vec<String>{let ids:Vec<i32> =candidates_by_id.keys().copied().collect();if ids.is_empty(){return Vec::new();}if ids.len()==1{let best=candidates_by_id[&ids[0]].iter().max_by(|a,b|a.score.total_cmp(&b.score)).unwrap();return vec![best.command.clone()];}if ids.len()==2{let mut best_score=f64::NEG_INFINITY;let mut best_pair=None;for a in&candidates_by_id[&ids[0]]{for b in&candidates_by_id[&ids[1]]{if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){continue;}let score=a.score+b.score;if score>best_score{best_score=score;best_pair=Some((a.command.clone(),b.command.clone()));}}}if let Some((a,b))=best_pair{return vec![a,b];}}vec!["WAIT".to_string();2]}fn move_command(command:&str)->Option<(i32,Cell)>{let fields:Vec<&str> =command.split_whitespace().collect();if fields.len()!=4||!fields[0].eq_ignore_ascii_case("MOVE"){return None;}Some((fields[1].parse().ok()?,(fields[2].parse().ok()?,fields[3].parse().ok()?),))}fn resolve_move_conflicts(view: &GameState, commands: &mut [String], move_history: &mut [(i32, Cell, Cell); 2]) {
                let mut moves: Vec<(i32, usize, Cell, Cell)> = commands.iter()
                    .enumerate()
                    .filter_map(|(index, command)| {
                        let (id, target) = Self::move_command(command)?;
                        let unit = view.units.iter().find(|unit| unit.id == id)?;
                        Some((id, index, unit.cell, next_cell(
                            &view.walkable, unit.cell, target, unit.stats.movement_speed,
                        )))
                    })
                    .collect();
                moves.retain(|(_, index, _, landing)| {
                    let (turn, two_back, previous) = move_history[*index];
                    if turn + 1 == view.turn
                        && two_back == *landing && previous != *landing
                    {
                        commands[*index] = "WAIT".to_string();
                        move_history[*index] = (view.turn, *landing, *landing);
                        false
                    } else {
                        move_history[*index] = (
                            view.turn,
                            if turn + 1 == view.turn { previous } else { *landing },
                            *landing,
                        );
                        true
                    }
                });
                let moving_ids: Vec<i32> = moves.iter()
                    .filter(|(_, _, current, landing)| current != landing)
                    .map(|(id, _, _, _)| *id)
                    .collect();
                let mut reserved: Vec<Cell> = view.units.iter()
                    .filter(|unit| unit.player == 0 && !moving_ids.contains(&unit.id))
                    .map(|unit| unit.cell)
                    .collect();
                moves.sort_by(|a, b| b.0.cmp(&a.0));
                for (id, index, current, landing) in moves {
                    if landing == current || reserved.contains(&landing) {
                        commands[index] = "WAIT".to_string();
                    } else {
                        reserved.push(landing);
                        commands[index] = format!("MOVE {} {} {}", id, landing.0, landing.1);
                    }
                }
            }}impl YamoBot {
            pub fn new() -> Self {
                Self { type_to_cut: None, desired_second: None, orchard_mother: None, move_history: [(0, (0, 0), (0, 0)); 2] }
            }

            fn ensure_opening(&mut self, view: &GameState) {
                if view.turn == 1 {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                    self.desired_second = Some(Self::choose_second_troll(view));
                    self.orchard_mother = Self::select_orchard_mother(view);
                }
            }

            fn choose_second_troll(view: &GameState) -> Stats {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &doors);
                let collection_eta = |level: i32, item: usize, kind: Option<PlantKind>| {
                    let missing = (1 + level * level - view.inventories[0][item]).max(0);
                    if missing == 0 {
                        return 0;
                    }
                    if let Some(kind) = kind {
                        return view.plants.iter()
                            .filter(|plant| plant.kind == kind && plant.health > 0)
                            .filter_map(|plant| {
                                let travel = distance.get(&plant.cell).copied()?;
                                let wait = (MoisanBot::ticks_until_fruit(view, plant) - travel)
                                    .max(0);
                                Some(missing * (2 * travel + 2) + wait)
                            })
                            .min()
                            .unwrap_or(10_000);
                    }
                    view.iron.iter()
                        .flat_map(|iron| ortho_neighbors(*iron))
                        .filter_map(|cell| distance.get(&cell).copied())
                        .min()
                        .map_or(10_000, |travel| missing * (2 * travel + 2))
                };
                let mut options = Vec::new();
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                
                                chop_power,
                            };
                            let eta = collection_eta(
                                movement_speed, PLUM, Some(PlantKind::Plum),
                            ) + collection_eta(
                                carry_capacity, LEMON, Some(PlantKind::Lemon),
                            ) + if view.iron.is_empty() {
                                0
                            } else {
                                collection_eta(chop_power, IRON, None)
                            };
                            options.push((stats, eta));
                        }
                    }
                }
                let key = |(stats, eta): &(Stats, i32)| {
                    (stats.movement_speed + stats.carry_capacity + stats.chop_power,
                        -*eta, stats.chop_power, stats.carry_capacity, stats.movement_speed)
                };
                let baseline = options.iter()
                    .filter(|(_, eta)| *eta <= 15)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(options[0]);
                if baseline.0.carry_capacity >= 2 {
                    return baseline.0;
                }
                let allowed_eta = (baseline.1 + 15).min(34);
                options.iter()
                    .filter(|(stats, eta)| stats.carry_capacity >= 2 && *eta <= allowed_eta)
                    .max_by_key(|option| key(option))
                    .copied()
                    .unwrap_or(baseline)
                    .0
            }

            fn select_orchard_mother(view: &GameState) -> Option<Cell> {
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0]).into_iter()
                    .filter(|cell| view.walkable.contains(cell)).collect();
                if doors.len() < 2 || doors.len() == 2
                    && view.plants.iter().any(|plant| doors.contains(&plant.cell))
                {
                    return None;
                }
                let enemy_distance = bfs_distances(
                    &view.walkable,
                    &ortho_neighbors(view.shacks[1]).into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .collect::<Vec<Cell>>(),
                );
                doors.into_iter()
                    .filter(|door| view.plant_at(*door).is_none())
                    .filter(|door| view.water.iter()
                        .any(|water| is_adjacent(*water, *door)))
                    .filter(|door| enemy_distance[door] >= 11)
                    .min_by_key(|door| (-enemy_distance[door], *door))
            }

            fn orchard_command(&self, view: &GameState) -> String {
                let mother = self.orchard_mother.unwrap();
                let starter = view.units.iter()
                    .filter(|unit| unit.player == 0)
                    .min_by_key(|unit| unit.id).unwrap();
                if starter.cell != mother {
                    return format!("MOVE {} {} {}", starter.id, mother.0, mother.1);
                }
                if let Some(tree) = view.plant_at(mother)
                    .map(|index| &view.plants[index])
                    .filter(|plant| plant.kind == PlantKind::Apple)
                {
                    return if starter.total_carried() > 0 {
                        format!("DROP {}", starter.id)
                    } else if tree.fruits > 0 && starter.free_capacity() > 0 {
                        format!("HARVEST {}", starter.id)
                    } else {
                        "WAIT".to_string()
                    };
                }
                if starter.carry[APPLE] > 0 {
                    format!("PLANT {} APPLE", starter.id)
                } else if starter.total_carried() > 0 {
                    format!("DROP {}", starter.id)
                } else {
                    format!("PICK {} APPLE", starter.id)
                }
            }

            fn fruit_kind(stock: &[i32; 6], bank: bool) -> Option<PlantKind> {
                let items = if bank {
                    [BANANA, PLUM, LEMON, APPLE]
                } else {
                    [PLUM, LEMON, APPLE, BANANA]
                };
                items.into_iter()
                    .find(|item| stock[*item] > 0)
                    .map(|item| match item {
                        PLUM => PlantKind::Plum,
                        LEMON => PlantKind::Lemon,
                        APPLE => PlantKind::Apple,
                        _ => PlantKind::Banana,
                    })
            }

            fn endgame_candidates(
                view: &GameState,
                unit: &Unit,
                focus: Option<PlantKind>,
            ) -> Vec<Candidate> {
                if unit.carry[WOOD] > 0 {
                    return MoisanBot::bank_candidates(view, unit);
                }
                let turns_left = TOTAL_TURNS - view.turn + 1;
                if let Some(kind) = Self::fruit_kind(&unit.carry, false) {
                    if view.turn <= 250 && (view.turn < 100 || view.plants.len() > 2) {
                        return MoisanBot::bank_candidates(view, unit);
                    }
                    let distance = bfs_distances(&view.walkable, &[unit.cell]);
                    let target = ortho_neighbors(view.shacks[0])
                        .into_iter()
                        .filter(|cell| view.walkable.contains(cell))
                        .filter(|cell| view.plant_at(*cell).is_none())
                        .filter(|cell| distance.contains_key(cell))
                        .filter(|cell| !view.units.iter().any(|other| {
                            other.player == 0 && other.id != unit.id && other.cell == *cell
                        }))
                        .min_by_key(|cell| (distance[cell], *cell));
                    let Some(cell) = target else {
                        return MoisanBot::bank_candidates(view, unit);
                    };
                    let travel = MoisanBot::ceil_div(
                        distance[&cell], unit.stats.movement_speed
                    );
                    if travel + MoisanBot::ceil_div(
                        tree_health(kind, 1), unit.stats.chop_power
                    ) + 3 > turns_left {
                        return MoisanBot::bank_candidates(view, unit);
                    }
                    return vec![Candidate {
                        command: if unit.cell == cell {
                            format!("PLANT {} {}", unit.id, kind.as_str())
                        } else {
                            format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                        },
                        score: 9_000.0 - travel as f64,
                        target: Some(cell),
                    }];
                }
                if unit.total_carried() > 0 {
                    return MoisanBot::bank_candidates(view, unit);
                }
                let mut out = vec![MoisanBot::wait()];
                let chops = MoisanBot::chop_candidates(view, unit, focus);
                if view.turn > 250 || view.turn >= 100 && view.plants.len() <= 2 {
                    if let Some(kind) = Self::fruit_kind(&view.inventories[0], true) {
                    if is_adjacent(unit.cell, view.shacks[0])
                        && view.plant_at(unit.cell).is_none()
                        && MoisanBot::ceil_div(
                            tree_health(kind, 1), unit.stats.chop_power
                        ) + 3 <= turns_left
                    {
                        out.push(Candidate {
                            command: format!("PICK {} {}", unit.id, kind.as_str()),
                            score: 8_000.0,
                            target: Some(unit.cell),
                        });
                    }
                    }
                }
                out.extend(chops);
                out
            }

        }impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.ensure_opening(view);
                if view.turn >= 35
                    && self.desired_second
                        .is_some_and(|stats| !MoisanBot::can_train(view, stats))
                {
                    self.desired_second = Some(Stats {
                        movement_speed: 1,
                        carry_capacity: 1,
                        
                        chop_power: 1,
                    });
                }
                let desired = self.desired_second.unwrap();
                let train_now = MoisanBot::can_train(view, desired);
                let mut output = Vec::new();
                if train_now {
                    output.push(format!(
                        "TRAIN {} {} {} {}",
                        desired.movement_speed,
                        desired.carry_capacity,
                        0,
                        desired.chop_power
                    ));
                }
                let mut units: Vec<&Unit> = view.units
                    .iter()
                    .filter(|unit| unit.player == 0)
                    .collect();
                units.sort_by_key(|unit| unit.id);
                let early = units.len() < 2 && !train_now;
                let mut candidates_by_id = BTreeMap::new();
                let orchard_mother = self.orchard_mother;
                let orchard_active = orchard_mother.is_some() && units.len() >= 2;
                for (unit_index, unit) in units.into_iter().enumerate() {
                    let mut candidates = if orchard_active && unit_index == 0
                    {
                        vec![MoisanBot::wait()]
                    } else if view.turn > 250 || !early {
                        Self::endgame_candidates(view, unit, self.type_to_cut)
                    } else {
                        MoisanBot::early_candidates(view, unit, desired)
                    };
                    if orchard_active {
                        if let Some(mother) = orchard_mother {
                            candidates.retain(|candidate| !matches!(candidate.target,
                                Some(cell)
                                if cell == mother));
                        }
                    }
                    if train_now
                        && unit.cell == view.shacks[0]
                        && !candidates.iter().any(|row| row.command.starts_with("MOVE "))
                    {
                        if let Some(cell) = ortho_neighbors(view.shacks[0])
                            .into_iter()
                            .find(|cell| view.walkable.contains(cell))
                        {
                            candidates.push(Candidate {
                                command: format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
                                score: 19_000.0,
                                target: Some(cell),
                            });
                        }
                    }
                    candidates_by_id.insert(unit.id, candidates);
                }
                let mut selected = MoisanBot::select(
                    candidates_by_id, &view.inventories[0]
                );
                if orchard_active {
                    selected[0] = self.orchard_command(view);
                }
                MoisanBot::resolve_move_conflicts(view, &mut selected, &mut self.move_history);
                output.extend(selected);
                output
            }
        }}use crate::game::GameState;pub trait Bot{fn commands(&mut self,view:&GameState)->Vec<String>;}}use std::io::{self,Write};use crate::bot::moisan::YamoBot;use crate::bot::Bot;use crate::game::protocol::{read_static_map,read_turn};fn main(){let stdin=io::stdin();let stdout=io::stdout();let mut reader=io::BufReader::new(stdin.lock());let mut out=io::BufWriter::new(stdout.lock());let Some(map)=read_static_map(&mut reader)else{return;};let mut bot=YamoBot::new();let mut turn=1;while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);writeln!(out,"{}",commands.join(";")).expect("write command line");out.flush().expect("flush command line");turn+=1;}}
