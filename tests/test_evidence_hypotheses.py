from __future__ import annotations
import json, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.evidence_hypotheses import (
    HypothesisError, load_hypotheses, validate_hypothesis,
)
from cgauto.build_decision_evidence_index import render_open_questions

START = "<!-- HYPOTHESIS-JSON"
END = "END-HYPOTHESIS-JSON -->"

def base_hypothesis():
    return {
        "id": "Q1",
        "question": "Is v4 the best rebuild base?",
        "origin": ["coordination/messages/chatgpt_1/20260807T112000Z-x.md"],
        "positions": [
            {"agent": "chatgpt_1", "stance": "v4 is least-bad reference"},
            {"agent": "claude_1", "stance": "no independent view"},
        ],
        "status": "open",
        "next_action": "Re-run the panel on v4 and v1 and compare blocking counts.",
    }

def write_hypothesis(repo: Path, h: dict):
    d = repo / "docs/evidence/hypotheses"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{h['id']}.md").write_text(
        f"# {h['id']}\n\n{START}\n{json.dumps(h, indent=2, sort_keys=True)}\n{END}\n"
    )

def test_minimal_hypothesis_validates(tmp_path):
    write_hypothesis(tmp_path, base_hypothesis())
    hs = load_hypotheses(tmp_path)
    assert len(hs) == 1
    validate_hypothesis(hs[0], record_ids=set())

def test_missing_field_rejected(tmp_path):
    h = base_hypothesis()
    del h["next_action"]
    with pytest.raises(HypothesisError, match="next_action"):
        validate_hypothesis(h, record_ids=set())

def test_bad_status_rejected(tmp_path):
    h = base_hypothesis()
    h["status"] = "kinda-open"
    with pytest.raises(HypothesisError, match="status"):
        validate_hypothesis(h, record_ids=set())

def test_resolved_requires_graduation_link(tmp_path):
    h = base_hypothesis()
    h["status"] = "resolved"
    with pytest.raises(HypothesisError, match="graduat"):
        validate_hypothesis(h, record_ids={"D101"})
    h["graduated_to"] = "D101"
    validate_hypothesis(h, record_ids={"D101"})

def test_graduation_target_must_exist(tmp_path):
    h = base_hypothesis()
    h["status"] = "resolved"
    h["graduated_to"] = "NOPE"
    with pytest.raises(HypothesisError, match="unknown record"):
        validate_hypothesis(h, record_ids={"D101"})

def test_origin_path_must_exist_when_repo_root_given(tmp_path):
    h = base_hypothesis()
    h["origin"] = ["docs/does-not-exist.md"]
    with pytest.raises(HypothesisError, match="origin path does not exist"):
        validate_hypothesis(h, record_ids=set(), repo_root=tmp_path)

def test_origin_path_existing_passes_when_repo_root_given(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("hello\n")
    h = base_hypothesis()
    h["origin"] = ["docs/real.md"]
    validate_hypothesis(h, record_ids=set(), repo_root=tmp_path)

def test_origin_path_existence_skipped_without_repo_root(tmp_path):
    # base_hypothesis()'s origin paths are message paths that do not exist
    # relative to tmp_path; omitting repo_root preserves the old
    # repo-agnostic behaviour so existing unit-level callers are unaffected.
    h = base_hypothesis()
    validate_hypothesis(h, record_ids=set())

def test_unsafe_origin_path_rejected(tmp_path):
    h = base_hypothesis()
    h["origin"] = ["../escape.md"]
    with pytest.raises(HypothesisError, match="unsafe origin path"):
        validate_hypothesis(h, record_ids=set())

def test_load_hypotheses_returns_empty_for_absent_directory(tmp_path):
    assert not (tmp_path / "docs/evidence/hypotheses").exists()
    assert load_hypotheses(tmp_path) == []

def test_load_hypotheses_returns_empty_for_empty_directory(tmp_path):
    (tmp_path / "docs/evidence/hypotheses").mkdir(parents=True)
    assert load_hypotheses(tmp_path) == []

def test_open_questions_render_is_deterministic_and_lists_open_first(tmp_path):
    h1 = base_hypothesis()
    h2 = base_hypothesis(); h2["id"] = "Q2"; h2["status"] = "void"
    first = render_open_questions([h1, h2])
    second = render_open_questions([h1, h2])
    assert first == second
    assert "Q1" in first and "Q2" in first
    assert first.index("Q1") < first.index("Q2")
    assert "Is v4 the best rebuild base?" in first

def test_open_questions_render_handles_empty_list(tmp_path):
    rendered = render_open_questions([])
    assert "Live questions: **0**" in rendered
    assert "Total entries: **0**" in rendered
    assert rendered.endswith("\n") and not rendered.endswith("\n\n")
