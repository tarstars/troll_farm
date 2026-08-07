from __future__ import annotations
import copy, json, subprocess, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.build_decision_evidence_index import build
from cgauto.check_decision_evidence_index import ValidationError, validate_repository

START = "<!-- DECISION-EVIDENCE-JSON"
END = "END-DECISION-EVIDENCE-JSON -->"

def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def git_init_and_commit(repo: Path) -> str:
    """Make `repo` a git repo and commit everything currently in it."""
    if not (repo / ".git").exists():
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "fixture")
    return git(repo, "rev-parse", "HEAD").strip()

def base_record():
    return {
        "schema_version": 2,
        "id": "T1",
        "title": "Fixture",
        "kind": "scientific_decision",
        "status": "closed",
        "decision_date": "2026-07-30",
        "question": "Does the fixture pass?",
        "scope": "Fixture scope.",
        "conclusion": "Yes.",
        "primary_evidence_strength": "panel_causal",
        "claims_ladder_effect": False,
        "cost": {"class": "low", "actual": "fixture"},
        "attempts": ["fixture"],
        "decisive_claims": [{
            "name": "value",
            "display": "+1.0 on 4/4 tasks",
            "population": "four fixture tasks",
            "source": {"path": "evidence.json", "json_pointer": "/value"},
            "evidence_strength": "panel_causal",
            "binding": True,
            "expected_value": 1.0,
        }],
        "textual_evidence": [{
            "claim": "Fixture text.",
            "source": {"path": "source.md", "locator": "lines 1-2"},
        }],
        "does_not_prove": ["Anything outside the fixture."],
        "limitations": ["Synthetic fixture."],
        "relations": [],
        "reopening_conditions": ["New fixture."],
        "discussions": [],
        "constraint_projection": {
            "section": "Fixture",
            "source": {"path": "source.md", "locator": "lines 1-2"},
            "bullet": "Fixture value is +1.0 on 4/4 tasks. [T1]",
        },
        "acceptance": {"state": "proposed", "author": "tester", "reviewer": "tester"},
    }

def write_record(repo: Path, record: dict):
    p = repo / "docs/evidence/records"
    p.mkdir(parents=True, exist_ok=True)
    content = f"# {record.get('id','bad')}\n\n{START}\n{json.dumps(record, indent=2, sort_keys=True)}\n{END}\n"
    (p / f"{record.get('id','bad')}.md").write_text(content)

def make_repo(tmp_path: Path, record=None, build_generated=True) -> Path:
    repo = tmp_path
    (repo / "docs/evidence/discussions").mkdir(parents=True, exist_ok=True)
    (repo / "docs/evidence/generated").mkdir(parents=True, exist_ok=True)
    (repo / "source.md").write_text(
        "Fixture value is +1.0 on 4/4 tasks. [T1]\nFixture text.\n"
    )
    (repo / "evidence.json").write_text(json.dumps({"value": 1.0}))
    sha = git_init_and_commit(repo)
    rec = record or base_record()
    for src in (
        rec["textual_evidence"][0]["source"],
        rec["constraint_projection"]["source"],
        rec["decisive_claims"][0]["source"],
    ):
        src.setdefault("commit", sha)
    pf = rec.get("premise_failure")
    if isinstance(pf, dict) and isinstance(pf.get("source"), dict):
        pf["source"].setdefault("commit", sha)
    write_record(repo, rec)
    if build_generated:
        build(repo)
    return repo

def test_valid_subset_and_deterministic_generation(tmp_path):
    repo = make_repo(tmp_path)
    first = {p.name: p.read_bytes() for p in (repo/"docs/evidence/generated").iterdir()}
    validate_repository(repo, require_pilot=False, check_generated=True)
    build(repo)
    second = {p.name: p.read_bytes() for p in (repo/"docs/evidence/generated").iterdir()}
    assert first == second

