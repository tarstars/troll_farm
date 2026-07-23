"""Tests for mechanically generated live-agent variants."""

from pathlib import Path

import pytest

from cgauto.make_live_variant import TUNED_CARRY_BLOCK, make_variant

REPO = Path(__file__).resolve().parent.parent


def test_idle_harvest_off_is_one_narrow_replacement() -> None:
    source = "aYamoBot::tuned_carry_regeneration_transit_idle_harvest(),12,false,14,2,z"

    candidate = make_variant(source, "idle-harvest-off")

    assert candidate == "aYamoBot::tuned_carry_regeneration_transit(),12,false,14,2,z"


def test_sparse_farming_on_only_sets_existing_policy_flag() -> None:
    source = (
        "abobot.idle_harvest=true;bot}omega"
        "&&!self.scarce_farming&&candidates.iter()"
    )

    candidate = make_variant(source, "sparse-farming-on")

    assert candidate == (
        "abobot.idle_harvest=true;bot.scarce_farming=true;bot}omega"
        "&&scarce_farmer_id!=Some(unit.id)&&candidates.iter()"
    )


def test_sparse_farming_work_conserving_releases_farmer_to_live_chop_loop() -> None:
    source = (
        "bot.idle_harvest=true;bot}"
        "&&!self.scarce_farming&&candidates.iter()"
        "if plan.crop.is_some(){return Vec::new();}"
        "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
        "self.opponent_eta_penalty,).is_empty(){return Vec::new();}"
    )

    candidate = make_variant(source, "sparse-farming-work-conserving")

    assert "bot.scarce_farming=true" in candidate
    assert "scarce_farmer_id!=Some(unit.id)" in candidate
    assert candidate.count("return Self::main_candidates") == 2
    assert "return Vec::new()" not in candidate


def test_late_supply_loop_waits_for_the_measured_supply_cliff() -> None:
    source = (
        "bot.idle_harvest=true;bot}"
        "&&!self.scarce_farming&&candidates.iter()"
        "if plan.crop.is_some(){return Vec::new();}"
        "if!Self::yamo_chop_candidates(view,unit,type_to_cut,Some(mother),"
        "self.opponent_eta_penalty,).is_empty(){return Vec::new();}"
        "if self.initial_tree_count.is_none(){self.initial_tree_count=Some(view.plants.len());"
        "if self.scarce_farming&&view.plants.len()<=14{self.scarce_plan=view.units.iter()"
        ".filter(|unit|unit.player==0).min_by_key(|unit|unit.id).map(|unit|ScarcePlan{"
        "farmer_id:unit.id,intent:ScarceIntent::NeedSeed,crop:None,});}}"
    )

    candidate = make_variant(source, "late-supply-loop")

    assert "bot.scarce_farming=true" in candidate
    assert "scarce_farmer_id!=Some(unit.id)" in candidate
    assert candidate.count("return Self::main_candidates") == 2
    assert "view.turn>=100&&view.plants.len()<=2" in candidate
    assert "view.plants.len()<=14" not in candidate


def test_supply_trigger_empty_only_tightens_late_loop_activation() -> None:
    source = "before view.turn>=100&&view.plants.len()<=2{self.scarce_plan= after"

    candidate = make_variant(source, "supply-trigger-empty")

    assert candidate == (
        "before view.turn>=100&&view.plants.is_empty(){self.scarce_plan= after"
    )


def test_supply_trigger_one_overlaps_ripening_with_last_tree() -> None:
    source = "before view.turn>=100&&view.plants.is_empty(){self.scarce_plan= after"

    candidate = make_variant(source, "supply-trigger-one")

    assert candidate == (
        "before view.turn>=100&&view.plants.len()<=1{self.scarce_plan= after"
    )


def test_supply_pulse_releases_mother_after_first_crop() -> None:
    source = (
        "before fn scarce_protected_tree(&self)->Option<Cell>{"
        "self.scarce_plan.and_then after"
    )

    candidate = make_variant(source, "supply-release-mother-after-crop")

    assert "plan.crop.is_some()){return None;}" in candidate
    assert candidate.endswith("self.scarce_plan.and_then after")


