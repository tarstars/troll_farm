from pathlib import Path
from types import SimpleNamespace
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "codex_1" / "norxondor-port" / "loss_read.py"
SPEC = importlib.util.spec_from_file_location("norxondor_port_loss_read", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def parsed(**updates):
    payload = {
        "moves": {},
        "harvest": [],
        "chop": [],
        "plant": [],
        "pick": [],
        "drop": [],
        "mine": [],
    }
    payload.update(updates)
    return SimpleNamespace(**payload)


def test_phase_index_has_exact_fifty_turn_boundaries():
    assert MODULE.phase_index(1) == 0
    assert MODULE.phase_index(50) == 0
    assert MODULE.phase_index(51) == 1
    assert MODULE.phase_index(300) == 5


def test_parsed_activity_closes_the_requested_action_denominator():
    actions = MODULE.parsed_activity(parsed(
        moves={1: (2, 3)}, harvest=[2], chop=[3], plant=[(4, "BANANA")],
        pick=[(5, "PLUM")], drop=[6], mine=[7],
    ))
    assert actions == {
        1: "move", 2: "harvest", 3: "chop", 4: "plant",
        5: "pick", 6: "drop", 7: "mine",
    }


def test_empty_events_keeps_six_inventory_items_per_phase_and_seat():
    events = MODULE.empty_events()
    assert set(events["deposits"]) == {0, 1}
    assert len(events["deposits"][0]) == 6
    assert all(row == [0] * 6 for row in events["deposits"][1])


def test_activity_windows_split_at_the_requested_phase_boundary():
    assert MODULE.ACTIVITY_WINDOWS == {
        "100-150": (100, 150),
        "151-200": (151, 200),
        "100-200": (100, 200),
    }
