from copy import deepcopy
from datetime import datetime, timedelta, timezone

from cgauto.arena_transfer_checkpoint import summarize
from cgauto.opponent_crop_dual_value_arena_gate import evaluate


def checkpoint(agent: int, submission: int, count: int, score: float) -> dict:
    rows = [
        {
            "game_id": index,
            "margin": 10 if index % 4 else -20,
            "valid": True,
            "runtime_markers": [],
        }
        for index in range(count)
    ]
    return {
        "agent_id": agent,
        "submission_id": submission,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "matching_finished": count,
        "matching_pending": 0,
        "parsed_results": count,
        "fetch_failures": [],
        "unexpected_rows": [],
        "identity_clean": True,
        "arena": {"score": score},
        "summary": summarize(rows),
        "rows": rows,
    }


def baseline() -> dict:
    return checkpoint(6560289, 41012593, 160, 24.28)


def candidate(count: int, score: float) -> dict:
    return checkpoint(6560350, 41012867, count, score)


def test_early_gate_continues_above_floor() -> None:
    assert evaluate(baseline(), candidate(60, 22.79), "early-60")["status"] == "continue"


def test_early_gate_rejects_at_floor() -> None:
    assert evaluate(baseline(), candidate(60, 22.78), "early-60")["status"] == "reject"


def test_terminal_requires_delayed_confirmation() -> None:
    initial = candidate(160, 24.90)
    assert evaluate(baseline(), initial, "terminal")["status"] == "wait"
    confirm = deepcopy(initial)
    confirm["observed_at"] = (
        datetime.fromisoformat(initial["observed_at"]) + timedelta(minutes=16)
    ).isoformat()
    assert evaluate(baseline(), initial, "terminal", confirm)["status"] == "promote"
