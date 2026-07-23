from cgauto.bundle_job_oracle import gate_report, select_option


def option(option_id, delta, kind="control"):
    return {"option": option_id, "margin_delta": delta, "job_kind": kind}


def test_oracle_prefers_control_on_a_terminal_margin_tie():
    chosen = select_option(
        [option(0, 0), option(1, 0, "bank"), option(2, -1, "fell_bank")]
    )
    assert chosen["option"] == 0


def test_oracle_selects_the_lowest_numbered_strict_improvement():
    chosen = select_option(
        [option(0, 0), option(1, 7, "bank"), option(2, 7, "harvest_bank")]
    )
    assert chosen["option"] == 1


def test_frozen_gate_requires_breadth_and_magnitude_simultaneously():
    summary = {
        "roots": 240,
        "noncontrol_options": 2400,
        "selected_noncontrol_rate": 0.10,
        "mean_oracle_margin_delta": 8.0,
        "mean_selected_root_margin_delta": 20.0,
        "selected_job_kinds": {"bank": 10, "fell_bank": 10, "harvest_bank": 0},
        "opponent_mean_oracle_margin_delta": {
            "a": 3.0,
            "b": 3.0,
            "c": 3.0,
            "d": 3.0,
            "e": 3.0,
            "f": 3.0,
            "g": 0.0,
            "h": 0.0,
        },
    }
    assert gate_report(summary, True)["passed"]
    summary["opponent_mean_oracle_margin_delta"]["h"] = -0.01
    assert not gate_report(summary, True)["passed"]
