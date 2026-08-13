# tests/test_doc_budgets.py
"""Doc budgets from docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md §5.
A budget violation is a real failure: STATE.md's own header has declared a 150-line
budget since 2026-07-29 and reached 360 lines with nothing enforcing it."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_BUDGET = 150

def test_state_md_within_budget():
    lines = (REPO / "docs" / "STATE.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= STATE_BUDGET, (
        f"docs/STATE.md is {len(lines)} lines, budget {STATE_BUDGET}. "
        "Move history to the ledger/archive instead of appending here."
    )
