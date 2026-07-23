#!/usr/bin/env python3
"""Generate narrowly-scoped variants from the immutable live-agent artifact."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

TUNED_CARRY_BLOCK = (
    "pub const TUNED_CARRY:Self=Self{train_horizon:15,preferred_min_carry:2,"
    "max_carry_capacity:3,preferred_min_chop:1,max_chop_power:3,"
    "require_preferred:false,max_extra_eta:15,hard_train_turn:35,"
    "prefer_movement_ties:false,};"
)

FARM_FIRST_FARMER_BLOCK = (
    "fn farmer_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{"
    "let mut out=vec![Self::wait()];let ring=Self::ring_cells(view);"
    "let ring_set:BTreeSet<Cell>=ring.iter().copied().collect();"
    "let goal=|kind|match kind{PlantKind::Lemon=>3,PlantKind::Plum|PlantKind::Apple=>2,"
    "PlantKind::Banana=>8};let local=|kind|view.plants.iter().filter(|plant|plant.kind==kind"
    "&&plant.health>0&&ring_set.contains(&plant.cell)).count()as i32;"
    "let farm_kind=if view.turn>=120{PlantKind::Banana}else{[PlantKind::Lemon,"
    "PlantKind::Plum,PlantKind::Apple].into_iter().min_by_key(|kind|"
    "(local(*kind)-goal(*kind),view.inventories[0][kind.item_index()],kind.item_index()))"
    ".unwrap_or(PlantKind::Lemon)};let farm_item=farm_kind.item_index();"
    "let farm_needed=view.turn>=120||local(farm_kind)<goal(farm_kind);"
    "let dist=bfs_distances(&view.walkable,&[unit.cell]);let empty_ring:Vec<Cell>=ring.iter()"
    ".filter(|cell|view.plant_at(**cell).is_none()).filter(|cell|dist.contains_key(*cell))"
    ".filter(|cell|!view.units.iter().any(|other|other.player==0&&other.id!=unit.id&&"
    "other.cell==**cell)).copied().collect();if Self::carrying_any(unit)||"
    "unit.free_capacity()<=0{if farm_needed&&unit.carry[farm_item]>0{for cell in&empty_ring{"
    "let travel=Self::ceil_div(dist[cell],unit.stats.movement_speed);out.push(Candidate{"
    "command:if unit.cell==*cell{format!(\"PLANT {} {}\",unit.id,farm_kind.as_str())}else{"
    "format!(\"MOVE {} {} {}\",unit.id,cell.0,cell.1)},score:9_000.0-travel as f64,"
    "target:Target::Cell(*cell),});}}out.extend(Self::bank_candidates(view,unit));return out;}"
    "if farm_needed{for plant in view.plants.iter().filter(|plant|plant.kind==farm_kind&&"
    "plant.health>0&&plant.fruits>0&&dist.contains_key(&plant.cell)&&(!ring_set.contains("
    "&plant.cell)||Self::is_ring_diagonal(view,plant.cell))){let travel=Self::ceil_div("
    "dist[&plant.cell],unit.stats.movement_speed);let local_seed=ring_set.contains("
    "&plant.cell);out.push(Candidate{command:if unit.cell==plant.cell{format!(\"HARVEST {}\","
    "unit.id)}else{format!(\"MOVE {} {} {}\",unit.id,plant.cell.0,plant.cell.1)},score:if "
    "local_seed{8_200.0}else{7_600.0}-travel as f64,target:Target::Tree(plant.cell),});}"
    "if!empty_ring.is_empty()&&view.inventories[0][farm_item]>0{for cell in ortho_neighbors("
    "view.shacks[0]){let Some(distance)=dist.get(&cell)else{continue;};if!view.walkable.contains("
    "&cell){continue;}out.push(Candidate{command:if unit.cell==cell{format!(\"PICK {} {}\","
    "unit.id,farm_kind.as_str())}else{format!(\"MOVE {} {} {}\",unit.id,cell.0,cell.1)},"
    "score:7_800.0-Self::ceil_div(*distance,unit.stats.movement_speed)as f64,"
    "target:Target::Cell(cell),});}}}for kind in PlantKind::ALL{let base=if kind=="
    "PlantKind::Banana{3_400.0}else{3_000.0};out.extend(Self::fruit_candidates(view,unit,kind,"
    "base));}out}"
)

ADAPTIVE_HYBRID_FUNDING_BLOCK = (
    "fn adaptive_hybrid_funding_candidates(view:&GameState,unit:&Unit,goal:Stats,"
    "starter:bool)->Vec<Candidate>{let mut out=vec![Self::wait()];let cost=training_cost(2,"
    "goal.tuple());if Self::carrying_any(unit)||unit.free_capacity()<=0{let ring="
    "Self::ring_cells(view);let dist=bfs_distances(&view.walkable,&[unit.cell]);for kind in "
    "[PlantKind::Lemon,PlantKind::Plum,PlantKind::Apple]{let item=kind.item_index();if "
    "unit.carry[item]<=0||view.inventories[0][item]<cost[item]||view.plants.iter().any("
    "|plant|plant.kind==kind&&ring.contains(&plant.cell)){continue;}for cell in ring.iter()"
    ".filter(|cell|view.plant_at(**cell).is_none()&&dist.contains_key(*cell)).filter(|cell|"
    "!view.units.iter().any(|other|other.player==0&&other.id!=unit.id&&other.cell==**cell)){"
    "out.push(Candidate{command:if unit.cell==*cell{format!(\"PLANT {} {}\",unit.id,"
    "kind.as_str())}else{format!(\"MOVE {} {} {}\",unit.id,cell.0,cell.1)},score:8_500.0-"
    "Self::ceil_div(dist[cell],unit.stats.movement_speed)as f64,target:Target::Cell(*cell),});"
    "}}out.extend(Self::bank_candidates(view,unit));return out;}let order=if starter{[LEMON,"
    "PLUM,APPLE,IRON]}else{[IRON,PLUM,LEMON,APPLE]};for(priority,item)in order.into_iter()"
    ".enumerate(){if view.inventories[0][item]>=cost[item]{continue;}let base=700.0-80.0*"
    "priority as f64;if item==IRON{out.extend(Self::iron_candidates(view,unit,base));}else{"
    "let kind=match item{PLUM=>PlantKind::Plum,LEMON=>PlantKind::Lemon,APPLE=>"
    "PlantKind::Apple,_=>unreachable!(),};out.extend(Self::fruit_candidates(view,unit,kind,"
    "base));}}out}fn farmer_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{Self::"
    "adaptive_hybrid_funding_candidates(view,unit,Stats{movement_speed:3,carry_capacity:4,"
    "harvest_power:1,chop_power:3},false)}"
)


def replace_once(source: str, before: str, after: str, label: str) -> str:
    count = source.count(before)
    if count != 1:
        raise RuntimeError(f"expected one {label!r} replacement site, found {count}")
    return source.replace(before, after, 1)


def make_farm_first_orchard(source: str) -> str:
    """Build the replay-derived farm-first option from the full promoted artifact."""

    result = replace_once(
        source,
        "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
        "if n>=4||TOTAL_TURNS-view.turn<=20{return false;}",
        "farm-first train cap",
    )
    before = (
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll);let train_now=!self.opening_abandoned&&"
        "MoisanBot::can_train(view,desired);"
    )
    after = (
        "let own_count=view.units.iter().filter(|unit|unit.player==0).count();"
        "let farmer_level=|item:usize,cap:i32|{let available=(view.inventories[0][item]-1).max(0);"
        "let level=if available>=9{3}else if available>=4{2}else{1};level.min(cap)};"
        "let desired=if own_count==1{Stats{movement_speed:farmer_level(PLUM,2),"
        "carry_capacity:farmer_level(LEMON,3),harvest_power:farmer_level(APPLE,2),"
        "chop_power:1}}else if own_count==2{Stats{movement_speed:2,carry_capacity:2,"
        "harvest_power:0,chop_power:2}}else if own_count==3{Stats{movement_speed:2,"
        "carry_capacity:2,harvest_power:0,chop_power:2}}else{self.desired_second.map("
        "|objective|objective.stats)"
        ".unwrap_or_else(Self::fallback_second_troll)};let train_now=!self.opening_abandoned&&"
        "(own_count==1||(own_count==2&&view.turn<=100)||(own_count==3&&view.turn<=180))&&"
        "MoisanBot::can_train(view,desired);"
    )
    result = replace_once(result, before, after, "farm-first staged specs")
    result = replace_once(
        result,
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
        "let my_units_count=my_units.len();let farm_ids:BTreeSet<i32>=my_units.iter().take(2)"
        ".map(|unit|unit.id).collect();let early=!self.opening_abandoned&&my_units_count<4&&"
        "(my_units_count<2||(my_units_count==2&&view.turn<=100)||(my_units_count==3&&"
        "view.turn<=180))&&!train_now;",
        "farm-first stage gate",
    )
    result = replace_once(
        result,
        "}else if early{MoisanBot::early_candidates(view,unit,desired)}else{"
        "Self::main_candidates(view,unit,self.type_to_cut,self.idle_regeneration,"
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)}",
        "}else if early&&my_units_count==3&&!farm_ids.contains(&unit.id){let cost=training_cost("
        "3,desired.tuple());if unit.total_carried()>0{Self::main_candidates(view,unit,"
        "self.type_to_cut,self.idle_regeneration,self.persistent_regeneration,protected_tree,"
        "self.opponent_eta_penalty,)}else if!view.iron.is_empty()&&view.inventories[0][IRON]<"
        "cost[IRON]{let mut candidates=vec![MoisanBot::wait()];candidates.extend("
        "MoisanBot::iron_candidates(view,unit,7_500.0));candidates}else{Self::main_candidates("
        "view,unit,self.type_to_cut,self.idle_regeneration,self.persistent_regeneration,"
        "protected_tree,self.opponent_eta_penalty,)}}else if early{let mut candidates="
        "MoisanBot::early_candidates(view,unit,desired);candidates.extend("
        "MoisanBot::farmer_candidates(view,unit));candidates}else if "
        "my_units_count>=3&&farm_ids.contains(&unit.id){MoisanBot::farmer_candidates(view,unit)}"
        "else{Self::main_candidates(view,unit,self.type_to_cut,self.idle_regeneration,"
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)}",
        "farm-first role dispatch",
    )
    result = replace_once(
        result,
        "}else if committed_regeneration{Self::endgame_candidates(view,unit,self.type_to_cut,"
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)}",
        "}else if committed_regeneration&&!early&&!(my_units_count>=3&&farm_ids.contains("
        "&unit.id)){Self::endgame_candidates(view,unit,self.type_to_cut,"
        "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)}",
        "farm-first regeneration ownership",
    )
    start = result.find("fn farmer_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{")
    end = result.find("fn ring_chop_candidates", start)
    if start < 0 or end < 0 or result.find("fn farmer_candidates", start + 1, end) >= 0:
        raise RuntimeError("could not isolate the farm-first farmer implementation")
    result = result[:start] + FARM_FIRST_FARMER_BLOCK + result[end:]
    result = replace_once(
        result,
        "let has_second=unit_ids.len()>=2;",
        "let has_second=unit_ids.len()>=4;",
        "farm-first secure-orchard handoff",
    )
    return result


def make_adaptive_max_bank_hybrid(source: str) -> str:
    """Build the replay-derived compact hybrid option from the full promoted artifact."""

    result = replace_once(
        source,
        "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
        "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        "adaptive-hybrid train cap",
    )
    before = (
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll);let train_now=!self.opening_abandoned&&"
        "MoisanBot::can_train(view,desired);"
    )
    after = (
        "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let max_level="
        "|item:usize,cap:i32|{let available=(view.inventories[0][item]-own_count as i32)"
        ".max(0);let mut level=0;while level<cap&&(level+1)*(level+1)<=available{level+=1;}"
        "level.max(1)};let desired=if own_count==1{Stats{movement_speed:max_level(PLUM,3),"
        "carry_capacity:max_level(LEMON,3),harvest_power:max_level(APPLE,3),chop_power:"
        "max_level(IRON,3)}}else if own_count==2{Stats{movement_speed:max_level(PLUM,3),"
        "carry_capacity:max_level(LEMON,4),harvest_power:max_level(APPLE,1),chop_power:"
        "max_level(IRON,3)}}else{self.desired_second.map(|objective|objective.stats)"
        ".unwrap_or_else(Self::fallback_second_troll)};let own_doors:Vec<Cell>="
        "ortho_neighbors(view.shacks[0]).into_iter().filter(|cell|view.walkable.contains(cell))"
        ".collect();let enemy_doors:Vec<Cell>=ortho_neighbors(view.shacks[1]).into_iter()"
        ".filter(|cell|view.walkable.contains(cell)).collect();let own_distance=bfs_distances("
        "&view.walkable,&own_doors);let enemy_distance=bfs_distances(&view.walkable,"
        "&enemy_doors);let useful_private=view.plants.iter().any(|plant|plant.health>0&&"
        "own_distance.get(&plant.cell)==Some(&0)&&enemy_distance.get(&plant.cell).copied()"
        ".unwrap_or(10_000)>0);let later_ready=desired.movement_speed>=2&&desired."
        "carry_capacity>=3&&desired.harvest_power>=1&&desired.chop_power>=2;let train_now="
        "!self.opening_abandoned&&MoisanBot::can_train(view,desired)&&(own_count==1||"
        "(own_count==2&&view.turn>=66&&view.turn<=125&&later_ready&&useful_private));"
    )
    result = replace_once(result, before, after, "adaptive-hybrid staged specs")
    result = replace_once(
        result,
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
        "let starter_id=my_units.first().map(|unit|unit.id);let funding=!self."
        "opening_abandoned&&my_units.len()==2&&view.turn<=125&&useful_private&&!train_now;"
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
        "adaptive-hybrid funding gate",
    )
    result = replace_once(
        result,
        "let mut candidates=if scarce_farmer_id==Some(unit.id){self.scarce_farmer_candidates("
        "view,unit,self.type_to_cut)}else if committed_regeneration{",
        "let mut candidates=if scarce_farmer_id==Some(unit.id){self.scarce_farmer_candidates("
        "view,unit,self.type_to_cut)}else if funding{let goal=Stats{movement_speed:3,"
        "carry_capacity:4,harvest_power:1,chop_power:3};let mut candidates=MoisanBot::"
        "adaptive_hybrid_funding_candidates(view,unit,goal,starter_id==Some(unit.id));"
        "candidates.extend(Self::main_candidates(view,unit,self.type_to_cut,self."
        "idle_regeneration,self.persistent_regeneration,protected_tree,self."
        "opponent_eta_penalty,));candidates}else if committed_regeneration{",
        "adaptive-hybrid role dispatch",
    )
    start = result.find("fn farmer_candidates(view:&GameState,unit:&Unit)->Vec<Candidate>{")
    end = result.find("fn ring_chop_candidates", start)
    if start < 0 or end < 0 or result.find("fn farmer_candidates", start + 1, end) >= 0:
        raise RuntimeError("could not isolate the adaptive-hybrid helper site")
    result = result[:start] + ADAPTIVE_HYBRID_FUNDING_BLOCK + result[end:]
    result = replace_once(
        result,
        "let has_second=unit_ids.len()>=2;",
        "let has_second=unit_ids.len()>=3;",
        "adaptive-hybrid secure-orchard handoff",
    )
    return result


def make_adaptive_max_bank_first_only(source: str) -> str:
    """Ablate later funding while preserving the adaptive first hybrid exactly."""

    result = make_adaptive_max_bank_hybrid(source)
    result = replace_once(
        result,
        "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
        "adaptive-first train cap",
    )
    result = replace_once(
        result,
        "let funding=!self.opening_abandoned&&my_units.len()==2&&view.turn<=125&&"
        "useful_private&&!train_now;",
        "let funding=false;",
        "adaptive-first funding ablation",
    )
    result = replace_once(
        result,
        "let has_second=unit_ids.len()>=3;",
        "let has_second=unit_ids.len()>=2;",
        "adaptive-first secure-orchard handoff",
    )
    return result


def make_adaptive_max_bank_first_hp0(source: str) -> str:
    """Buy the immediate max movement/carry/chop worker without unused harvest."""

    result = make_adaptive_max_bank_first_only(source)
    return replace_once(
        result,
        "harvest_power:max_level(APPLE,3),chop_power:max_level(IRON,3)",
        "harvest_power:0,chop_power:max_level(IRON,3)",
        "adaptive first harvest-0 ablation",
    )


def make_adaptive_max_bank_surplus(source: str) -> str:
    """Keep normal work until a useful later max-bank hybrid is already affordable."""

    result = make_adaptive_max_bank_hybrid(source)
    return replace_once(
        result,
        "let funding=!self.opening_abandoned&&my_units.len()==2&&view.turn<=125&&"
        "useful_private&&!train_now;",
        "let funding=false;",
        "adaptive-surplus funding ablation",
    )


def make_adaptive_max_bank_mixed_surplus(source: str) -> str:
    """Use the first hybrid's harvest stat without an exclusive funding detour."""

    result = make_adaptive_max_bank_surplus(source)
    result = replace_once(
        result,
        "let starter_id=my_units.first().map(|unit|unit.id);let funding=false;",
        "let starter_id=my_units.first().map(|unit|unit.id);let hybrid_id=my_units.get(1)"
        ".map(|unit|unit.id);let funding=false;",
        "adaptive mixed-harvest role id",
    )
    before = (
        "self.opponent_eta_penalty,));candidates}else if committed_regeneration{"
    )
    after = (
        "self.opponent_eta_penalty,));candidates}else if hybrid_id==Some(unit.id)&&view.turn"
        "<=125&&unit.stats.harvest_power>0{let mut candidates=Self::main_candidates("
        "view,unit,self.type_to_cut,self.idle_regeneration,self.persistent_regeneration,"
        "protected_tree,self.opponent_eta_penalty,);for kind in PlantKind::ALL{candidates."
        "extend(MoisanBot::fruit_candidates(view,unit,kind,-500.0).into_iter().filter("
        "|candidate|candidate.command.starts_with(\"HARVEST \")));}candidates}else if "
        "committed_regeneration{"
    )
    return replace_once(result, before, after, "adaptive mixed-harvest role")


