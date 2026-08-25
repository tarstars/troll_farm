"""The paired-night pairing: order alternation, and arm-aware differencing.

Owner ruling 2026-08-22, from `docs/METHODS-LEDGER.md`,
`paired-order-carries-the-drift`: running A B A B and pairing each A with the B
after it puts arm A in the EARLIER slot of every pair, so a within-night trend
enters every difference with a fixed sign. Pairing cancels noise, not trend.
Measured across three nights: the night with no slope was stable under
re-pairing (+0.22 -> +0.30); both nights with a downward slope roughly halved
(+1.02 -> +0.43, +0.55 -> +0.13).

The fix is to alternate the ORDER between pairs (A B, B A, A B, ...). That is
only safe if the arithmetic subtracts by ARM rather than by position — otherwise
reversing a pair silently inverts its sign, which would be far worse than the
bias it repairs. Both properties are pinned here.
"""
from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nr = _load("night_runner", "cgauto/night_runner.py")


def state_from(order_and_scores):
    """`order_and_scores` is [(label, score), ...] in the order they were READ."""
    return {"reads": [{"label": lbl, "score": sc} for lbl, sc in order_and_scores]}


def test_difference_is_A_minus_B_whichever_slot_A_occupies():
    """The load-bearing property: reversing a pair must not flip its sign."""
    a_first = state_from([("A1", 23.0), ("B1", 21.0)])
    b_first = state_from([("B1", 21.0), ("A1", 23.0)])

    assert nr.pair_stats(a_first)["pairs"] == [2.0]
    assert nr.pair_stats(b_first)["pairs"] == [2.0], (
        "a B-first pair was differenced by position, inverting the challenger's "
        "margin — alternating the order without this is worse than the bias"
    )


def test_a_full_alternating_block_reads_the_same_as_the_old_fixed_order():
    """Same scores, same verdict, whichever order the arms were submitted in."""
    fixed = state_from([("A1", 23.0), ("B1", 22.0), ("A2", 21.0), ("B2", 22.0)])
    alternating = state_from([("A1", 23.0), ("B1", 22.0),
                              ("B2", 22.0), ("A2", 21.0)])

    assert nr.pair_stats(fixed)["pairs"] == nr.pair_stats(alternating)["pairs"]
    assert nr.pair_stats(alternating)["mean"] == 0.0


def test_the_plan_alternates_which_arm_goes_first():
    """A must not hold the earlier slot of every pair."""
    plan = nr.session3_state()["plan"]
    firsts = [plan[i]["arm"] for i in range(0, len(plan), 2)]

    assert len(plan) == 10
    assert firsts != ["A"] * 5, "arm A still occupies the earlier slot of every pair"
    assert firsts == ["A", "B", "A", "B", "A"], f"expected ABBA alternation, got {firsts}"


def test_every_pair_still_contains_one_of_each_arm():
    """Alternation must not produce an A/A or B/B pair."""
    plan = nr.session3_state()["plan"]
    for i in range(0, len(plan), 2):
        assert {plan[i]["arm"], plan[i + 1]["arm"]} == {"A", "B"}, (
            f"pair {i // 2 + 1} is not a matched pair"
        )


def test_the_extension_continues_the_alternation_and_balances_at_ten():
    """M-1's extension appends pairs 6..10; at n=10 the order must be balanced."""
    state = nr.session3_state()
    for row in state["plan"]:
        state.setdefault("reads", []).append({"label": row["label"], "score": 22.0})
    nr.extend_plan(state)

    plan = state["plan"]
    firsts = [plan[i]["arm"] for i in range(0, len(plan), 2)]
    assert len(plan) == 20
    assert firsts.count("A") == firsts.count("B") == 5, (
        f"at n=10 each arm must lead five pairs; got {firsts}"
    )
    for i in range(0, len(plan), 2):
        assert {plan[i]["arm"], plan[i + 1]["arm"]} == {"A", "B"}


def test_labels_still_name_their_arm():
    """The arithmetic reads the arm off the label, so the two cannot disagree."""
    plan = nr.session3_state()["plan"]
    for row in plan:
        assert row["label"][0] == row["arm"], f"{row} label and arm disagree"
