from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.migrate_evidence_locators import migrate_repo
from tests.test_decision_evidence_index import (
    base_record, git_init_and_commit, make_repo, write_record,
)


def _read_payload(repo: Path, record_id: str = "T1") -> dict:
    text = (repo / f"docs/evidence/records/{record_id}.md").read_text(encoding="utf-8")
    return json.loads(
        text.split("<!-- DECISION-EVIDENCE-JSON", 1)[1]
            .split("END-DECISION-EVIDENCE-JSON -->", 1)[0]
    )


def test_migration_pins_commit_and_captures_quote_and_is_idempotent(tmp_path):
    repo = make_repo(tmp_path, build_generated=False)
    record = base_record()
    record["schema_version"] = 1
    for src in (record["textual_evidence"][0]["source"],
                record["constraint_projection"]["source"]):
        src.pop("commit", None)
    record["decisive_claims"][0]["source"].pop("commit", None)
    write_record(repo, record)
    git_init_and_commit(repo)

    changed = migrate_repo(repo)
    assert changed == 1

    payload = _read_payload(repo)
    assert payload["schema_version"] == 2

    # base_record()'s textual_evidence and constraint_projection locators are
    # both "lines 1-2" (a deliberate superset used elsewhere in the suite for
    # token-containment checks), so the captured excerpt spans both fixture
    # lines rather than just the claim's own line.
    expected_excerpt = "Fixture value is +1.0 on 4/4 tasks. [T1]\nFixture text."

    te_src = payload["textual_evidence"][0]["source"]
    assert len(te_src["commit"]) == 40
    assert te_src["quote"] == expected_excerpt

    cp_src = payload["constraint_projection"]["source"]
    assert len(cp_src["commit"]) == 40
    assert cp_src["quote"] == expected_excerpt

    dc_src = payload["decisive_claims"][0]["source"]
    assert len(dc_src["commit"]) == 40
    # decisive_claims cites via json_pointer, not a line locator, so no
    # quote is captured for it -- only the commit is stamped.
    assert "quote" not in dc_src
    assert dc_src["json_pointer"] == "/value"
    assert dc_src["path"] == "evidence.json"

    assert migrate_repo(repo) == 0


def test_migration_stamps_premise_failure_source(tmp_path):
    """H7 is a real void-premise record whose premise_failure.source is the
    only exerciser of the fourth source location. Cover it explicitly so a
    regression here cannot slip past the test suite."""
    repo = make_repo(tmp_path, build_generated=False)
    record = base_record()
    record["schema_version"] = 1
    record["status"] = "void-premise"
    record["premise_failure"] = {
        "false_premise": "A nonexistent mechanic exists.",
        "refutation": "Source proves it does not.",
        "source": {"path": "source.md", "locator": "lines 1-2"},
    }
    write_record(repo, record)
    git_init_and_commit(repo)

    changed = migrate_repo(repo)
    assert changed == 1

    payload = _read_payload(repo)
    assert payload["schema_version"] == 2
    pf = payload["premise_failure"]
    pf_src = pf["source"]
    assert len(pf_src["commit"]) == 40
    assert pf_src["quote"] == "Fixture value is +1.0 on 4/4 tasks. [T1]\nFixture text."
    # Prose fields on premise_failure must be untouched by the migration.
    assert pf["false_premise"] == "A nonexistent mechanic exists."
    assert pf["refutation"] == "Source proves it does not."

    assert migrate_repo(repo) == 0


def test_migration_preserves_non_ascii_prose_byte_for_byte(tmp_path):
    """Regression for the ensure_ascii=True defect: json.dumps() re-serializes
    the *whole* payload whenever schema_version bumps 1->2, so any non-ASCII
    prose (curly quotes, minus/arrow/delta signs, etc., all present in the
    real records) must round-trip byte-for-byte rather than being rewritten
    as \\uXXXX escapes."""
    repo = make_repo(tmp_path, build_generated=False)
    record = base_record()
    record["schema_version"] = 1
    question = "Does Δ improve → outcome by ≥1.0 vs ≤0 baseline, ’smart’ quotes?"
    scope = "Scope with − minus and → arrow."
    conclusion = "Yes — Δ ≥ threshold."
    display = "+1.0 on 4/4 tasks (Δ ≥ 1.0)"
    claim = "Fixture text with ’apostrophe’ and → arrow."
    bullet = "Fixture value is +1.0 → [T1] (Δ ≥ 1.0)"
    record["question"] = question
    record["scope"] = scope
    record["conclusion"] = conclusion
    record["decisive_claims"][0]["display"] = display
    record["textual_evidence"][0]["claim"] = claim
    record["constraint_projection"]["bullet"] = bullet
    for src in (record["textual_evidence"][0]["source"],
                record["constraint_projection"]["source"]):
        src.pop("commit", None)
    record["decisive_claims"][0]["source"].pop("commit", None)
    write_record(repo, record)
    git_init_and_commit(repo)

    changed = migrate_repo(repo)
    assert changed == 1

    text = (repo / "docs/evidence/records/T1.md").read_text(encoding="utf-8")
    assert "\\u" not in text, "non-ASCII prose was escaped instead of preserved"

    payload = _read_payload(repo)
    assert payload["question"] == question
    assert payload["scope"] == scope
    assert payload["conclusion"] == conclusion
    assert payload["decisive_claims"][0]["display"] == display
    assert payload["textual_evidence"][0]["claim"] == claim
    assert payload["constraint_projection"]["bullet"] == bullet

    assert migrate_repo(repo) == 0