def make_adaptive_max_bank_cell_122(source: str) -> str:
    """Use max-bank training only for the replay-supported turn-one 1/2/2 cell."""

    result = replace_once(
        source,
        "desired_second:Option<OpeningObjective>,opening_initialized:bool,",
        "desired_second:Option<OpeningObjective>,adaptive_max_bank_stats:Option<Stats>,"
        "opening_initialized:bool,",
        "adaptive 1/2/2 state field",
    )
    result = replace_once(
        result,
        "desired_second:None,opening_initialized:false,",
        "desired_second:None,adaptive_max_bank_stats:None,opening_initialized:false,",
        "adaptive 1/2/2 state initialization",
    )
    result = replace_once(
        result,
        "self.reconcile_regeneration_commitments(view);self.reconcile_tree_commitments(view);"
        "self.ensure_opening(view);",
        "self.reconcile_regeneration_commitments(view);self.reconcile_tree_commitments(view);"
        "if!self.opening_initialized&&view.turn==1{let own_count=view.units.iter().filter("
        "|unit|unit.player==0).count();let max_level=|item:usize|{let available=(view."
        "inventories[0][item]-own_count as i32).max(0);let mut level=0;while level<3&&"
        "(level+1)*(level+1)<=available{level+=1;}level.max(1)};let max=Stats{movement_speed:"
        "max_level(PLUM),carry_capacity:max_level(LEMON),harvest_power:max_level(APPLE),"
        "chop_power:max_level(IRON)};if own_count==1&&max.movement_speed==1&&max."
        "carry_capacity==2&&max.harvest_power==2{self.adaptive_max_bank_stats=Some(max);}}"
        "self.ensure_opening(view);",
        "adaptive 1/2/2 frozen entry gate",
    )
    before = (
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll);let train_now=!self.opening_abandoned&&"
        "MoisanBot::can_train(view,desired);"
    )
    after = (
        "let original_desired=self.desired_second.map(|objective|objective.stats)"
        ".unwrap_or_else(Self::fallback_second_troll);let desired=self."
        "adaptive_max_bank_stats.unwrap_or(original_desired);let train_now=!self."
        "opening_abandoned&&MoisanBot::can_train(view,desired);"
    )
    return replace_once(result, before, after, "adaptive 1/2/2 desired stats")