def test_registry_is_compact_navigation_projection(tmp_path):
    repo = make_repo(tmp_path)
    text = (repo/"docs/evidence/generated/decision-evidence-index.yaml").read_text()
    assert text.count("\n") == 1
    registry = json.loads(text)
    assert registry["schema"] == "decision-evidence-index-v1"
    assert registry["canonical_format"] == "docs/evidence/records/*.md#DECISION-EVIDENCE-JSON"
    projected = registry["records"][0]
    assert projected["canonical_record"] == "docs/evidence/records/T1.md"
    assert projected["claims"] == [{
        "display": "+1.0 on 4/4 tasks",
        "name": "value",
        "population": "four fixture tasks",
        "source": "evidence.json#/value",
        "strength": "panel_causal",
    }]
    assert "schema_version" not in projected
    assert "textual_evidence" not in projected

@pytest.mark.parametrize("mutator", [
    lambda r: r.pop("cost"),
    lambda r: r["decisive_claims"][0].update(population=""),
    lambda r: r["decisive_claims"][0]["source"].update(json_pointer="/missing"),
    lambda r: r["relations"].append({"type":"supports","target":"UNKNOWN"}),
    lambda r: r["discussions"].append("MISSING-Q1"),
    lambda r: r.update(status="void-premise"),
    lambda r: r.update(claims_ladder_effect=True),
    lambda r: r["decisive_claims"][0].update(compared_population="other population"),
    lambda r: r["textual_evidence"][0]["source"].update(locator="lines 1-99"),
    lambda r: r.update(does_not_prove=[]),
    lambda r: r.update(limitations=[]),
    lambda r: r.update(reopening_conditions=[]),
])
def test_malformed_fixtures_fail(tmp_path, mutator):
    r = base_record()
    mutator(r)
    repo = make_repo(tmp_path, r, build_generated=False)
    with pytest.raises(ValidationError):
        validate_repository(repo, require_pilot=False, check_generated=False)

def test_void_premise_is_not_counted_as_closure(tmp_path):
    r = base_record()
    r["status"] = "void-premise"
    r["premise_failure"] = {
        "false_premise": "A nonexistent mechanic exists.",
        "refutation": "Source proves it does not.",
        "source": {"path":"source.md","locator":"lines 1-2"},
    }
    repo = make_repo(tmp_path, r)
    records, _warnings = validate_repository(repo, require_pilot=False, check_generated=True)
    manifest = json.loads((repo/"docs/evidence/generated/manifest.json").read_text())
    assert len(records) == 1
    assert manifest["void_premise_count"] == 1
    assert manifest["closure_count_excluding_void"] == 0

def test_disclosed_population_mismatch_passes(tmp_path):
    r = base_record()
    r["decisive_claims"][0].update(
        compared_population="different panel",
        population_compatibility="invalid_disclosed",
        incompatibility_reason="Threshold and outcome use different populations.",
    )
    repo = make_repo(tmp_path, r)
    validate_repository(repo, require_pilot=False, check_generated=True)

@pytest.mark.parametrize("mutator", [
    lambda r: r.update(primary_evidence_strength="unknown_strength"),
    lambda r: r["decisive_claims"][0].update(evidence_strength="unknown_strength"),
    lambda r: r["decisive_claims"][0].update(source={"json_pointer":"/value"}),
    lambda r: r["decisive_claims"][0].update(source={"path":"evidence.json","json_pointer":"/value","locator":"lines 1-1"}),
    lambda r: r["relations"].append({"type":"invalid_relation","target":"external:X"}),
    lambda r: r["acceptance"].update(state="accepted"),
    lambda r: r.update(question=""),
])
def test_additional_mandatory_rule_failures(tmp_path, mutator):
    r = base_record()
    mutator(r)
    repo = make_repo(tmp_path, r, build_generated=False)
    with pytest.raises(ValidationError):
        validate_repository(repo, require_pilot=False, check_generated=False)


