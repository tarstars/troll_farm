"""Exit semantics of the bite-test mutation runner (guards task G5 instance 5).

The contract pinned here is claude_1's 2026-08-10 revision (``80c3dd63``),
integrated 2026-08-12, which superseded the trunk defect
``return 0 if control_green else 1`` (a drive whose mutants never patched or
compiled reported success). Severity order: control red beats everything;
an incomplete drive (subset, structural failures, drift override) exits 2
unless ``--partial`` acknowledges it on the record — the results document
still carries ``completeness.complete = false`` either way, so a publisher
gating on the doc sees the subset even when the exit is 0.
"""
import importlib.util
import pathlib

RUNNER = (pathlib.Path(__file__).resolve().parents[1]
          / "claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py")
spec = importlib.util.spec_from_file_location("run_mutations_g5", RUNNER)
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)


def test_control_red_is_exit_1_regardless_of_completeness():
    assert rm.drive_verdict(False, True, False, []) == 1
    assert rm.drive_verdict(False, False, True, ["subset"]) == 1


def test_incomplete_unacknowledged_is_exit_2():
    assert rm.drive_verdict(True, False, False,
                            ["3 mutant(s) failed to compile"]) == 2


def test_incomplete_acknowledged_with_partial_is_exit_0():
    assert rm.drive_verdict(True, False, True,
                            ["--only selected 4 of 24 manifest entries"]) == 0


def test_complete_drive_is_exit_0():
    assert rm.drive_verdict(True, True, False, []) == 0


def test_vacuous_acknowledged_drive_exits_0_by_design():
    # Deliberate in the integrated design: --partial states the subset on the
    # record; the results doc's completeness block (complete=false, reasons)
    # is what publishers must gate on. This test documents the trade.
    assert rm.drive_verdict(True, False, True,
                            ["attempted 0 of 24 manifest entries"]) == 0