def test_preseed_low_supply_adds_no_harvest_or_protection_path() -> None:
    source = (
        "before if carried>0&&is_adjacent(unit.cell,view.shacks[0]){out.extend("
        "Self::bank_candidates(view,unit));}if unit.free_capacity()<=0 after"
    )

    candidate = make_variant(source, "preseed-low-supply")

    assert "view.turn>=100&&view.plants.len()<=2" in candidate
    assert "format!(\"PICK {} {}\",unit.id,kind.as_str())" in candidate
    assert "HARVEST" not in candidate
    assert "scarce" not in candidate


def test_preseed_behind_only_adds_one_score_state_gate() -> None:
    source = (
        "before if safe_regeneration&&carried==0&&view.turn>=100&&"
        "view.plants.len()<=2&& after"
    )

    candidate = make_variant(source, "preseed-behind-only")

    assert candidate == (
        "before if safe_regeneration&&carried==0&&view.turn>=100&&"
        "view.plants.len()<=2&&score(&view.inventories[0])<"
        "score(&view.inventories[1])&& after"
    )


def test_score_blind_endgame_removes_only_behind_low_supply_switch() -> None:
    source = (
        "before fn endgame(view:&GameState)->bool{view.turn>250||"
        "(view.plants.len()<=4&&score(&view.inventories[0])<"
        "score(&view.inventories[1]))} after"
    )

    candidate = make_variant(source, "score-blind-endgame")

    assert candidate == "before fn endgame(view:&GameState)->bool{view.turn>250} after"


def test_supply_banana_only_rejects_slower_seed_kinds() -> None:
    source = (
        "[PlantKind::Banana,PlantKind::Plum,PlantKind::Lemon,PlantKind::Apple,]"
        ".into_iter().find(|kind|view.inventories[0][kind.item_index()]>0)"
        " plant.health>0&&plant.fruits>0&&distance.contains_key(&plant.cell)"
    )

    candidate = make_variant(source, "supply-banana-only")

    assert "[PlantKind::Banana].into_iter()" in candidate
    assert "plant.kind==PlantKind::Banana" in candidate
    assert "PlantKind::Plum" not in candidate


def test_supply_pulse_liquidates_ripe_mother_before_crop() -> None:
    source = (
        "before fn scarce_crop(&self)->Option<Cell>{"
        "self.scarce_plan.and_then(|plan|plan.crop)} after"
    )

    candidate = make_variant(source, "supply-liquidate-mother-first")

    assert "ScarceIntent::TendMother{mother,..}=>Some(mother)" in candidate
    assert "and_then(|plan|plan.crop)}" not in candidate


def test_focus_bonus_off_keeps_rate_score_and_removes_only_denial_bonus() -> None:
    source = "before score+=900.0/(1+opponent_distance)as f64; after"

    candidate = make_variant(source, "focus-bonus-off")

    assert candidate == "before score+=0.0/(1+opponent_distance)as f64; after"


def test_focus_bonus_capable_only_preserves_denial_for_a_capable_chopper() -> None:
    source = (
        "before if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{"
        "score+=900.0/(1+opponent_distance)as f64;} after"
    )

    candidate = make_variant(source, "focus-bonus-capable-only")

    assert candidate == (
        "before if Some(plant.kind)==type_to_cut&&opponent_trolls<=2&&"
        "(unit.stats.chop_power>1||unit.stats.carry_capacity>1){"
        "score+=900.0/(1+opponent_distance)as f64;} after"
    )


def test_focus_bank_race_filter_is_limited_to_low_supply_focus_bonus() -> None:
    source = (
        "before if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{"
        "let opponent_distance=manhattan(plant.cell,view.shacks[1]);"
        "score+=900.0/(1+opponent_distance)as f64;} after"
    )

    candidate = make_variant(source, "focus-bank-race-filter")

    assert "view.plants.len()>4||" in candidate
    assert "opponent_turns<turns" in candidate
    assert "opponent.stats.chop_power>0" in candidate
    assert "opponent.free_capacity()>0" in candidate
    assert candidate.count("score+=900.0") == 1


