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

    text = (repo / "docs/evidence/records/T1.md").read_text()
    payload = json.loads(
        text.split("<!-- DECISION-EVIDENCE-JSON", 1)[1]
            .split("END-DECISION-EVIDENCE-JSON -->", 1)[0]
    )
    assert payload["schema_version"] == 2
    src = payload["textual_evidence"][0]["source"]
    assert len(src["commit"]) == 40
    # base_record()'s textual_evidence locator is "lines 1-2" (a deliberate
    # superset used elsewhere in the suite for token-containment checks), so
    # the captured excerpt spans both fixture lines rather than just the
    # claim's own line.
    assert src["quote"] == "Fixture value is +1.0 on 4/4 tasks. [T1]\nFixture text."

    assert migrate_repo(repo) == 0
