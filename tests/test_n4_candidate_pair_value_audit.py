import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "cgauto/n4_candidate_pair_value_audit.py"
spec = importlib.util.spec_from_file_location("n4", MODULE_PATH)
n4 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(n4)


def row(seed, seat=0, opp=0, **updates):
    base = {
        "seed": str(seed), "seat": str(seat), "opp": str(opp), "turn": "1",
        "live_full": "WAIT;WAIT", "latency_us": "1000", "pair_count": "2",
        "probe_present": "1", "live_pair_found": "1", "pair_index": "1",
        "is_live": "0", "semantic_distinct": "1", "candidates_blob": "candidate",
        "boundary_bank": "1", "boundary_tree": "0", "boundary_collision": "0",
        "boundary_disappearance": "0", "boundary_route_order": "0",
        "overlap_move_residual": "0", "overlap_threatened_crop": "0",
        "overlap_d163_d168": "0", "overlap_primitive_mutation": "0",
        "overlap_static_option": "0", "terminal_margin_used_for_eligibility": "0",
    }
    base.update({key: str(value) for key, value in updates.items()})
    return base


def full_surface(**updates):
    rows = []
    frozen = {}
    for seed in range(1, n4.EXPECTED_GAMES + 1):
        seat = seed % 2
        opp = seed % 8
        rows.append(row(seed, seat, opp, **updates))
        frozen[(seed, seat, opp, 1)] = ["WAIT", "WAIT"]
    return rows, frozen


def test_instrumentation_is_anchor_exact():
    fixture = """        #[derive(Clone, Debug)]
        struct Candidate {
            command: String,
            score: f64,
            target: Target,
        }
            banana_factory_worker_three_bridge_post_training_commands: usize,
                    banana_factory_worker_three_bridge_post_training_commands: 0,
            pub fn fresh_harvest_regeneration_telemetry(
                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                out.extend(selected);
                if out.is_empty() {
"""
    transformed = n4.instrument_resident(fixture)
    assert "pub struct N4CandidateProbe" in transformed
    assert "n4_force_pair" in transformed
    assert "n4_selected_pre" in transformed
    assert "fn main()" in n4.runner_source()


def test_surface_clears_only_with_all_gates():
    rows, frozen = full_surface()
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "SURFACE_CLEARED_FOR_PHASE_B"
    assert not any(result["hard_closes"].values())


def test_sparse_or_missing_task_is_unidentifiable():
    rows, frozen = full_surface()
    result = n4.analyze_rows(rows[:-1], frozen)
    assert result["verdict"] == "UNIDENTIFIABLE"
    assert result["hard_closes"]["source_or_outcome_integrity_failure"]


def test_reconstruction_mismatch_is_unidentifiable():
    rows, frozen = full_surface()
    rows[0]["live_full"] = "MOVE%201%202%203;WAIT"
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "UNIDENTIFIABLE"
    assert result["hard_closes"]["live_reconstruction_not_exact"]


def test_all_distinct_boundaries_collapsing_to_move_residual_close():
    rows, frozen = full_surface(overlap_move_residual=1)
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "NOT_DISTINCT"
    assert result["hard_closes"]["not_distinct_from_consumed_grammar"]


def test_one_nonoverlap_pair_prevents_global_not_distinct_close():
    rows, frozen = full_surface(overlap_move_residual=1)
    rows[0]["overlap_move_residual"] = "0"
    result = n4.analyze_rows(rows, frozen)
    assert not result["hard_closes"]["not_distinct_from_consumed_grammar"]


def test_outcome_field_cannot_enter_eligibility():
    rows, frozen = full_surface()
    rows[0]["terminal_margin_used_for_eligibility"] = "1"
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "UNIDENTIFIABLE"
    assert result["outcome_influenced_eligibility"]


def test_latency_close():
    rows, frozen = full_surface(latency_us=6000)
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "RUNTIME_CLOSE"


def test_void_probe_or_candidate_blob_is_integrity_failure():
    rows, frozen = full_surface()
    rows[0]["probe_present"] = "0"
    rows[0]["candidates_blob"] = ""
    result = n4.analyze_rows(rows, frozen)
    assert result["verdict"] == "UNIDENTIFIABLE"


def test_percent_roundtrip():
    encoded = "MOVE%201%202%203%3Bnote%7Cvalue"
    assert n4.decode_field(encoded) == "MOVE 1 2 3;note|value"