def test_focus_bank_race_reject_drops_only_losing_low_supply_focus_tree() -> None:
    source = (
        "before let mut score=1000.0*wood as f64/turns as f64;"
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{ after"
    )

    candidate = make_variant(source, "focus-bank-race-reject")

    assert "view.plants.len()<=4" in candidate
    assert "Some(plant.kind)==type_to_cut" in candidate
    assert "opponent.stats.chop_power>0" in candidate
    assert "<turns}){continue;}" in candidate
    assert candidate.endswith(
        "if Some(plant.kind)==type_to_cut&&opponent_trolls<=2{ after"
    )


def test_dynamic_training_focus_restores_map_focus_after_selection() -> None:
    source = (
        "before self.ensure_opening(view);self.reconcile_scarce_plan(view); middle "
        "if let Some(farmer_id)=scarce_farmer_id{self.regeneration_commitments.remove("
        "&farmer_id);}out.extend(selected);if out.is_empty(){out.push(\"WAIT\".to_string());}out}"
    )

    candidate = make_variant(source, "dynamic-training-focus")

    assert "let fixed_type_to_cut=self.type_to_cut" in candidate
    assert "view.inventories[1][LEMON]<=view.inventories[1][PLUM]" in candidate
    assert "self.type_to_cut=fixed_type_to_cut;out}" in candidate


def test_greedy_assignment_is_a_single_two_worker_joint_solver_ablation() -> None:
    source = "before if ids.len()==2{let mut best_score=f64::NEG_INFINITY; after"

    candidate = make_variant(source, "greedy-two-unit-assignment")

    assert candidate == (
        "before if false&&ids.len()==2{let mut best_score=f64::NEG_INFINITY; after"
    )


def test_harvest_hand_then_wood_worker_expands_cap_and_sequences_roles() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); after"
    )

    candidate = make_variant(source, "harvest-hand-then-wood-worker")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "own_count==1{Stats{movement_speed:1,carry_capacity:2,harvest_power:1" in candidate
    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0" in candidate


def test_hybrid_then_wood_worker_uses_census_role_then_dedicated_chopper() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); after"
    )

    candidate = make_variant(source, "hybrid-then-wood-worker")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "own_count==1{Stats{movement_speed:2,carry_capacity:2,harvest_power:1,chop_power:2}" in candidate
    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}" in candidate


def test_hybrid_funded_third_worker_keeps_opening_collection_active() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); later "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now; after"
    )

    candidate = make_variant(source, "hybrid-funded-third-worker")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "own_count==1{Stats{movement_speed:2,carry_capacity:2,harvest_power:1,chop_power:2}" in candidate
    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}" in candidate
    assert "my_units.len()<3&&!train_now" in candidate


def test_farm_first_orchard_is_a_complete_staged_option() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "farm-first-orchard")

    assert "if n>=4||TOTAL_TURNS" in candidate
    assert "movement_speed:farmer_level(PLUM,2)" in candidate
    assert "carry_capacity:farmer_level(LEMON,3)" in candidate
    assert "harvest_power:farmer_level(APPLE,2)" in candidate
    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2" in candidate
    assert "own_count==3{Stats{movement_speed:2" in candidate
    assert "own_count==2&&view.turn<=100" in candidate
    assert "own_count==3&&view.turn<=180" in candidate
    assert "my_units_count==3&&!farm_ids.contains(&unit.id)" in candidate
    assert "my_units_count>=3&&farm_ids.contains(&unit.id)" in candidate
    assert "PlantKind::Lemon=>3" in candidate
    assert "PlantKind::Plum|PlantKind::Apple=>2" in candidate
    assert "view.turn>=120{PlantKind::Banana}" in candidate
    assert "committed_regeneration&&!early" in candidate
    assert "let has_second=unit_ids.len()>=4" in candidate
    assert len(candidate) < 100_000


def test_adaptive_max_bank_hybrid_is_a_complete_conditional_option() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-hybrid")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "movement_speed:max_level(PLUM,3)" in candidate
    assert "carry_capacity:max_level(LEMON,3)" in candidate
    assert "harvest_power:max_level(APPLE,3)" in candidate
    assert "carry_capacity:max_level(LEMON,4)" in candidate
    assert "harvest_power:max_level(APPLE,1)" in candidate
    assert "view.turn>=66&&view.turn<=125" in candidate
    assert "own_distance.get(&plant.cell)==Some(&0)" in candidate
    assert "let funding=!self.opening_abandoned&&my_units.len()==2" in candidate
    assert "adaptive_hybrid_funding_candidates" in candidate
    assert "let order=if starter{[LEMON,PLUM,APPLE,IRON]}" in candidate
    assert "else{[IRON,PLUM,LEMON,APPLE]}" in candidate
    assert "movement_speed:3,carry_capacity:4,harvest_power:1,chop_power:3" in candidate
    assert "let has_second=unit_ids.len()>=3" in candidate
    assert len(candidate) < 100_000


