"""Pure tests for controlled idle-harvest telemetry extraction."""

from cgauto.idle_harvest_field_probe import telemetry_summary


def test_telemetry_summary_reads_test_session_stderr_frames() -> None:
    result = {
        "frames": [
            {"stderr": "@IH_CAND t=280 unit=0 commands=HARVEST 0\n"},
            {"stderr": "@IH_SELECT t=280 unit=0 command=HARVEST 0\n"},
            {"stderr": "@IH_ORCHARD_FORCE t=290 unit=0 command=HARVEST 0\n"},
        ]
    }

    summary = telemetry_summary(result)

    assert summary["counts"] == {"cand": 1, "select": 1, "orchard_force": 1}
    assert summary["select_turns"] == [280]
    assert summary["orchard_force_turns"] == [290]