def make_adaptive_max_bank_cell_122_carry3(source: str) -> str:
    """Enter 1/2/2 only when it replaces the parent's delayed 1/3 worker."""

    result = make_adaptive_max_bank_cell_122(source)
    return replace_once(
        result,
        "let desired=self.adaptive_max_bank_stats.unwrap_or(original_desired);",
        "let desired=if original_desired.movement_speed==1&&original_desired."
        "carry_capacity==3{self.adaptive_max_bank_stats.unwrap_or(original_desired)}else{"
        "original_desired};",
        "adaptive 1/2/2 parent-spec comparison",
    )


def make_adaptive_max_bank_cell_122_carry3_harvest(source: str, power: int) -> str:
    """Ablate unused paid harvest from the selected immediate worker."""

    if power not in (0, 1):
        raise ValueError("harvest ablation must be level 0 or 1")
    result = make_adaptive_max_bank_cell_122_carry3(source)
    return replace_once(
        result,
        "self.adaptive_max_bank_stats.unwrap_or(original_desired)}else{original_desired};",
        "self.adaptive_max_bank_stats.map(|stats|Stats{harvest_power:"
        f"{power},..stats}}).unwrap_or(original_desired)}}else{{original_desired}};",
        f"adaptive 1/2/2 harvest-{power} ablation",
    )


