import importlib.util
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("cut_fixtures", Path("scripts/cut_fixtures.py"))
cut = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cut)


def row(turn, *, branch="N", available="NONE", wc=0, ka=0):
    return {
        "turn": turn,
        "units": {"0": {"chosen": "NONE", "available": available, "branch": branch}},
        "meta": {"wc": wc, "xc": 0, "ka": ka},
    }


def test_event_and_run_detectors():
    rows = [row(turn, available="TREE(1,2)") for turn in range(1, 61)]
    rows[2]["meta"]["wc"] = 1
    rows[3]["meta"]["ka"] = 31
    classes = [hit[0] for hit in cut.selected(rows)]
    assert classes.count("dance") == 1
    assert classes.count("long_kept_goal") == 1
    assert classes.count("parked_troll") == 1
    assert classes.count("stall") == 1


def test_grader_requires_zero_count_reason():
    library = {"errors": [], "fixtures": [], "counts": {name: 0 for name in cut.CLASSES}, "absent_classes": {}}
    errors = cut.grade(library)
    assert len(errors) == len(cut.CLASSES)
