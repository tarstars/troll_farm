mod game{pub mod types{use std::collections::BTreeSet;pub type Cell=(i32,i32);pub const ITEM_COUNT:usize=6;pub const PLUM:usize=0;pub const LEMON:usize=1;pub const APPLE:usize=2;pub const BANANA:usize=3;pub const IRON:usize=4;pub const WOOD:usize=5;pub type Stock=[i32;ITEM_COUNT];#[derive(Clone,Copy,Debug,Eq,PartialEq,Ord,PartialOrd,Hash)]pub enum PlantKind{Plum,Lemon,Apple,Banana,}impl PlantKind{pub fn parse(value:&str)->Option<PlantKind>{match value.to_ascii_uppercase().as_str(){"PLUM"=>Some(PlantKind::Plum),"LEMON"=>Some(PlantKind::Lemon),"APPLE"=>Some(PlantKind::Apple),"BANANA"=>Some(PlantKind::Banana),_=>None,}}pub fn as_str(self)->&'static str{match self{PlantKind::Plum=>"PLUM",PlantKind::Lemon=>"LEMON",PlantKind::Apple=>"APPLE",PlantKind::Banana=>"BANANA",}}pub fn item_index(self)->usize{match self{PlantKind::Plum=>PLUM,PlantKind::Lemon=>LEMON,PlantKind::Apple=>APPLE,PlantKind::Banana=>BANANA,}}}#[derive(Clone,Copy,Debug,Eq,PartialEq)]pub struct Stats{pub movement_speed:i32,pub carry_capacity:i32,pub harvest_power:i32,pub chop_power:i32,}impl Stats{pub fn tuple(self)->(i32,i32,i32,i32){(self.movement_speed,self.carry_capacity,self.harvest_power,self.chop_power,)}}#[derive(Clone,Debug,Eq,PartialEq)]pub struct Unit{pub id:i32,pub player:usize,pub cell:Cell,pub stats:Stats,pub carry:Stock,}impl Unit{pub fn total_carried(&self)->i32{self.carry.iter().sum()}pub fn free_capacity(&self)->i32{self.stats.carry_capacity-self.total_carried()}}#[derive(Clone,Debug,Eq,PartialEq)]pub struct Plant{pub kind:PlantKind,pub cell:Cell,pub size:i32,pub health:i32,pub fruits:i32,pub cooldown:i32,}#[derive(Clone,Debug,Eq,PartialEq)]pub struct GameState{pub width:i32,pub height:i32,pub walkable:BTreeSet<Cell>,pub shacks:[Cell;2],pub inventories:[Stock;2],pub units:Vec<Unit>,pub plants:Vec<Plant>,pub scores:[i32;2],pub turn:i32,pub next_id:i32,pub iron:BTreeSet<Cell>,pub water:BTreeSet<Cell>,}impl GameState{pub fn plant_at(&self,cell:Cell)->Option<usize>{self.plants.iter().position(|plant|plant.cell==cell)}pub fn unit(&self,id:i32)->Option<&Unit>{self.units.iter().find(|unit|unit.id==id)}}}pub mod rules{use super::types::{PlantKind,Stock,APPLE,IRON,LEMON,PLUM,WOOD};pub const TOTAL_TURNS:i32=300;pub const WOOD_POINTS:i32=4;pub fn plant_cooldown(kind:PlantKind)->i32{match kind{PlantKind::Plum=>8,PlantKind::Lemon=>8,PlantKind::Apple=>9,PlantKind::Banana=>6,}}pub fn water_boost(kind:PlantKind)->i32{match kind{PlantKind::Plum=>5,PlantKind::Lemon=>5,PlantKind::Apple=>7,PlantKind::Banana=>2,}}pub fn tree_health_params(kind:PlantKind)->(i32,i32){match kind{PlantKind::Plum|PlantKind::Lemon=>(4,2),PlantKind::Apple=>(8,3),PlantKind::Banana=>(2,1),}}pub fn tree_health(kind:PlantKind,size:i32)->i32{let(base,slope)=tree_health_params(kind);base+slope*size}pub fn effective_cooldown(kind:PlantKind,near_water:bool)->i32{plant_cooldown(kind)-if near_water{water_boost(kind)}else{0}}pub fn training_cost(n:i32,talents:(i32,i32,i32,i32))->Stock{let(ms,cc,hp,chop)=talents;let mut cost=[0;6];cost[PLUM]=n+ms*ms;cost[LEMON]=n+cc*cc;cost[APPLE]=n+hp*hp;cost[IRON]=n+chop*chop;cost}pub fn score(inventory:&Stock)->i32{inventory[PLUM]+inventory[LEMON]+inventory[APPLE]+inventory[3]+WOOD_POINTS*inventory[WOOD]}pub fn item_index(name:&str)->Option<usize>{match name.to_ascii_uppercase().as_str(){"PLUM"=>Some(PLUM),"LEMON"=>Some(LEMON),"APPLE"=>Some(APPLE),"BANANA"=>Some(3),"IRON"=>Some(IRON),"WOOD"=>Some(WOOD),_=>None,}}}pub mod nav{use super::types::Cell;use std::collections::{BTreeMap,BTreeSet,VecDeque};pub const NEIGHBORS:[Cell;4]=[(0,1),(1,0),(0,-1),(-1,0)];pub fn manhattan(a:Cell,b:Cell)->i32{(a.0-b.0).abs()+(a.1-b.1).abs()}pub fn ortho_neighbors(cell:Cell)->[Cell;4]{[(cell.0,cell.1+1),(cell.0+1,cell.1),(cell.0,cell.1-1),(cell.0-1,cell.1),]}pub fn is_adjacent(a:Cell,b:Cell)->bool{manhattan(a,b)==1}pub fn bfs_distances(walkable:&BTreeSet<Cell>,sources:&[Cell])->BTreeMap<Cell,i32>{let mut dist=BTreeMap::new();let mut queue=VecDeque::new();for&cell in sources{if dist.insert(cell,0).is_none(){queue.push_back(cell);}}while let Some(cell)=queue.pop_front(){let d=dist[&cell];for delta in NEIGHBORS{let next=(cell.0+delta.0,cell.1+delta.1);if walkable.contains(&next)&&!dist.contains_key(&next){dist.insert(next,d+1);queue.push_back(next);}}}dist}pub fn next_cell(walkable:&BTreeSet<Cell>,current:Cell,target:Cell,speed:i32)->Cell{let from_current=bfs_distances(walkable,&[current]);if let Some(distance)=from_current.get(&target){if*distance<=speed{return target;}}let to_target=if!from_current.contains_key(&target){if from_current.is_empty(){return current;}let best_manhattan=from_current.keys().map(|cell|manhattan(target,*cell)).min().unwrap();let goals:Vec<Cell> =from_current.keys().filter(|cell|manhattan(target,**cell)==best_manhattan).copied().collect();bfs_distances(walkable,&goals)}else{bfs_distances(walkable,&[target])};from_current.iter().filter(|(cell,distance)|**distance<=speed&&to_target.contains_key(*cell)).map(|(cell,_)|*cell).min_by_key(|cell|(to_target[cell],*cell)).unwrap_or(current)}}pub mod protocol{use super::rules::score;use super::types::{Cell,GameState,Plant,PlantKind,Stats,Unit};use std::collections::BTreeSet;use std::io::BufRead;#[derive(Clone,Debug)]pub struct StaticMap{pub width:i32,pub height:i32,pub walkable:BTreeSet<Cell>,pub shacks:[Cell;2],pub iron:BTreeSet<Cell>,pub water:BTreeSet<Cell>,}pub fn read_line(reader:&mut impl BufRead)->Option<String>{let mut line=String::new();match reader.read_line(&mut line){Ok(0)=>None,Ok(_)=>Some(line.trim_end_matches('\n').trim_end_matches('\r').to_string(),),Err(_)=>None,}}pub fn read_static_map(reader:&mut impl BufRead)->Option<StaticMap>{let header=read_line(reader)?;let mut parts=header.split_whitespace();let width=parts.next()?.parse().ok()?;let height=parts.next()?.parse().ok()?;let mut rows=Vec::new();for _ in 0..height{rows.push(read_line(reader)?);}Some(parse_static_map(width,height,&rows))}pub fn parse_static_map(width:i32,height:i32,rows:&[String])->StaticMap{let mut walkable=BTreeSet::new();let mut shacks=[(0,0),(0,0)];let mut iron=BTreeSet::new();let mut water=BTreeSet::new();for(y,row)in rows.iter().enumerate(){for(x,ch)in row.chars().enumerate(){let cell=(x as i32,y as i32);match ch{'0'=>shacks[0]=cell,'1'=>shacks[1]=cell,'.'=>{walkable.insert(cell);}'+'=>{iron.insert(cell);}'~'=>{water.insert(cell);}_=>{}}}}StaticMap{width,height,walkable,shacks,iron,water,}}pub fn read_turn(reader:&mut impl BufRead,map:&StaticMap,turn:i32)->Option<GameState>{let mut inventories=[[0;6];2];for inv in&mut inventories{let line=read_line(reader)?;let values:Vec<i32> =line.split_whitespace().map(|value|value.parse().ok()).collect::<Option<Vec<i32>>>()?;if values.len()!=6{return None;}inv.copy_from_slice(&values);}let tree_count:usize=read_line(reader)?.trim().parse().ok()?;let mut plants=Vec::with_capacity(tree_count);for _ in 0..tree_count{let line=read_line(reader)?;let fields:Vec<&str> =line.split_whitespace().collect();if fields.len()!=7{return None;}plants.push(Plant{kind:PlantKind::parse(fields[0])?,cell:(fields[1].parse().ok()?,fields[2].parse().ok()?),size:fields[3].parse().ok()?,health:fields[4].parse().ok()?,fruits:fields[5].parse().ok()?,cooldown:fields[6].parse().ok()?,});}let unit_count:usize=read_line(reader)?.trim().parse().ok()?;let mut units=Vec::with_capacity(unit_count);let mut next_id=0;for _ in 0..unit_count{let line=read_line(reader)?;let values:Vec<i32> =line.split_whitespace().map(|value|value.parse().ok()).collect::<Option<Vec<i32>>>()?;if values.len()!=14{return None;}next_id=next_id.max(values[0]+1);units.push(Unit{id:values[0],player:values[1]as usize,cell:(values[2],values[3]),stats:Stats{movement_speed:values[4],carry_capacity:values[5],harvest_power:values[6],chop_power:values[7],},carry:[values[8],values[9],values[10],values[11],values[12],values[13],],});}Some(GameState{width:map.width,height:map.height,walkable:map.walkable.clone(),shacks:map.shacks,inventories,units,plants,scores:[score(&inventories[0]),score(&inventories[1])],turn,next_id,iron:map.iron.clone(),water:map.water.clone(),})}}pub use types::GameState;}mod bot{pub mod moisan{use super::Bot;use crate::game::nav::{bfs_distances,is_adjacent,manhattan,next_cell,ortho_neighbors};use crate::game::rules::{effective_cooldown,item_index,score,training_cost,tree_health,TOTAL_TURNS,};use crate::game::types::{Cell,GameState,Plant,PlantKind,Stats,Unit,APPLE,BANANA,IRON,LEMON,PLUM,WOOD,};use std::collections::{BTreeMap,BTreeSet};#[derive(Clone,Copy,Debug,Eq,PartialEq,Ord,PartialOrd)]enum Target{None,Shack,Bank(Cell),Cell(Cell),Tree(Cell),}#[derive(Clone,Debug)]struct Candidate{command:String,score:f64,target:Target,}struct MoisanBot;#[derive(Clone,Copy,Debug,Eq,PartialEq)]pub struct YamoBot {
            announced: bool,
            type_to_cut: Option<PlantKind>,
            desired_second: Option<Stats>,
        }#[derive(Clone,Copy)]struct PredictedTree{size:i32,health:i32,cooldown:i32,}impl MoisanBot{fn focus_type(view:&GameState)->PlantKind{let starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).iter().filter(|cell|view.walkable.contains(cell)).copied().collect();let dist=bfs_distances(&view.walkable,&starts);let sum=|kind:PlantKind|view.plants.iter().filter(|plant|plant.kind==kind).map(|plant|dist.get(&plant.cell).copied().unwrap_or(10_000)).sum::<i32>();let lemon=sum(PlantKind::Lemon);let plum=sum(PlantKind::Plum);if lemon<=plum&&plum-lemon<=8{PlantKind::Plum}else if lemon<=plum{PlantKind::Lemon}else{PlantKind::Plum}}fn ceil_div(a:i32,b:i32)->i32{if b<=0{10_000}else{(a+b-1)/b}}fn carry_total(unit:&Unit)->i32{unit.carry.iter().sum()}fn carrying_any(unit:&Unit)->bool{Self::carry_total(unit)>0}fn bank_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{let dist=bfs_distances(&view.walkable,&[unit.cell]);let mut out:Vec<Candidate> =ortho_neighbors(view.shacks[0]).into_iter().filter(|cell|view.walkable.contains(cell)&&dist.contains_key(cell)).map(|cell|{let at_drop=unit.cell==cell;Candidate{command:if at_drop{format!("DROP {}",unit.id)}else{format!("MOVE {} {} {}",unit.id,cell.0,cell.1)},score:if at_drop{8_000.0}else{7_000.0-Self::ceil_div(dist[&cell],unit.stats.movement_speed)as f64},target:Target::Bank(cell),}}).collect();if out.is_empty(){out.push(Candidate{command:format!("MOVE {} {} {}",unit.id,view.shacks[0].0,view.shacks[0].1),score:7_000.0,target:Target::Shack,});}out}fn can_train(view:&GameState,stats:Stats)->bool{let n=view.units.iter().filter(|unit|unit.player==0).count()as i32;if n>=2||TOTAL_TURNS-view.turn<=20{return false;}let cost=training_cost(n,stats.tuple());let pay_iron=!view.iron.is_empty();view.inventories[0][PLUM]>=cost[PLUM]&&view.inventories[0][LEMON]>=cost[LEMON]&&view.inventories[0][APPLE]>=cost[APPLE]&&(!pay_iron||view.inventories[0][IRON]>=cost[IRON])}fn ticks_until_fruit(view:&GameState,plant:&Plant)->i32{if plant.fruits>0{return 0;}let near_water=view.water.iter().any(|water|is_adjacent(*water,plant.cell));let mut size=plant.size;let mut cooldown=plant.cooldown.max(0);for turns in 1..=100{if cooldown>0{cooldown-=1;}if cooldown==0{if size<4{size+=1;cooldown=effective_cooldown(plant.kind,near_water);}else{return turns;}}}100}fn early_candidates(view:&GameState,unit:&Unit,desired:Stats)->Vec<Candidate>{let mut out=vec![Self::wait()];if Self::carrying_any(unit)||unit.free_capacity()<=0{out.extend(Self::bank_candidates(view,unit));return out;}let n=view.units.iter().filter(|unit|unit.player==0).count()as i32;let cost=training_cost(n,desired.tuple());for item in[PLUM,LEMON,APPLE,IRON]{if item==APPLE&&cost[item]<=view.inventories[0][item]{continue;}if item!=APPLE&&cost[item]<=view.inventories[0][item]{continue;}if item==IRON{out.extend(Self::iron_candidates(view,unit,6_100.0));}else{let kind=match item{PLUM=>PlantKind::Plum,LEMON=>PlantKind::Lemon,APPLE=>PlantKind::Apple,_=>unreachable!(),};out.extend(Self::fruit_candidates(view,unit,kind,6_000.0));}}if out.len()==1{out.extend(Self::chop_candidates(view,unit,None));}out}fn fruit_candidates(view:&GameState,unit:&Unit,kind:PlantKind,base_score:f64,)->Vec<Candidate>{let mut out=Vec::new();if view.plants.iter().any(|plant|plant.cell==unit.cell&&plant.kind==kind&&plant.fruits>0){out.push(Candidate{command:format!("HARVEST {}",unit.id),score:base_score+900.0,target:Target::Tree(unit.cell),});}let dist=bfs_distances(&view.walkable,&[unit.cell]);for plant in&view.plants{if plant.kind!=kind||plant.health<=0||!dist.contains_key(&plant.cell){continue;}let travel=Self::ceil_div(dist[&plant.cell],unit.stats.movement_speed);let wait=(Self::ticks_until_fruit(view,plant)-travel).max(0);out.push(Candidate{command:format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1),score:base_score-(travel+wait)as f64,target:Target::Tree(plant.cell),});}out}fn iron_candidates(view:&GameState,unit:&Unit,base_score:f64)->Vec<Candidate>{let mut out=Vec::new();if view.iron.iter().any(|iron|is_adjacent(*iron,unit.cell)){out.push(Candidate{command:format!("MINE {}",unit.id),score:base_score+900.0,target:Target::Cell(unit.cell),});}let dist=bfs_distances(&view.walkable,&[unit.cell]);for iron in&view.iron{for cell in ortho_neighbors(*iron){if!view.walkable.contains(&cell){continue;}if let Some(d)=dist.get(&cell){out.push(Candidate{command:format!("MOVE {} {} {}",unit.id,cell.0,cell.1),score:base_score-*d as f64,target:Target::Cell(cell),});}}}out}fn predicted_opp_chop(view:&GameState,plant:&Plant)->i32{let on_tree:i32=view.units.iter().filter(|unit|unit.player==1&&unit.cell==plant.cell).map(|unit|unit.stats.chop_power).sum();if on_tree>0{return on_tree;}let expected=tree_health(plant.kind,plant.size);if plant.health<expected{1}else{0}}fn predict_tree(view:&GameState,plant:&Plant,turns:i32)->Option<PredictedTree>{let mut size=plant.size;let mut health=plant.health;let mut fruits=plant.fruits;let mut cooldown=plant.cooldown;let opp_chop=Self::predicted_opp_chop(view,plant);let near_water=view.water.iter().any(|water|is_adjacent(*water,plant.cell));for _ in 0..turns{if opp_chop>0{health-=opp_chop;if health<=0{return None;}}if cooldown>0{cooldown-=1;}if cooldown==0&&health>0{if size<4{size+=1;health+=crate::game::rules::tree_health_params(plant.kind).1;cooldown=effective_cooldown(plant.kind,near_water);}else if fruits<3{fruits+=1;cooldown=effective_cooldown(plant.kind,near_water);}}}Some(PredictedTree{size,health,cooldown,})}fn chop_outcome(view:&GameState,plant:&Plant,predicted:PredictedTree,chop_power:i32,)->Option<(i32,i32)>{if chop_power<=0{return None;}let near_water=view.water.iter().any(|water|is_adjacent(*water,plant.cell));let cooldown_reset=effective_cooldown(plant.kind,near_water);let(_,growth_health)=crate::game::rules::tree_health_params(plant.kind);let mut size=predicted.size;let mut health=predicted.health;let mut cooldown=predicted.cooldown;for turns in 1..=100{health-=chop_power;if health<=0{return Some((turns,size));}if cooldown>0{cooldown-=1;}if cooldown==0&&size<4{size+=1;health+=growth_health;cooldown=cooldown_reset;}}None}fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>{let mut out=Vec::new();if unit.stats.chop_power<=0||unit.free_capacity()<=0{return out;}let from_unit=bfs_distances(&view.walkable,&[unit.cell]);let shack_starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).iter().filter(|cell|view.walkable.contains(cell)).copied().collect();let to_shack=bfs_distances(&view.walkable,&shack_starts);let opponent_trolls=view.units.iter().filter(|unit|unit.player==1).count();for plant in&view.plants{if plant.health<=0||!from_unit.contains_key(&plant.cell){continue;}let travel_turns=Self::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{continue;};if predicted.size<=0||predicted.health<=0{continue;}let return_turns=to_shack.get(&plant.cell).map(|d|Self::ceil_div(*d,unit.stats.movement_speed)).unwrap_or_else(||{Self::ceil_div(manhattan(plant.cell,view.shacks[0]),unit.stats.movement_speed,)});let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{continue;};let turns=(travel_turns+chop_turns+return_turns+1).max(1);if turns>TOTAL_TURNS-view.turn+1{continue;}let wood=final_size.min(unit.free_capacity());if wood<=0{continue;}let mut score=1000.0*wood as f64/turns as f64;if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{let opponent_distance=manhattan(plant.cell,view.shacks[1]);score+=900.0/(1+opponent_distance)as f64;}let command=if plant.cell==unit.cell{format!("CHOP {}",unit.id)}else{format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1)};out.push(Candidate{command,score,target:Target::Tree(plant.cell),});}out}fn wait()->Candidate{Candidate{command:"WAIT".to_string(),score:0.0,target:Target::None,}}fn compatible(a:Target,b:Target)->bool{if a==Target::None||b==Target::None{return true;}let cell=|target|match target{Target::Bank(cell)|Target::Cell(cell)|Target::Tree(cell)=>Some(cell),_=>None,};match(cell(a),cell(b)){(Some(a),Some(b))=>a!=b,_=>a!=b,}}fn picked_item(command:&str)->Option<usize>{let fields:Vec<_> =command.split_whitespace().collect();(fields.len()==3&&fields[0].eq_ignore_ascii_case("PICK")).then(||item_index(fields[2])).flatten()}fn stock_compatible(a:&Candidate,b:&Candidate,inventory:&[i32;6])->bool{match(Self::picked_item(&a.command),Self::picked_item(&b.command)){(Some(a),Some(b))if a==b=>inventory[a]>=2,_=>true,}}fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;6],)->Vec<String>{let ids:Vec<i32> =candidates_by_id.keys().copied().collect();if ids.is_empty(){return Vec::new();}if ids.len()==1{let best=candidates_by_id[&ids[0]].iter().max_by(|a,b|a.score.total_cmp(&b.score)).unwrap();return vec![best.command.clone()];}if ids.len()==2{let mut best_score=f64::NEG_INFINITY;let mut best_pair=None;for a in&candidates_by_id[&ids[0]]{for b in&candidates_by_id[&ids[1]]{if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){continue;}let score=a.score+b.score;if score>best_score{best_score=score;best_pair=Some((a.command.clone(),b.command.clone()));}}}if let Some((a,b))=best_pair{return vec![a,b];}}let mut used_targets=Vec::new();let mut used_stock=[0;6];let mut commands=Vec::new();for id in ids{let mut candidates=candidates_by_id[&id].clone();candidates.sort_by(|a,b|b.score.total_cmp(&a.score));let best=candidates.into_iter().find(|candidate|{used_targets.iter().all(|target|Self::compatible(candidate.target,*target))&&Self::picked_item(&candidate.command).map(|item|used_stock[item]<inventory[item]).unwrap_or(true)}).unwrap_or_else(Self::wait);used_targets.push(best.target);if let Some(item)=Self::picked_item(&best.command){used_stock[item]+=1;}commands.push(best.command);}commands}fn move_command(command:&str)->Option<(i32,Cell)>{let fields:Vec<&str> =command.split_whitespace().collect();if fields.len()!=4||!fields[0].eq_ignore_ascii_case("MOVE"){return None;}Some((fields[1].parse().ok()?,(fields[2].parse().ok()?,fields[3].parse().ok()?),))}fn resolve_move_conflicts(view:&GameState,commands:&mut[String]){Self::resolve_move_conflicts_with_priority(view,commands,&BTreeSet::new());}fn resolve_move_conflicts_with_priority(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,){Self::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,&BTreeSet::new(),);}fn resolve_move_conflicts_with_priority_and_forbidden(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,forbidden_for_non_priority:&BTreeSet<Cell>,){let command_by_id:BTreeMap<i32,usize> =commands.iter().enumerate().filter_map(|(index,command)|Self::move_command(command).map(|(id,_)|(id,index))).collect();let projections:Vec<(i32,usize,Cell,Cell,Cell)> =command_by_id.iter().filter_map(|(id,index)|{let unit=view.unit(*id)?;let(_,target)=Self::move_command(&commands[*index])?;let landing=next_cell(&view.walkable,unit.cell,target,unit.stats.movement_speed);Some((*id,*index,unit.cell,target,landing))}).collect();let moving_ids:BTreeSet<i32> =projections.iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,_,_,_,_)|*id).collect();let occupied_now:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.cell).collect();let mut reserved:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0&&!moving_ids.contains(&unit.id)).map(|unit|unit.cell).collect();for(_,index,current,_,landing)in&projections{if landing==current{commands[*index]="WAIT".to_string();}}let mut movers:Vec<(i32,usize,Cell,Cell)> =projections.into_iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,index,_,target,landing)|(id,index,target,landing)).collect();movers.sort_by(|a,b|{let a_priority=priority_ids.contains(&a.0);let b_priority=priority_ids.contains(&b.0);b_priority.cmp(&a_priority).then_with(||b.0.cmp(&a.0))});for(id,index,target,landing)in movers{let Some(unit)=view.unit(id)else{continue};let landing_forbidden=!priority_ids.contains(&id)&&forbidden_for_non_priority.contains(&landing);if!landing_forbidden&&!reserved.contains(&landing){reserved.insert(landing);commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);continue;}let toward_goal=bfs_distances(&view.walkable,&[target]);let detour=ortho_neighbors(unit.cell).into_iter().filter(|cell|view.walkable.contains(cell)).filter(|cell|!reserved.contains(cell)).filter(|cell|!occupied_now.contains(cell)).filter(|cell|{priority_ids.contains(&id)||!forbidden_for_non_priority.contains(cell)}).min_by_key(|cell|{(toward_goal.get(cell).copied().unwrap_or_else(||manhattan(*cell,target)),*cell,)});commands[index]=if let Some(cell)=detour{reserved.insert(cell);format!("MOVE {} {} {}",id,cell.0,cell.1)}else{"WAIT".to_string()};}}}impl YamoBot {
            pub fn new() -> Self {
                Self { announced: false, type_to_cut: None, desired_second: None }
            }

            fn ensure_opening(&mut self, view: &GameState) {
                if self.type_to_cut.is_none() {
                    self.type_to_cut = Some(MoisanBot::focus_type(view));
                }
                if self.desired_second.is_none() {
                    self.desired_second = Some(Self::choose_second_troll(view));
                }
            }

            fn choose_second_troll(view: &GameState) -> Stats {
                let mut best_key: Option<(bool, i32, i32, i32, i32, i32)> = None;
                let mut best_stats = Stats {
                    movement_speed: 1,
                    carry_capacity: 1,
                    harvest_power: 0,
                    chop_power: 1,
                };
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            let cost = training_cost(1, stats.tuple());
                            let mut deficit = (cost[PLUM] - view.inventories[0][PLUM]).max(0)
                                + (cost[LEMON] - view.inventories[0][LEMON]).max(0)
                                + (cost[APPLE] - view.inventories[0][APPLE]).max(0);
                            if !view.iron.is_empty() {
                                deficit += (cost[IRON] - view.inventories[0][IRON]).max(0);
                            }
                            let preferred = deficit <= 1 && carry_capacity >= 2;
                            let total = movement_speed + carry_capacity + chop_power;
                            let key = (
                                preferred,
                                if preferred { total } else { -deficit },
                                if preferred { -deficit } else { total },
                                chop_power,
                                carry_capacity,
                                movement_speed,
                            );
                            if best_key.map(|old| key > old).unwrap_or(true) {
                                best_key = Some(key);
                                best_stats = stats;
                            }
                        }
                    }
                }
                best_stats
            }

            fn strongest_affordable(view: &GameState) -> Option<Stats> {
                let mut best: Option<((i32, i32, i32, i32), Stats)> = None;
                for movement_speed in 1..=3 {
                    for carry_capacity in 1..=3 {
                        for chop_power in 1..=3 {
                            let stats = Stats {
                                movement_speed,
                                carry_capacity,
                                harvest_power: 0,
                                chop_power,
                            };
                            if !MoisanBot::can_train(view, stats) {
                                continue;
                            }
                            let key = (
                                movement_speed + carry_capacity + chop_power,
                                chop_power,
                                carry_capacity,
                                movement_speed,
                            );
                            if best.map(|old| key > old.0).unwrap_or(true) {
                                best = Some((key, stats));
                            }
                        }
                    }
                }
                best.map(|row| row.1)
            }

            fn fixed_bank_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                let starts: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let distance = bfs_distances(&view.walkable, &[unit.cell]);
                let door = starts
                    .into_iter()
                    .filter(|cell| distance.contains_key(cell))
                    .min();
                let Some(door) = door else { return vec![MoisanBot::wait()] };
                vec![Candidate {
                    command: if unit.cell == door {
                        format!("DROP {}", unit.id)
                    } else {
                        format!("MOVE {} {} {}", unit.id, door.0, door.1)
                    },
                    score: 20_000.0,
                    target: Target::Bank(door),
                }]
            }

            fn carried_fruit(unit: &Unit) -> Option<PlantKind> {
                [
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                    (BANANA, PlantKind::Banana),
                ]
                .into_iter()
                .find(|(item, _)| unit.carry[*item] > 0)
                .map(|(_, kind)| kind)
            }

            fn bank_fruit(view: &GameState) -> Option<PlantKind> {
                [
                    (BANANA, PlantKind::Banana),
                    (PLUM, PlantKind::Plum),
                    (LEMON, PlantKind::Lemon),
                    (APPLE, PlantKind::Apple),
                ]
                .into_iter()
                .find(|(item, _)| view.inventories[0][*item] > 0)
                .map(|(_, kind)| kind)
            }

            fn conversion_chop_turns(
                view: &GameState,
                cell: Cell,
                kind: PlantKind,
                chop_power: i32,
            ) -> i32 {
                if chop_power <= 0 { return 10_000; }
                let near_water = view.water.iter().any(|water| is_adjacent(*water, cell));
                let cooldown_reset = effective_cooldown(kind, near_water);
                let growth_health = crate::game::rules::tree_health_params(kind).1;
                let mut size = 1;
                let mut health = tree_health(kind, size);
                let mut cooldown = cooldown_reset;
                for turns in 1..=100 {
                    health -= chop_power;
                    if health <= 0 { return turns; }
                    if cooldown > 0 { cooldown -= 1; }
                    if cooldown == 0 && size < 4 {
                        size += 1;
                        health += growth_health;
                        cooldown = cooldown_reset;
                    }
                }
                10_000
            }

            fn endgame_candidates(view: &GameState, unit: &Unit) -> Vec<Candidate> {
                if unit.carry[WOOD] > 0 {
                    return Self::fixed_bank_candidates(view, unit);
                }
                let from_unit = bfs_distances(&view.walkable, &[unit.cell]);
                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])
                    .into_iter()
                    .filter(|cell| view.walkable.contains(cell))
                    .collect();
                let to_shack = bfs_distances(&view.walkable, &doors);
                let turns_left = TOTAL_TURNS - view.turn + 1;
                if let Some(kind) = Self::carried_fruit(unit) {
                    let mut out = vec![MoisanBot::wait()];
                    for cell in view.walkable.iter().filter(|cell| {
                        view.plant_at(**cell).is_none()
                            && from_unit.contains_key(*cell)
                            && to_shack.contains_key(*cell)
                            && !view.units.iter().any(|other| {
                                other.player == 0 && other.id != unit.id && other.cell == **cell
                            })
                    }) {
                        let travel = MoisanBot::ceil_div(
                            from_unit[cell], unit.stats.movement_speed
                        );
                        let chop = Self::conversion_chop_turns(
                            view, *cell, kind, unit.stats.chop_power
                        );
                        let home = MoisanBot::ceil_div(
                            to_shack[cell], unit.stats.movement_speed
                        ) + 1;
                        if travel + 1 + chop + home > turns_left { continue; }
                        out.push(Candidate {
                            command: if unit.cell == *cell {
                                format!("PLANT {} {}", unit.id, kind.as_str())
                            } else {
                                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                            },
                            score: 9_000.0 - travel as f64,
                            target: Target::Cell(*cell),
                        });
                    }
                    return out;
                }
                if unit.total_carried() > 0 {
                    return Self::fixed_bank_candidates(view, unit);
                }
                let mut out = vec![MoisanBot::wait()];
                let chops = MoisanBot::chop_candidates(view, unit, None);
                if let Some(mut current) = chops
                    .iter()
                    .find(|candidate| candidate.command == format!("CHOP {}", unit.id))
                    .cloned()
                {
                    current.score = 10_000.0;
                    out.push(current);
                    return out;
                }
                if let Some(kind) = Self::bank_fruit(view) {
                    if is_adjacent(unit.cell, view.shacks[0])
                        && view.plant_at(unit.cell).is_none()
                        && Self::conversion_chop_turns(
                            view, unit.cell, kind, unit.stats.chop_power
                        ) + 3 <= turns_left
                    {
                        out.push(Candidate {
                            command: format!("PICK {} {}", unit.id, kind.as_str()),
                            score: 8_000.0,
                            target: Target::Cell(unit.cell),
                        });
                    }
                }
                out.extend(chops);
                out
            }

            fn ordinary_candidates(
                view: &GameState,
                unit: &Unit,
                early: bool,
                desired: Stats,
            ) -> Vec<Candidate> {
                if unit.total_carried() > 0 {
                    return Self::fixed_bank_candidates(view, unit);
                }
                if early {
                    return MoisanBot::early_candidates(view, unit, desired);
                }
                let mut out = vec![MoisanBot::wait()];
                out.extend(MoisanBot::chop_candidates(view, unit, None));
                out
            }
        }impl Bot for YamoBot {
            fn commands(&mut self, view: &GameState) -> Vec<String> {
                self.ensure_opening(view);
                if view.turn >= 35
                    && self.desired_second
                        .is_some_and(|stats| !MoisanBot::can_train(view, stats))
                {
                    if let Some(stats) = Self::strongest_affordable(view) {
                        self.desired_second = Some(stats);
                    }
                }
                let desired = self.desired_second.unwrap();
                let train_now = MoisanBot::can_train(view, desired);
                let mut output = Vec::new();
                if !self.announced {
                    self.announced = true;
                    output.push("MSG e7a-half-size-logical".to_string());
                }
                if train_now {
                    output.push(format!(
                        "TRAIN {} {} {} {}",
                        desired.movement_speed,
                        desired.carry_capacity,
                        desired.harvest_power,
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
                for unit in units {
                    let mut candidates = if view.turn > 250 {
                        Self::endgame_candidates(view, unit)
                    } else {
                        Self::ordinary_candidates(view, unit, early, desired)
                    };
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
                                target: Target::Cell(cell),
                            });
                        }
                    }
                    candidates_by_id.insert(unit.id, candidates);
                }
                let mut selected = MoisanBot::select(
                    candidates_by_id, &view.inventories[0]
                );
                MoisanBot::resolve_move_conflicts(view, &mut selected);
                output.extend(selected);
                if output.is_empty() { output.push("WAIT".to_string()); }
                output
            }
        }}use crate::game::GameState;pub trait Bot{fn commands(&mut self,view:&GameState)->Vec<String>;}}use std::io::{self,Write};use crate::bot::moisan::YamoBot;use crate::bot::Bot;use crate::game::protocol::{read_static_map,read_turn};fn main(){let stdin=io::stdin();let stdout=io::stdout();let mut reader=io::BufReader::new(stdin.lock());let mut out=io::BufWriter::new(stdout.lock());let Some(map)=read_static_map(&mut reader)else{return;};let mut bot=YamoBot::new();let mut turn=1;while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);writeln!(out,"{}",commands.join(";")).expect("write command line");out.flush().expect("flush command line");turn+=1;}}