def test_adaptive_max_bank_first_only_removes_only_the_expansion_stage() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-first-only")

    assert "movement_speed:max_level(PLUM,3)" in candidate
    assert "harvest_power:max_level(APPLE,3)" in candidate
    assert "if n>=2||TOTAL_TURNS" in candidate
    assert "let funding=false;" in candidate
    assert "let has_second=unit_ids.len()>=2" in candidate
    assert "view.turn>=66&&view.turn<=125" in candidate
    assert len(candidate) < 100_000


def test_adaptive_max_bank_first_hp0_removes_unexploited_harvest_only() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-first-hp0")

    assert "movement_speed:max_level(PLUM,3)" in candidate
    assert "carry_capacity:max_level(LEMON,3)" in candidate
    assert "harvest_power:0,chop_power:max_level(IRON,3)" in candidate
    assert "if n>=2||TOTAL_TURNS" in candidate
    assert "let funding=false;" in candidate
    assert len(candidate) < 100_000


def test_adaptive_max_bank_surplus_keeps_expansion_but_removes_hoarding() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-surplus")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "view.turn>=66&&view.turn<=125" in candidate
    assert "later_ready&&useful_private" in candidate
    assert "let funding=false;" in candidate
    assert "let has_second=unit_ids.len()>=3" in candidate


def test_adaptive_mixed_surplus_uses_paid_harvest_without_exclusive_funding() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-mixed-surplus")

    assert "let funding=false;" in candidate
    assert "hybrid_id==Some(unit.id)" in candidate
    assert "hybrid_id==Some(unit.id)&&view.turn<=125" in candidate
    assert "unit.stats.harvest_power>0" in candidate
    assert "for kind in PlantKind::ALL" in candidate
    assert "fruit_candidates(view,unit,kind,-500.0)" in candidate
    assert "candidate.command.starts_with(\"HARVEST \")" in candidate
    assert len(candidate) < 100_000


def test_adaptive_max_bank_cell_122_freezes_a_narrow_turn_one_entry_gate() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-cell-122")

    assert "adaptive_max_bank_stats:Option<Stats>" in candidate
    assert "adaptive_max_bank_stats:None" in candidate
    assert "!self.opening_initialized&&view.turn==1" in candidate
    assert "own_count==1&&max.movement_speed==1" in candidate
    assert "max.carry_capacity==2&&max.harvest_power==2" in candidate
    assert "adaptive_max_bank_stats=Some(max)" in candidate
    assert "adaptive_max_bank_stats.unwrap_or(original_desired)" in candidate
    assert "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}" in candidate
    assert "let has_second=unit_ids.len()>=2;" in candidate
    assert "funding" not in candidate
    assert len(candidate) < 100_000


def test_adaptive_cell_122_carry3_replaces_only_the_delayed_parent_spec() -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, "adaptive-max-bank-cell-122-carry3")

    assert "!self.opening_initialized&&view.turn==1" in candidate
    assert "max.carry_capacity==2&&max.harvest_power==2" in candidate
    assert "original_desired.movement_speed==1" in candidate
    assert "original_desired.carry_capacity==3" in candidate
    assert "adaptive_max_bank_stats.unwrap_or(original_desired)" in candidate
    assert "if n>=2||TOTAL_TURNS-view.turn<=20{return false;}" in candidate
    assert "let has_second=unit_ids.len()>=2;" in candidate
    assert len(candidate) < 100_000


@pytest.mark.parametrize("power", [0, 1])
def test_adaptive_cell_122_carry3_can_ablate_unused_harvest(power: int) -> None:
    source = (
        REPO
        / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs"
    ).read_text()

    candidate = make_variant(source, f"adaptive-max-bank-cell-122-carry3-hp{power}")

    assert "original_desired.movement_speed==1" in candidate
    assert "original_desired.carry_capacity==3" in candidate
    assert f"Stats{{harvest_power:{power},..stats}}" in candidate
    assert "max.carry_capacity==2&&max.harvest_power==2" in candidate
    assert len(candidate) < 100_000


def test_surplus_third_worker_only_relaxes_the_unit_cap() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} after "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;"
    )

    candidate = make_variant(source, "surplus-third-worker")

    assert candidate == (
        "before if n>=3||TOTAL_TURNS-view.turn<=20{return false;} after "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now;"
    )