def test_d176a_requires_three_distinct_outcomes(tmp_path):
    r = base_record()
    r["id"] = "D176a"
    r["outcomes"] = {"mechanism":"successful", "value":"immaterial", "protocol_quality":"ok"}
    repo = make_repo(tmp_path, r, build_generated=False)
    with pytest.raises(ValidationError):
        validate_repository(repo, require_pilot=False, check_generated=False)


def test_in_bounds_but_unrelated_constraints_excerpt_fails(tmp_path):
    r = base_record()
    r["constraint_projection"]["source"] = {
        "path": "docs/CONSTRAINTS.md",
        "locator": "lines 1-1",
    }
    # CONSTRAINTS.md must exist before the fixture commit so the pinned
    # citation (stamped by make_repo) can resolve it at that commit.
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/CONSTRAINTS.md").write_text(
        "Unrelated result is +9.0 on 99/99 tasks. [OTHER]\n"
        "Fixture value is +1.0 on 4/4 tasks. [T1]\n"
    )
    repo = make_repo(tmp_path, r, build_generated=False)
    with pytest.raises(ValidationError, match="does not identify T1|omits content tokens"):
        validate_repository(repo, require_pilot=False, check_generated=False)

    r["constraint_projection"]["source"]["locator"] = "lines 2-2"
    write_record(repo, r)
    validate_repository(repo, require_pilot=False, check_generated=False)


def test_pinned_locator_survives_later_line_drift(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["constraint_projection"]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["decisive_claims"][0]["source"] = {
        "path": "evidence.json", "commit": sha, "json_pointer": "/value",
    }
    write_record(repo, record)
    # Prepend lines so every old line number is wrong in the working tree.
    (repo / "source.md").write_text(
        "PREPENDED\nPREPENDED\n" + (repo / "source.md").read_text()
    )
    build(repo)
    validate_repository(repo, require_pilot=False, check_generated=True)

def test_unresolvable_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    for src in (
        record["textual_evidence"][0]["source"],
        record["constraint_projection"]["source"],
        record["decisive_claims"][0]["source"],
    ):
        src["commit"] = "0" * 40
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="does not resolve"):
        validate_repository(repo, require_pilot=False, check_generated=False)

def test_path_absent_at_pinned_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    record["textual_evidence"][0]["source"] = {
        "path": "later.md", "commit": sha, "locator": "lines 1-1",
    }
    record["constraint_projection"]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 1-2",
    }
    record["decisive_claims"][0]["source"] = {
        "path": "evidence.json", "commit": sha, "json_pointer": "/value",
    }
    (repo / "later.md").write_text("created after the pin\n")
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="absent at commit"):
        validate_repository(repo, require_pilot=False, check_generated=False)

def test_missing_tokens_at_pinned_commit_is_hard_error(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["schema_version"] = 2
    # Claim asserts a number the pinned excerpt does not contain.
    record["textual_evidence"][0]["claim"] = "Fixture text shows +99.9 improvement."
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    build(repo)
    with pytest.raises(ValidationError, match="omits content tokens"):
        validate_repository(repo, require_pilot=False, check_generated=False)

def test_quote_drift_warns_but_does_not_fail(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
        "quote": "Fixture text.",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    (repo / "source.md").write_text("Fixture value is +1.0 on 4/4 tasks. [T1]\nREWORDED.\n")
    build(repo)
    _records, warnings = validate_repository(repo, require_pilot=False, check_generated=True)
    assert any("drift" in w for w in warnings), warnings

def test_quote_present_in_current_file_produces_no_drift_warning(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    sha = git_init_and_commit(repo)
    record = base_record()
    record["textual_evidence"][0]["source"] = {
        "path": "source.md", "commit": sha, "locator": "lines 2-2",
        "quote": "Fixture text.",
    }
    for src in (record["constraint_projection"]["source"],
                record["decisive_claims"][0]["source"]):
        src.setdefault("commit", sha)
    write_record(repo, record)
    build(repo)
    _records, warnings = validate_repository(repo, require_pilot=False, check_generated=True)
    assert not [w for w in warnings if "drift" in w], warnings
