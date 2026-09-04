#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import oracle


class FakeRef:
    def __init__(self):
        self.units = {
            0: {"player": 0, "cell": (1, 1), "speed": 1, "cap": 2,
                "harvest": 1, "chop": 1, "carry": [0] * 6},
            2: {"player": 0, "cell": (2, 1), "speed": 2, "cap": 3,
                "harvest": 0, "chop": 3, "carry": [0] * 6},
        }


def test_fragments():
    assert oracle.command_fragments("MSG hi; MOVE 0 3 4 ;;WAIT") == [
        "MSG hi", "MOVE 0 3 4", "WAIT"
    ]
    assert oracle.fragment_unit("MOVE 2 3 4") == 2
    assert oracle.fragment_unit("TRAIN 1 1 0 1") is None


def test_rewrite_preserves_non_overridden_and_train():
    ref = FakeRef()
    line = "MSG x;TRAIN 1 2 0 2;MOVE 0 9 9;CHOP 2"
    got = oracle.rewrite_for_test(line, {2: "MOVE 2 4 4"}, {(4, 4)}, ref)
    assert got == "MSG x;TRAIN 1 2 0 2;MOVE 0 9 9;MOVE 2 4 4"


def test_reserved_target_suppresses_other_worker():
    ref = FakeRef()
    line = "MOVE 0 4 4;MOVE 2 8 8"
    got = oracle.rewrite_for_test(line, {2: "CHOP 2"}, {(4, 4)}, ref)
    assert got == "CHOP 2"


def test_bootstrap_zero():
    ci = oracle.bootstrap_ci([0.0] * 8, draws=200)
    assert ci["n"] == 8
    assert ci["mean"] == ci["lower95"] == ci["upper95"] == 0.0


def test_policy_manifest_requires_no_plant():
    payload = {
        "policies": [
            {
                "name": "x", "enabled": True, "species": "BANANA",
                "start_turn": 70, "plant_count": 1,
                "max_door_distance": 2, "latest_plant_turn": 100,
                "fell_size": 4,
            }
        ]
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p.json"
        path.write_text(json.dumps(payload))
        try:
            oracle.load_policies(path)
        except oracle.ExperimentError:
            pass
        else:
            raise AssertionError("manifest without NO_PLANT was accepted")


def main():
    tests = [
        test_fragments,
        test_rewrite_preserves_non_overridden_and_train,
        test_reserved_target_suppresses_other_worker,
        test_bootstrap_zero,
        test_policy_manifest_requires_no_plant,
    ]
    for test in tests:
        test()
        print("ok", test.__name__)
    print(f"PASS {len(tests)} tests")


if __name__ == "__main__":
    main()