def test_surplus_third_wood_worker_preserves_the_second_worker_and_collector_gate() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); later "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now; after"
    )

    candidate = make_variant(source, "surplus-third-wood-worker")

    assert "if n>=3||TOTAL_TURNS" in candidate
    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}}" in candidate
    assert "my_units.len()<2&&!train_now" in candidate
    assert "my_units.len()<3" not in candidate
    assert "harvest_power:1" not in candidate


def test_starter_funded_third_worker_keeps_only_the_starter_collecting() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); later "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now; then "
        "}else if early{MoisanBot::early_candidates(view,unit,desired)} after"
    )

    candidate = make_variant(source, "starter-funded-third-worker")

    assert "own_count==2{Stats{movement_speed:2,carry_capacity:2,harvest_power:0,chop_power:2}}" in candidate
    assert "my_units.len()==2&&!train_now" in candidate
    assert "my_units.iter().map(|unit|unit.id).min()" in candidate
    assert "early||third_funding_id==Some(unit.id)" in candidate
    assert "my_units.len()<3" not in candidate


def test_bounded_minimal_third_worker_has_a_hard_funding_deadline() -> None:
    source = (
        "before if n>=2||TOTAL_TURNS-view.turn<=20{return false;} middle "
        "let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else("
        "Self::fallback_second_troll); later "
        "let early=!self.opening_abandoned&&my_units.len()<2&&!train_now; then "
        "}else if early{MoisanBot::early_candidates(view,unit,desired)} after"
    )

    candidate = make_variant(source, "bounded-minimal-third-worker")

    assert "own_count==2{Stats{movement_speed:1,carry_capacity:1,harvest_power:0,chop_power:1}}" in candidate
    assert "my_units.len()==2&&!train_now&&view.turn<=25" in candidate
    assert "early||third_funding_id==Some(unit.id)" in candidate


def test_secure_orchard_door12_only_relaxes_exclusive_geometry() -> None:
    source = (
        "before YamoBot::tuned_carry_regeneration_transit_idle_harvest(),"
        "12,false,14,2, after"
    )

    candidate = make_variant(source, "secure-orchard-door12")

    assert candidate == (
        "before YamoBot::tuned_carry_regeneration_transit_idle_harvest(),"
        "12,false,12,2, after"
    )


def test_secure_orchard_coverage_uses_existing_broader_safe_boundary() -> None:
    source = (
        "before YamoBot::tuned_carry_regeneration_transit_idle_harvest(),"
        "12,false,14,2, after"
    )

    candidate = make_variant(source, "secure-orchard-coverage")

    assert candidate == (
        "before YamoBot::tuned_carry_regeneration_transit_idle_harvest(),"
        "8,false,11,1, after"
    )


def test_tree_target_bonus25_uses_existing_commitment_memory() -> None:
    source = "before bot.idle_harvest=true;bot} after"

    candidate = make_variant(source, "tree-target-bonus25")

    assert candidate == "before bot.idle_harvest=true;bot.tree_target_bonus=25;bot} after"


@pytest.mark.parametrize(
    ("variant", "before", "after"),
    [
        ("train-prefer-carry3", "preferred_min_carry:2", "preferred_min_carry:3"),
        ("train-cap-carry2", "max_carry_capacity:3", "max_carry_capacity:2"),
        ("train-prefer-chop2", "preferred_min_chop:1", "preferred_min_chop:2"),
        ("train-cap-chop2", "max_chop_power:3", "max_chop_power:2"),
        ("train-require-carry2", "require_preferred:false", "require_preferred:true"),
        ("train-extra-eta8", "max_extra_eta:15", "max_extra_eta:8"),
        ("train-extra-eta25", "max_extra_eta:15", "max_extra_eta:25"),
        ("train-deadline25", "hard_train_turn:35", "hard_train_turn:25"),
        ("train-deadline45", "hard_train_turn:35", "hard_train_turn:45"),
        (
            "train-prefer-movement-ties",
            "prefer_movement_ties:false",
            "prefer_movement_ties:true",
        ),
    ],
)
def test_training_variant_changes_one_field_in_live_policy(
    variant: str, before: str, after: str
) -> None:
    candidate = make_variant(TUNED_CARRY_BLOCK, variant)

    assert candidate == TUNED_CARRY_BLOCK.replace(before, after, 1)
    assert before not in candidate
    assert candidate.count(after) == 1


def test_variant_rejects_missing_site() -> None:
    with pytest.raises(RuntimeError, match="found 0"):
        make_variant("fn main() {}", "idle-harvest-off")
