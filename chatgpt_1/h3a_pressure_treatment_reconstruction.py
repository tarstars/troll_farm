#!/usr/bin/env python3
"""Reconstruct and exhaustively classify the archived Phase-21 dual-value treatment.

This task is source archaeology only. It reads frozen repository artifacts, proves exact
fallback↔treatment equality, compiles both sources, and emits a compact deterministic result.
It never writes an existing source, creates a policy arm, or reads game/map data.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
FALLBACK = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
TREATMENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-opponent-crop-dual-value-e6-slim.min.rs"
)
SIDECAR = TREATMENT.with_name(TREATMENT.name + ".sha256")
FULL_PARENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-preseed-orchard-coverage.min.rs"
)

FALLBACK_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
TREATMENT_SHA256 = "083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf"
FULL_PARENT_SHA256 = "da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9"


@dataclass(frozen=True)
class Edit:
    name: str
    category: str
    before: str
    after: str
    classification: tuple[str, ...]

    def result_row(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "before_sha256": digest_text(self.before),
            "after_sha256": digest_text(self.after),
            "before_bytes": len(self.before.encode()),
            "after_bytes": len(self.after.encode()),
            "delta_bytes": len(self.after.encode()) - len(self.before.encode()),
            "classification": list(self.classification),
        }


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(text: str, before: str, after: str, label: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"{label}: expected one anchor, found {count}")
    return text.replace(before, after, 1)


PROVENANCE_METHODS = (
    "fn reconcile_opponent_crops(&mut self,view:&GameState){"
    "let current:BTreeSet<Cell>=view.plants.iter().filter(|plant|plant.health>0)"
    ".map(|plant|plant.cell).collect();if self.plant_history_initialized{"
    "for cell in current.difference(&self.previous_plants){"
    "if!self.own_plant_attempts.contains(cell){self.opponent_crops.insert(*cell);}}"
    "self.opponent_crops.retain(|cell|current.contains(cell));}else{"
    "self.plant_history_initialized=true;}self.previous_plants=current;"
    "self.own_plant_attempts.clear();}"
    "fn remember_own_plant_attempts(&mut self,view:&GameState,commands:&[String]){"
    "for command in commands{let fields:Vec<_>=command.split_whitespace().collect();"
    "if fields.first()!=Some(&\"PLANT\"){continue;}let Some(unit)=fields.get(1)"
    ".and_then(|id|id.parse().ok()).and_then(|id|view.unit(id))"
    ".filter(|unit|unit.player==0)else{continue;};"
    "self.own_plant_attempts.insert(unit.cell);}}"
    "fn apply_opponent_crop_dual_value(&self,view:&GameState,unit:&Unit,"
    "candidates:&mut[Candidate]){if self.opponent_crops.is_empty(){return;}"
    "let distance=bfs_distances(&view.walkable,&[unit.cell]);for candidate in candidates{"
    "let Target::Tree(cell)=candidate.target else{continue;};"
    "if!self.opponent_crops.contains(&cell){continue;}"
    "let Some(cells)=distance.get(&cell)else{continue;};"
    "let eta=MoisanBot::ceil_div(*cells,unit.stats.movement_speed);"
    "if eta<=6{candidate.score+=candidate.score;}}}"
)

BASE_RECONCILE = "fn reconcile_regeneration_commitments(&mut self,view:&GameState)"

EDITS: tuple[Edit, ...] = (
    Edit(
        name="add_provenance_state_fields",
        category="provenance",
        before="external_protected_tree:Option<Cell>,}",
        after=(
            "external_protected_tree:Option<Cell>,plant_history_initialized:bool,"
            "previous_plants:BTreeSet<Cell>,own_plant_attempts:BTreeSet<Cell>,"
            "opponent_crops:BTreeSet<Cell>,}"
        ),
        classification=(
            "adds only plant-history initialization, prior live-plant set, own-attempt set,"
            " and opponent-crop set",
        ),
    ),
    Edit(
        name="initialize_provenance_state",
        category="provenance",
        before=(
            "external_protected_tree:None,}}"
            "pub fn tuned_carry_regeneration_transit_idle_harvest"
        ),
        after=(
            "external_protected_tree:None,plant_history_initialized:false,"
            "previous_plants:BTreeSet::new(),own_plant_attempts:BTreeSet::new(),"
            "opponent_crops:BTreeSet::new(),}}"
            "pub fn tuned_carry_regeneration_transit_idle_harvest"
        ),
        classification=("initializes only the four provenance fields",),
    ),
    Edit(
        name="add_provenance_and_dual_value_methods",
        category="provenance_and_scoring",
        before=BASE_RECONCILE,
        after=PROVENANCE_METHODS + BASE_RECONCILE,
        classification=(
            "opponent crop = newly appeared live plant not preceded by our PLANT attempt",
            "tracked opponent crops are retained only while live",
            "eligible target class is existing Target::Tree only",
            "eligibility requires tracked opponent-crop provenance",
            "ETA uses existing BFS distance and ceil_div by movement speed",
            "ETA threshold is exactly <=6",
            "score operation is exactly candidate.score += candidate.score (1:1 dual value)",
        ),
    ),
    Edit(
        name="reconcile_provenance_before_existing_opening_logic",
        category="provenance_lifecycle",
        before=(
            "fn commands(&mut self,view:&GameState)->Vec<String>{"
            "self.reconcile_regeneration_commitments(view);self.ensure_opening(view);"
        ),
        after=(
            "fn commands(&mut self,view:&GameState)->Vec<String>{"
            "self.reconcile_opponent_crops(view);"
            "self.reconcile_regeneration_commitments(view);self.ensure_opening(view);"
        ),
        classification=(
            "adds one provenance reconciliation call before unchanged resident opening logic",
        ),
    ),
    Edit(
        name="apply_dual_value_to_existing_candidates",
        category="scoring_hook",
        before=(
            "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)};"
            "if endgame&&self.idle_harvest"
        ),
        after=(
            "self.persistent_regeneration,protected_tree,self.opponent_eta_penalty,)};"
            "self.apply_opponent_crop_dual_value(view,unit,&mut candidates);"
            "if endgame&&self.idle_harvest"
        ),
        classification=(
            "applies only to the already-generated candidate vector",
            "does not add a target, command, commitment, harvest rewrite, or scheduler branch",
        ),
    ),
    Edit(
        name="remember_main_loop_own_plant_attempts",
        category="provenance_lifecycle",
        before=(
            "MoisanBot::resolve_move_conflicts(view,&mut selected);"
            "self.remember_selected_regeneration(&selected);out.extend(selected);"
        ),
        after=(
            "MoisanBot::resolve_move_conflicts(view,&mut selected);"
            "self.remember_selected_regeneration(&selected);"
            "self.remember_own_plant_attempts(view,&selected);out.extend(selected);"
        ),
        classification=(
            "records already-selected own PLANT commands after unchanged conflict resolution",
        ),
    ),
    Edit(
        name="remember_orchard_wrapper_own_plant_attempts",
        category="provenance_lifecycle",
        before="&BTreeSet::from([geometry.mother]),);commands}}}",
        after=(
            "&BTreeSet::from([geometry.mother]),);"
            "self.inner.remember_own_plant_attempts(view,&commands);commands}}}"
        ),
        classification=(
            "records already-emitted wrapper PLANT commands; does not alter those commands",
        ),
    ),
)


def apply_edits(fallback: str) -> str:
    result = fallback
    for edit in EDITS:
        result = replace_once(result, edit.before, edit.after, edit.name)
    return result


def remove_edits(treatment: str) -> str:
    result = treatment
    for edit in reversed(EDITS):
        result = replace_once(result, edit.after, edit.before, f"inverse:{edit.name}")
    return result


def ceil_div(value: int, divisor: int) -> int:
    if divisor <= 0:
        raise ValueError("movement speed must be positive")
    return (value + divisor - 1) // divisor


def dual_value_score(
    score: float,
    *,
    tracked_opponent_crop: bool,
    tree_target: bool,
    reachable_distance_cells: int | None,
    movement_speed: int,
) -> float:
    """Pure fixture for the exact inserted eligibility/ETA/score semantics."""
    if not tracked_opponent_crop or not tree_target or reachable_distance_cells is None:
        return score
    eta = ceil_div(reachable_distance_cells, movement_speed)
    return score + score if eta <= 6 else score


def verify_semantics() -> dict[str, Any]:
    required = {
        "provenance_new_plant": "current.difference(&self.previous_plants)",
        "exclude_own_attempt": "!self.own_plant_attempts.contains(cell)",
        "retain_live_only": "self.opponent_crops.retain(|cell|current.contains(cell))",
        "existing_tree_targets_only": "let Target::Tree(cell)=candidate.target",
        "tracked_provenance_required": "!self.opponent_crops.contains(&cell)",
        "bfs_distance": "bfs_distances(&view.walkable,&[unit.cell])",
        "ceil_div_eta": "MoisanBot::ceil_div(*cells,unit.stats.movement_speed)",
        "eta_threshold": "if eta<=6",
        "one_to_one_score": "candidate.score+=candidate.score",
    }
    missing = [name for name, text in required.items() if text not in PROVENANCE_METHODS]
    if missing:
        raise ValueError(f"semantics fragments missing: {missing}")

    prohibited = {
        "fixed_additive_bonus": "candidate.score+=100.0",
        "new_target_constructor": "Candidate{",
        "harvest_rewrite": "HARVEST ",
        "commitment": "commitment",
        "scheduler_mode": "mode",
    }
    present = [name for name, text in prohibited.items() if text in PROVENANCE_METHODS]
    if present:
        raise ValueError(f"prohibited semantics present: {present}")

    fixtures = {
        "eligible_eta_6": dual_value_score(
            12.5,
            tracked_opponent_crop=True,
            tree_target=True,
            reachable_distance_cells=12,
            movement_speed=2,
        ),
        "ineligible_eta_7": dual_value_score(
            12.5,
            tracked_opponent_crop=True,
            tree_target=True,
            reachable_distance_cells=13,
            movement_speed=2,
        ),
        "ineligible_untracked": dual_value_score(
            12.5,
            tracked_opponent_crop=False,
            tree_target=True,
            reachable_distance_cells=1,
            movement_speed=1,
        ),
        "ineligible_non_tree": dual_value_score(
            12.5,
            tracked_opponent_crop=True,
            tree_target=False,
            reachable_distance_cells=1,
            movement_speed=1,
        ),
        "ineligible_unreachable": dual_value_score(
            12.5,
            tracked_opponent_crop=True,
            tree_target=True,
            reachable_distance_cells=None,
            movement_speed=1,
        ),
    }
    expected = {
        "eligible_eta_6": 25.0,
        "ineligible_eta_7": 12.5,
        "ineligible_untracked": 12.5,
        "ineligible_non_tree": 12.5,
        "ineligible_unreachable": 12.5,
    }
    if fixtures != expected:
        raise ValueError(f"eligibility fixture mismatch: {fixtures} != {expected}")
    return {
        "required_fragments": sorted(required),
        "prohibited_fragments_absent": sorted(prohibited),
        "fixtures": fixtures,
    }


def compile_artifact(source: Path, output: Path) -> dict[str, Any]:
    rustc = shutil.which("rustc")
    if rustc is None:
        raise RuntimeError("rustc is unavailable")
    command = [rustc, "--edition=2021", "-O", str(source), "-o", str(output)]
    completed = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"compile failed for {source}:\n{completed.stdout}\n{completed.stderr}"
        )
    return {
        "source": str(source.relative_to(REPO)),
        "command": command,
        "output_sha256": digest_file(output),
        "output_bytes": output.stat().st_size,
    }


def archived_generator_output() -> str:
    from cgauto.make_opponent_crop_dual_value_candidate import make_candidate

    parent = FULL_PARENT.read_text()
    if digest_text(parent) != FULL_PARENT_SHA256:
        raise ValueError("full parent SHA-256 mismatch")
    return make_candidate(parent)


def sidecar_digest(path: Path) -> str:
    fields = path.read_text().strip().split()
    if not fields:
        raise ValueError("empty treatment sidecar")
    return fields[0]


def analyze(*, compile_sources: bool = True) -> dict[str, Any]:
    fallback = FALLBACK.read_text()
    treatment = TREATMENT.read_text()

    hashes = {
        "fallback": digest_text(fallback),
        "treatment": digest_text(treatment),
        "sidecar": sidecar_digest(SIDECAR),
        "full_parent": digest_file(FULL_PARENT),
    }
    expected = {
        "fallback": FALLBACK_SHA256,
        "treatment": TREATMENT_SHA256,
        "sidecar": TREATMENT_SHA256,
        "full_parent": FULL_PARENT_SHA256,
    }
    if hashes != expected:
        raise ValueError(f"frozen input hash mismatch: {hashes} != {expected}")

    direct = apply_edits(fallback)
    inverse = remove_edits(treatment)
    archived = archived_generator_output()

    equality = {
        "direct_fallback_to_treatment": direct == treatment,
        "inverse_treatment_to_fallback": inverse == fallback,
        "archived_generator_to_treatment": archived == treatment,
        "repeated_direct_output": apply_edits(fallback) == direct,
        "repeated_inverse_output": remove_edits(treatment) == inverse,
    }
    if not all(equality.values()):
        raise ValueError(f"exact reconstruction failed: {equality}")

    semantics = verify_semantics()
    compile_results: list[dict[str, Any]] = []
    if compile_sources:
        with tempfile.TemporaryDirectory(prefix="h3a-reconstruct-") as directory:
            root = Path(directory)
            compile_results.append(
                compile_artifact(FALLBACK, root / "fallback")
            )
            compile_results.append(
                compile_artifact(TREATMENT, root / "treatment")
            )

    return {
        "schema": "troll-farm-h3a-pressure-treatment-reconstruction-v1",
        "verdict": "TREATMENT_REPRODUCIBLE",
        "inputs": {
            "fallback_path": str(FALLBACK.relative_to(REPO)),
            "fallback_sha256": FALLBACK_SHA256,
            "treatment_path": str(TREATMENT.relative_to(REPO)),
            "treatment_sha256": TREATMENT_SHA256,
            "sidecar_path": str(SIDECAR.relative_to(REPO)),
            "full_parent_path": str(FULL_PARENT.relative_to(REPO)),
            "full_parent_sha256": FULL_PARENT_SHA256,
        },
        "equality": equality,
        "edits": [edit.result_row() for edit in EDITS],
        "edit_count": len(EDITS),
        "total_delta_bytes": len(treatment.encode()) - len(fallback.encode()),
        "semantics": semantics,
        "compilation": compile_results,
        "classification": {
            "provenance": True,
            "original_tree_target_eligibility": True,
            "original_eta_threshold_6": True,
            "score_operation_candidate_plus_equal_candidate": True,
            "new_multiplier": False,
            "new_eta": False,
            "new_target": False,
            "new_commitment": False,
            "harvest_rewrite": False,
            "scheduler_change": False,
            "unrelated_bytes": False,
        },
        "panel_authorized": False,
        "arena_or_platform_action": False,
    }


def self_test() -> None:
    fixture = "A" + EDITS[0].before + "B"
    transformed = replace_once(
        fixture, EDITS[0].before, EDITS[0].after, "fixture"
    )
    assert replace_once(
        transformed, EDITS[0].after, EDITS[0].before, "inverse fixture"
    ) == fixture
    assert dual_value_score(
        3.0,
        tracked_opponent_crop=True,
        tree_target=True,
        reachable_distance_cells=6,
        movement_speed=1,
    ) == 6.0
    assert dual_value_score(
        3.0,
        tracked_opponent_crop=True,
        tree_target=True,
        reachable_distance_cells=7,
        movement_speed=1,
    ) == 3.0
    semantics = verify_semantics()
    assert semantics["fixtures"]["eligible_eta_6"] == 25.0
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--skip-compile",
        action="store_true",
        help="diagnostic only; canonical result must compile both frozen artifacts",
    )
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    result = analyze(compile_sources=not args.skip_compile)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "edit_count": result["edit_count"],
                "total_delta_bytes": result["total_delta_bytes"],
                "compiled": len(result["compilation"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
