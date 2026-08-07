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
