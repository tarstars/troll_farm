"""Exit semantics of the bite-test mutation runner (G5 instance 5, finding F2).

The defect being removed: ``return 0 if control_green else 1`` — a drive whose
mutants never patched or compiled still reported success. Verdicts must reflect
drive VALIDITY; kill results are a measurement, not a harness failure.
"""
import importlib.util
import pathlib

RUNNER = (pathlib.Path(__file__).resolve().parents[1]
          / "claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py")
spec = importlib.util.spec_from_file_location("run_mutations_g5", RUNNER)
rm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rm)


def _totals(run, patch_failed=0, compile_failed=0):
    return {"mutants_run": run, "patch_failed": patch_failed,
            "compile_failed": compile_failed}


def test_vacuous_drive_zero_mutants_is_exit_3():
    assert rm.drive_verdict(True, _totals(0), allow_partial=False) == 3


def test_vacuous_drive_not_excusable_by_allow_partial():
    assert rm.drive_verdict(True, _totals(0), allow_partial=True) == 3


def test_partial_drive_compile_failures_exit_4_by_default():
    assert rm.drive_verdict(True, _totals(5, compile_failed=2),
                            allow_partial=False) == 4


def test_partial_drive_patch_failures_exit_4_by_default():
    assert rm.drive_verdict(True, _totals(5, patch_failed=1),
                            allow_partial=False) == 4


def test_partial_drive_allowed_with_flag():
    assert rm.drive_verdict(True, _totals(5, patch_failed=1),
                            allow_partial=True) == 0


def test_control_red_is_exit_1_before_anything_else():
    assert rm.drive_verdict(False, _totals(0), allow_partial=False) == 1


def test_clean_full_drive_is_exit_0():
    assert rm.drive_verdict(True, _totals(9), allow_partial=False) == 0
