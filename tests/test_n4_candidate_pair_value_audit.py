import importlib.util
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "cgauto/n4_candidate_pair_value_audit.py"
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


def dual_output_fixture():
    return """        #[derive(Clone, Debug)]
        struct Candidate {
            command: String,
            score: f64,
            target: Target,
        }
            opponent_crop_harvest_rewrites: usize,
                    opponent_crop_harvest_rewrites: 0,
            pub fn fresh_harvest_regeneration_telemetry(
                let tree_targets = Self::tree_targets_by_command(&by_id);
                let mut selected = MoisanBot::select(by_id, &view.inventories[0]);
                out.extend(selected);
                if out.is_empty() {
                    out.push("WAIT".to_string());
                }
                self.remember_selected_regeneration(view, &selected);
                self.apply_opponent_crop_harvest_contact(view, &mut selected);
                self.remember_own_plant_attempts(view, &selected);
                if let Some(farmer_id) = scarce_farmer_id {
                    self.regeneration_commitments.remove(&farmer_id);
                }
                out.extend(selected);
                if out.is_empty() {
"""


def assert_probe_accesses(transformed):
    assert transformed.count("N4_LAST_PROBE.with(|slot| {") == 1
    assert transformed.count(
        "N4_LAST_PROBE.with(|slot| *slot.borrow_mut() = None);"
    ) == 1
    assert transformed.count(
        "N4_LAST_PROBE.with(|slot| slot.borrow_mut().take())"
    ) == 1


def assert_inner_outer_ownership(transformed):
    assert "n4_forced_pair: Option<Vec<String>>" in transformed
    assert "self.inner.n4_forced_pair = Some(commands);" in transformed
    assert "let mut selected = self.n4_forced_pair.take()" in transformed
    assert "&self.opponent_crops, &n4_selected_pre, &selected" in transformed
    assert "&self.inner.opponent_crops" not in transformed


def test_instrumentation_uses_unique_live_path_not_generic_tail():
    transformed = n4.instrument_resident(dual_output_fixture())
    assert "pub struct N4CandidateProbe" in transformed
    assert "n4_selected_pre" in transformed
    assert_inner_outer_ownership(transformed)
    assert_probe_accesses(transformed)
    assert transformed.count("out.extend(selected);") == 2
    assert "fn main()" in n4.runner_source()


def test_actual_sacred_source_materializes_once():
    resident = ROOT / "rust/src/d171a_control_resident_snapshot.rs"
    assert n4.sha256_file(resident) == n4.RESIDENT_SHA256
    transformed = n4.instrument_resident(resident.read_text())
    assert_probe_accesses(transformed)
    assert_inner_outer_ownership(transformed)


def test_generated_rust_compiles(tmp_path):
    if shutil.which("cargo") is None:
        pytest.skip("Cargo is unavailable in this runtime")
    resident = ROOT / "rust/src/d171a_control_resident_snapshot.rs"
    instrumented = tmp_path / "n4_instrumented_resident.rs"
    runner = tmp_path / "n4_generated_runner.rs"
    instrumented.write_text(n4.instrument_resident(resident.read_text()))
    runner.write_text(n4.runner_source())
    env = os.environ.copy()
    env.update({
        "N4_INSTRUMENTED_RESIDENT": str(instrumented),
        "N4_GENERATED_RUNNER": str(runner),
        "CARGO_TARGET_DIR": str(tmp_path / "cargo-target"),
    })
    completed = subprocess.run(
        [
            "cargo", "check", "--manifest-path", "rust/Cargo.toml",
            "--bin", "n4_candidate_pair_surface",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr


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