def training_policy_replacement(before: str, after: str) -> tuple[tuple[str, str], ...]:
    """Return one exact replacement confined to the live TUNED_CARRY constant."""

    count = TUNED_CARRY_BLOCK.count(before)
    if count != 1:
        raise AssertionError(f"training field {before!r} occurs {count} times")
    return ((TUNED_CARRY_BLOCK, TUNED_CARRY_BLOCK.replace(before, after, 1)),)


VARIANTS = {
    # Phase-2 complete macro option reconstructed from the rank-2 replay archetype.  Unlike the
    # earlier worker-only transplants, this changes the first trained role, keeps two workers on
    # explicit training-resource farming, adds a fixed wood worker, and preserves staged handoff.
    "farm-first-orchard": (),
    # Rank-1 replay archetype: buy the independently maximum-affordable hybrid, then use a
    # mixed starter/hybrid funding window and admit one later max-bank hybrid only on the
    # measured door-tree geometry.  The diagnostic option is capped at three total workers.
    "adaptive-max-bank-hybrid": (),
    "adaptive-max-bank-first-only": (),
    "adaptive-max-bank-first-hp0": (),
    "adaptive-max-bank-surplus": (),
    "adaptive-max-bank-mixed-surplus": (),
    "adaptive-max-bank-cell-122": (),
    "adaptive-max-bank-cell-122-carry3": (),
    "adaptive-max-bank-cell-122-carry3-hp0": (),
    "adaptive-max-bank-cell-122-carry3-hp1": (),
    "idle-harvest-off": ((
        "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),12,false,14,2,",
        "YamoBot::tuned_carry_regeneration_transit(),12,false,14,2,",
    ),),
    # The dormant flag is overloaded in the recovered source: it both creates the sparse plan
    # and globally disables idle harvest.  Scope that suppression to the assigned farmer so an
    # inactive dense map remains command-identical and the trained worker keeps the live fallback.
    "sparse-farming-on": (
        (
            "bot.idle_harvest=true;bot}",
            "bot.idle_harvest=true;bot.scarce_farming=true;bot}",
        ),
        (
            "&&!self.scarce_farming&&candidates.iter()",
            "&&scarce_farmer_id!=Some(unit.id)&&candidates.iter()",
        ),
    ),
    "sparse-farming-work-conserving": (
        (
            "bot.idle_harvest=true;bot}",
            "bot.idle_harvest=true;bot.scarce_farming=true;bot}",
        ),
        (
            "&&!self.scarce_farming&&candidates.iter()",
            "&&scarce_farmer_id!=Some(unit.id)&&candidates.iter()",
        ),
        (
            "if plan.crop.is_some(){return Vec::new();}",
            "if plan.crop.is_some(){return Self::main_candidates(view,unit,type_to_cut,false,"
            "self.persistent_regeneration,Some(mother),self.opponent_eta_penalty,);}",
        ),
        (
            "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
            "self.opponent_eta_penalty,).is_empty(){return Vec::new();}",
            "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
            "self.opponent_eta_penalty,).is_empty(){return Self::main_candidates(view,unit,"
            "type_to_cut,false,self.persistent_regeneration,Some(mother),"
            "self.opponent_eta_penalty,);}",
        ),
    ),
    # Start the existing mother/crop loop only after ordinary supply has collapsed.  Unlike the
    # original sparse policy, the farmer keeps chopping whenever no immediate loop action exists.
    "late-supply-loop": (
        (
            "bot.idle_harvest=true;bot}",
            "bot.idle_harvest=true;bot.scarce_farming=true;bot}",
        ),
        (
            "&&!self.scarce_farming&&candidates.iter()",
            "&&scarce_farmer_id!=Some(unit.id)&&candidates.iter()",
        ),
        (
            "if plan.crop.is_some(){return Vec::new();}",
            "if plan.crop.is_some(){return Self::main_candidates(view,unit,type_to_cut,false,"
            "self.persistent_regeneration,Some(mother),self.opponent_eta_penalty,);}",
        ),
        (
            "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
            "self.opponent_eta_penalty,).is_empty(){return Vec::new();}",
            "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
            "self.opponent_eta_penalty,).is_empty(){return Self::main_candidates(view,unit,"
            "type_to_cut,false,self.persistent_regeneration,Some(mother),"
            "self.opponent_eta_penalty,);}",
        ),
        (
            "if self.initial_tree_count.is_none(){self.initial_tree_count=Some(view.plants.len());"
            "if self.scarce_farming&&view.plants.len()<=14{self.scarce_plan=view.units.iter()"
            ".filter(|unit|unit.player==0).min_by_key(|unit|unit.id).map(|unit|ScarcePlan{"
            "farmer_id:unit.id,intent:ScarceIntent::NeedSeed,crop:None,});}}",
            "if self.initial_tree_count.is_none(){self.initial_tree_count=Some(view.plants.len());}"
            "if self.scarce_farming&&self.scarce_plan.is_none()&&view.turn>=100&&"
            "view.plants.len()<=2{self.scarce_plan=view.units.iter().filter(|unit|unit.player==0)"
            ".min_by_key(|unit|unit.id).map(|unit|ScarcePlan{farmer_id:unit.id,"
            "intent:ScarceIntent::NeedSeed,crop:None,});}",
        ),
    ),
    # Follow-on to late-supply-loop: do not establish the protected loop until no tree remains.
    "supply-trigger-empty": ((
        "view.turn>=100&&view.plants.len()<=2{self.scarce_plan=",
        "view.turn>=100&&view.plants.is_empty(){self.scarce_plan=",
    ),),
    # Apply to an exhausted-loop descendant to overlap ripening with the final ordinary tree.
    "supply-trigger-one": ((
        "view.turn>=100&&view.plants.is_empty(){self.scarce_plan=",
        "view.turn>=100&&view.plants.len()<=1{self.scarce_plan=",
    ),),
    # Follow-on to the exhausted loop: after the first crop is planted, release the mother too.
    "supply-release-mother-after-crop": ((
        "fn scarce_protected_tree(&self)->Option<Cell>{self.scarce_plan.and_then",
        "fn scarce_protected_tree(&self)->Option<Cell>{if self.scarce_plan.is_some_and(|plan|"
        "plan.crop.is_some()){return None;}self.scarce_plan.and_then",
    ),),
    # Convert existing banked fruit before the final two trees disappear, allowing growth to
    # overlap their conversion.  This creates no farmer, protected tree, or harvest detour.
    "preseed-low-supply": ((
        "if carried>0&&is_adjacent(unit.cell,view.shacks[0]){out.extend("
        "Self::bank_candidates(view,unit));}if unit.free_capacity()<=0",
        "if carried>0&&is_adjacent(unit.cell,view.shacks[0]){out.extend("
        "Self::bank_candidates(view,unit));}if safe_regeneration&&carried==0&&view.turn>=100&&"
        "view.plants.len()<=2&&view.units.iter().filter(|unit|unit.player==0).count()>=2&&"
        "is_adjacent(unit.cell,view.shacks[0])&&view.plant_at(unit.cell).is_none(){for(priority,"
        "kind)in Self::inventory_fruits(view).into_iter().enumerate(){out.push(Candidate{command:"
        "format!(\"PICK {} {}\",unit.id,kind.as_str()),score:7500.0-priority as f64,target:"
        "Target::Cell(unit.cell),});}}if unit.free_capacity()<=0",
    ),),
    # Score-state isolation applied to the generated preseed descendant: extending supply is a
    # variance-seeking action only while behind; equal/ahead states retain exact live selection.
    "preseed-behind-only": ((
        "if safe_regeneration&&carried==0&&view.turn>=100&&view.plants.len()<=2&&",
        "if safe_regeneration&&carried==0&&view.turn>=100&&view.plants.len()<=2&&score("
        "&view.inventories[0])<score(&view.inventories[1])&&",
    ),),
    # Score-state ablation: remove the live behind-and-low-supply early endgame switch while
    # retaining the unconditional turn-250 endgame.  This measures whether asymmetry is already
    # a productive baseline feature before layering more lead/deficit branches.
    "score-blind-endgame": ((
        "fn endgame(view:&GameState)->bool{view.turn>250||(view.plants.len()<=4&&score("
        "&view.inventories[0])<score(&view.inventories[1]))}",
        "fn endgame(view:&GameState)->bool{view.turn>250}",
    ),),
    # Follow-on to the one-generation pulse: only the fast banana cycle is economical enough to
    # test; other fruit continues through the exact live policy.
    "supply-banana-only": (
        (
            "[PlantKind::Banana,PlantKind::Plum,PlantKind::Lemon,PlantKind::Apple,]"
            ".into_iter().find(|kind|view.inventories[0][kind.item_index()]>0)",
            "[PlantKind::Banana].into_iter().find(|kind|view.inventories[0]"
            "[kind.item_index()]>0)",
        ),
        (
            "plant.health>0&&plant.fruits>0&&distance.contains_key(&plant.cell)",
            "plant.kind==PlantKind::Banana&&plant.health>0&&plant.fruits>0&&"
            "distance.contains_key(&plant.cell)",
        ),
    ),
    # Follow-on to the banana pulse: once the crop exists, claim the ripe mother before the
    # size-1 crop so the opponent is not handed the high-value half of the pulse.
    "supply-liquidate-mother-first": ((
        "fn scarce_crop(&self)->Option<Cell>{self.scarce_plan.and_then(|plan|plan.crop)}",
        "fn scarce_crop(&self)->Option<Cell>{self.scarce_plan.and_then(|plan|plan.crop.and_then("
        "|_|match plan.intent{ScarceIntent::TendMother{mother,..}=>Some(mother),_=>None,}))}",
    ),),
    "focus-bonus-off": ((
        "score+=900.0/(1+opponent_distance)as f64;",
        "score+=0.0/(1+opponent_distance)as f64;",
    ),),
    # Preserve denial for a worker that can convert it efficiently.  The original starter is
    # chop-1/carry-1; capability checks are robust to seat-dependent unit ids and also avoid
    # forcing a rare fallback-trained 1/1 worker onto denial duty.
    "focus-bonus-capable-only": ((
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{",
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2&&"
        "(unit.stats.chop_power>1||unit.stats.carry_capacity>1){",
    ),),
    # Preserve the live focus bonus except in the measured low-supply failure mode: another
    # bank-capable worker can arrive, fell the current health, and return home strictly sooner.
    # This is a static single-worker estimate, matching the behavior-neutral telemetry gate.
    "focus-bank-race-filter": ((
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{let opponent_distance="
        "manhattan(plant.cell,view.shacks[1]);score+=900.0/(1+opponent_distance)as f64;}",
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2&&(view.plants.len()>4||!view.units"
        ".iter().filter(|opponent|opponent.player==1&&opponent.stats.chop_power>0&&opponent."
        "free_capacity()>0).any(|opponent|{let opponent_from=bfs_distances(&view.walkable,&["
        "opponent.cell]);let opponent_doors:Vec<Cell>=ortho_neighbors(view.shacks[1]).into_iter()"
        ".filter(|cell|view.walkable.contains(cell)).collect();let opponent_home=bfs_distances("
        "&view.walkable,&opponent_doors);let(Some(to_tree),Some(to_home))=(opponent_from.get("
        "&plant.cell),opponent_home.get(&plant.cell))else{return false;};let opponent_turns="
        "Self::ceil_div(*to_tree,opponent.stats.movement_speed)+Self::ceil_div(plant.health.max(1)"
        ",opponent.stats.chop_power)+Self::ceil_div(*to_home,opponent.stats.movement_speed)+1;"
        "opponent_turns<turns})){let opponent_distance=manhattan(plant.cell,view.shacks[1]);"
        "score+=900.0/(1+opponent_distance)as f64;}",
    ),),
    # Strong discriminator for the same narrow cell: remove the focus-tree candidate entirely
    # when the opponent's static bank completion is strictly faster.  If this is harmful, the
    # telemetry's single-worker race model is not sufficient to drive selection.
    "focus-bank-race-reject": ((
        "let mut score=1000.0*wood as f64/turns as f64;if Some(plant.kind)==type_to_cut&&"
        "opponent_trolls<=2{",
        "let mut score=1000.0*wood as f64/turns as f64;if view.plants.len()<=4&&Some(plant.kind)"
        "==type_to_cut&&opponent_trolls<=2&&view.units.iter().filter(|opponent|opponent.player"
        "==1&&opponent.stats.chop_power>0&&opponent.free_capacity()>0).any(|opponent|{let "
        "opponent_from=bfs_distances(&view.walkable,&[opponent.cell]);let opponent_doors:Vec<Cell>"
        "=ortho_neighbors(view.shacks[1]).into_iter().filter(|cell|view.walkable.contains(cell))"
        ".collect();let opponent_home=bfs_distances(&view.walkable,&opponent_doors);let(Some("
        "to_tree),Some(to_home))=(opponent_from.get(&plant.cell),opponent_home.get(&plant.cell))"
        "else{return false;};Self::ceil_div(*to_tree,opponent.stats.movement_speed)+Self::"
        "ceil_div(plant.health.max(1),opponent.stats.chop_power)+Self::ceil_div(*to_home,opponent"
        ".stats.movement_speed)+1<turns}){continue;}if Some(plant.kind)==type_to_cut&&"
        "opponent_trolls<=2{",
    ),),
    # Before the opponent's first train, aim the existing denial bonus at whichever of PLUM or
    # LEMON is currently scarcer in its bank.  Restore the immutable map-derived focus after
    # selection so the entire post-training policy remains exact live behavior.
    "dynamic-training-focus": (
        (
            "self.ensure_opening(view);self.reconcile_scarce_plan(view);",
            "self.ensure_opening(view);let fixed_type_to_cut=self.type_to_cut;if view.units.iter()"
            ".filter(|unit|unit.player==1).count()<2{self.type_to_cut=Some(if view.inventories[1]"
            "[LEMON]<=view.inventories[1][PLUM]{PlantKind::Lemon}else{PlantKind::Plum});}self."
            "reconcile_scarce_plan(view);",
        ),
        (
            "if let Some(farmer_id)=scarce_farmer_id{self.regeneration_commitments.remove("
            "&farmer_id);}out.extend(selected);if out.is_empty(){out.push(\"WAIT\".to_string());}out}",
            "if let Some(farmer_id)=scarce_farmer_id{self.regeneration_commitments.remove("
            "&farmer_id);}out.extend(selected);if out.is_empty(){out.push(\"WAIT\".to_string());}"
            "self.type_to_cut=fixed_type_to_cut;out}",
        ),
    ),
    # Comparative-advantage ablation: force the normal two-worker case through the live greedy
    # fallback.  A loss demonstrates that the existing exhaustive pair assignment is already
    # carrying this direction and should not be replaced by role-first heuristics.
    "greedy-two-unit-assignment": ((
        "if ids.len()==2{let mut best_score=f64::NEG_INFINITY;",
        "if false&&ids.len()==2{let mut best_score=f64::NEG_INFINITY;",
    ),),
    # High-risk workforce discriminator: train a cheap carry-2/harvest-1 seed hand first, then a
    # dedicated (2,2,0,2) wood worker.  This deliberately tests the full sequence rather than
    # another isolated opening constant; the live two-worker cap remains the control.
    "harvest-hand-then-wood-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==1{Stats{movement_speed:1,carry_capacity:2,harvest_power:1,chop_power:0}}"
            "else if own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,"
            "chop_power:2}}else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
    ),
    # Census-derived scale discriminator: four of the current top five repeatedly train a
    # harvest-capable chopper, while exact live never does.  Test the smallest affordable
    # version first, then add the live-style dedicated wood worker as unit three.
    "hybrid-then-wood-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==1{Stats{movement_speed:2,carry_capacity:2,harvest_power:1,chop_power:2}}"
            "else if own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,"
            "chop_power:2}}else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
    ),
    # Complete the census-derived sequence instead of merely changing the second worker.  While
    # only two workers exist, reuse the opening collector for both of them so PLUM/LEMON/IRON are
    # deliberately banked until the dedicated third chopper can actually be trained.
    "hybrid-funded-third-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==1{Stats{movement_speed:2,carry_capacity:2,harvest_power:1,chop_power:2}}"
            "else if own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,"
            "chop_power:2}}else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
        (
            "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
            "let early=!self.opening_abandoned&&my_units.len()<3&&!train_now;",
        ),
    ),
    # Preserve the promoted opening and its selected worker specification exactly.  A third
    # worker is allowed only when ordinary play has already accumulated its complete cost;
    # unlike the rejected macro variants, this adds no harvest role and keeps the two-worker
    # collector gate unchanged, so it never hoards deliberately for expansion.
    "surplus-third-worker": ((
        "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
        "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
    ),),
    # The exact opening remains untouched.  If normal two-worker play later banks the complete
    # cost of a modest 2/2/0/2 wood worker, spend that surplus; do not keep the opening collector
    # active and do not substitute a harvest-capable second worker.
    "surplus-third-wood-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}}"
            "else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
    ),
    # A narrower funding architecture than the rejected hybrid-funded branch: preserve the live
    # second worker and keep it on the normal planner, while only the weak starter reuses the
    # opening collector until a 2/2/0/2 third worker is paid.  Collection stops on the train turn.
    "starter-funded-third-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}}"
            "else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
        (
            "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
            "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;let "
            "third_funding_id=(!self.opening_abandoned&&my_units.len()==2&&!train_now).then(||"
            "my_units.iter().map(|unit|unit.id).min()).flatten();",
        ),
        (
            "}else if early{MoisanBot::early_candidates(view,unit,desired)}",
            "}else if early||third_funding_id==Some(unit.id){MoisanBot::early_candidates("
            "view,unit,desired)}",
        ),
    ),
    # Kill test for the workforce branch: target the cheapest useful wood worker and cap the
    # starter's funding detour at turn 25.  If even this cannot train or improve, the normal
    # stall horizon is too short for a third-worker bootstrap from the promoted economy.
    "bounded-minimal-third-worker": (
        (
            "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}",
            "if n>=3||TOTAL_TURNS-view.turn<=20{return false;}",
        ),
        (
            "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll);",
            "let own_count=view.units.iter().filter(|unit|unit.player==0).count();let desired=if "
            "own_count==2{Stats{movement_speed:1,carry_capacity:1,harvest_power:0,chop_power:1}}"
            "else{self.desired_second.map(|objective|objective.stats).unwrap_or_else("
            "Self::fallback_second_troll)};",
        ),
        (
            "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;",
            "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;let "
            "third_funding_id=(!self.opening_abandoned&&my_units.len()==2&&!train_now&&"
            "view.turn<=25).then(||my_units.iter().map(|unit|unit.id).min()).flatten();",
        ),
        (
            "}else if early{MoisanBot::early_candidates(view,unit,desired)}",
            "}else if early||third_funding_id==Some(unit.id){MoisanBot::early_candidates("
            "view,unit,desired)}",
        ),
    ),
    # Exclusive-geometry discriminator: keep enemy ETA, worker-speed, and orchard behavior exact,
    # but admit mother cells two steps closer to the enemy door than the live >=14 constraint.
    "secure-orchard-door12": ((
        "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),12,false,14,2,",
        "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),12,false,12,2,",
    ),),
    # Existing coverage-only policy boundary: still requires an enemy-distant, alternate-route
    # mother, but admits slower workers and the broader >=11 enemy-door geometry.
    "secure-orchard-coverage": ((
        "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),12,false,14,2,",
        "YamoBot::tuned_carry_regeneration_transit_idle_harvest(),8,false,11,1,",
    ),),
    # Motion discriminator: the live bot already remembers selected tree targets but assigns
    # them zero value.  A small bonus tests whether the measured A->B->A reversals are costly
    # target flaps without turning the target into an overriding persistent commitment.
    "tree-target-bonus25": ((
        "bot.idle_harvest=true;bot}",
        "bot.idle_harvest=true;bot.tree_target_bonus=25;bot}",
    ),),
    # Ten one-field training-policy ideas.  Keeping every replacement inside the exact live
    # TUNED_CARRY block prevents similarly named parked policies from changing accidentally.
    "train-prefer-carry3": training_policy_replacement(
        "preferred_min_carry:2", "preferred_min_carry:3"
    ),
    "train-cap-carry2": training_policy_replacement(
        "max_carry_capacity:3", "max_carry_capacity:2"
    ),
    "train-prefer-chop2": training_policy_replacement(
        "preferred_min_chop:1", "preferred_min_chop:2"
    ),
    "train-cap-chop2": training_policy_replacement(
        "max_chop_power:3", "max_chop_power:2"
    ),
    "train-require-carry2": training_policy_replacement(
        "require_preferred:false", "require_preferred:true"
    ),
    "train-extra-eta8": training_policy_replacement("max_extra_eta:15", "max_extra_eta:8"),
    "train-extra-eta25": training_policy_replacement(
        "max_extra_eta:15", "max_extra_eta:25"
    ),
    "train-deadline25": training_policy_replacement(
        "hard_train_turn:35", "hard_train_turn:25"
    ),
    "train-deadline45": training_policy_replacement(
        "hard_train_turn:35", "hard_train_turn:45"
    ),
    "train-prefer-movement-ties": training_policy_replacement(
        "prefer_movement_ties:false", "prefer_movement_ties:true"
    ),
}


