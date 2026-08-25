# tests/test_doc_budgets.py
"""Doc budgets from docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md §5.
A budget violation is a real failure: STATE.md's own header has declared a 150-line
budget since 2026-07-29 and reached 360 lines with nothing enforcing it."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE_BUDGET = 150
GOALS_BUDGET = 60

def test_state_md_within_budget():
    lines = (REPO / "docs" / "STATE.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= STATE_BUDGET, (
        f"docs/STATE.md is {len(lines)} lines, budget {STATE_BUDGET}. "
        "Move history to the ledger/archive instead of appending here."
    )

def test_goals_md_within_budget():
    """GOALS.md is the owner's progress view: three goals, one number each.  It rots the
    moment it becomes prose, so the budget it declares in its own header is enforced here
    rather than trusted -- the exact failure this module was written for."""
    lines = (REPO / "docs" / "GOALS.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= GOALS_BUDGET, (
        f"docs/GOALS.md is {len(lines)} lines, budget {GOALS_BUDGET}. "
        "Goals are numbers, not narrative -- move the reasoning to the task record."
    )
