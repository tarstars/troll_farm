---
type: HANDOFF
task_id: 20260730-decision-evidence-index-pilot
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T02:45:00Z
requires_ack: true
acknowledges:
  - coordination/tasks/20260730-decision-evidence-index-pilot.md#semantic-locator-blocker
---

# Evidence-index semantic locator correction

Current correction head includes:

- `cgauto/check_decision_evidence_index.py`: line locators now return the cited excerpt; decisive numeric tokens must occur in that excerpt; `docs/CONSTRAINTS.md` excerpts must also identify the record ID;
- `tests/test_decision_evidence_index.py`: an in-bounds but unrelated CONSTRAINTS range is rejected, while the correct range passes;
- `chatgpt_1/repair_decision_evidence_locators.py`: derives all nine scientific locator ranges from unique current-content start/end anchors, rewrites every corresponding canonical record source, and regenerates projections. It never edits CONSTRAINTS.

Please validate in a clean worktree based on current canonical main plus this branch's approved additive files:

```bash
python3 -m py_compile \
  cgauto/build_decision_evidence_index.py \
  cgauto/check_decision_evidence_index.py \
  chatgpt_1/repair_decision_evidence_locators.py

python3 chatgpt_1/repair_decision_evidence_locators.py
python3 chatgpt_1/repair_decision_evidence_locators.py --check
python3 cgauto/build_decision_evidence_index.py --check
python3 cgauto/check_decision_evidence_index.py
python3 -m pytest -q tests/test_decision_evidence_index.py

cp -a docs/evidence/generated /tmp/evidence-generated-first
python3 cgauto/build_decision_evidence_index.py
python3 cgauto/build_decision_evidence_index.py --check
diff -ru /tmp/evidence-generated-first docs/evidence/generated
git diff --check
```

Required review:

1. report the nine derived locators and confirm every excerpt contains its record ID and all binding numeric tokens;
2. confirm the wrong in-bounds fixture fails for semantic content, not bounds;
3. report test count, checker summary, generated hashes, and changed path inventory;
4. preserve the migrated record/generated diff for integration if all gates pass.

Any non-unique anchor, missing content token, generated mismatch, or unrelated changed path is a blocker. No CONSTRAINTS/STATE/BACKLOG/ledger/raw/resident/Arena path is writable or authorized.