def make_variant(source: str, name: str) -> str:
    if name == "farm-first-orchard":
        return make_farm_first_orchard(source)
    if name == "adaptive-max-bank-hybrid":
        return make_adaptive_max_bank_hybrid(source)
    if name == "adaptive-max-bank-first-only":
        return make_adaptive_max_bank_first_only(source)
    if name == "adaptive-max-bank-first-hp0":
        return make_adaptive_max_bank_first_hp0(source)
    if name == "adaptive-max-bank-surplus":
        return make_adaptive_max_bank_surplus(source)
    if name == "adaptive-max-bank-mixed-surplus":
        return make_adaptive_max_bank_mixed_surplus(source)
    if name == "adaptive-max-bank-cell-122":
        return make_adaptive_max_bank_cell_122(source)
    if name == "adaptive-max-bank-cell-122-carry3":
        return make_adaptive_max_bank_cell_122_carry3(source)
    if name == "adaptive-max-bank-cell-122-carry3-hp0":
        return make_adaptive_max_bank_cell_122_carry3_harvest(source, 0)
    if name == "adaptive-max-bank-cell-122-carry3-hp1":
        return make_adaptive_max_bank_cell_122_carry3_harvest(source, 1)
    result = source
    for before, after in VARIANTS[name]:
        count = result.count(before)
        if count != 1:
            raise RuntimeError(f"expected one {name!r} replacement site, found {count}")
        result = result.replace(before, after, 1)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=sorted(VARIANTS))
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    original = args.source.read_text()
    candidate = make_variant(original, args.variant)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)
    digest = hashlib.sha256(candidate.encode()).hexdigest()
    args.output.with_name(args.output.name + ".sha256").write_text(
        f"{digest}  {args.output.name}\n"
    )
    print(f"generated {args.variant}: {len(candidate)} bytes -> {args.output}")
    print(f"sha256 {digest}")


if __name__ == "__main__":
    main()
