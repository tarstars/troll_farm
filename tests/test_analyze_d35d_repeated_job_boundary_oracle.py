from cgauto.analyze_d35d_repeated_job_boundary_oracle import (
    INTEGER_FIELDS,
    OPPONENTS,
    analyze,
    select_rollout,
)


TEST_SEEDS = tuple(range(100, 108))


def set_outcome(row: dict, prefix: str, own: int, opponent: int, turn: int) -> None:
    row.update(
        {
            f"{prefix}_own_score": own,
            f"{prefix}_opponent_score": opponent,
            f"{prefix}_margin": own - opponent,
            f"{prefix}_own_wood": own // 4,
            f"{prefix}_opponent_wood": opponent // 4,
            f"{prefix}_own_workers": 2,
            f"{prefix}_opponent_workers": 2,
            f"{prefix}_terminal_turn": turn,
        }
    )


def plan_key(option: int) -> str:
    target = option if option <= 10 else option + 100
    return f"fell_bank:0:{target},1:-:-+keep:1:-:-:-|train=none"


def base_row(seed: int, seat: int, opponent: str, epoch: int, option: int) -> dict:
    row = {field: 0 for field in INTEGER_FIELDS}
    row.update(
        {
            "seed": seed,
            "seat": seat,
            "opponent": opponent,
            "epoch": epoch,
            "epoch_turn": 50 + 10 * epoch,
            "option": option,
            "selected": int(option == 11),
            "catalog": (
                "control" if option == 0 else "generic" if option <= 10 else "competitive"
            ),
            "plan_key": "control" if option == 0 else plan_key(option),
            "role_tuple": "control" if option == 0 else "fell_bank+keep",
            "target_owners": (
                "none+none"
                if option == 0
                else "natural+none"
                if option <= 10
                else "opponent+none"
            ),
            "predicted_eta": 0 if option == 0 else 10,
            "predicted_reward": 0 if option == 0 else 20,
            "rate_score": 0 if option == 0 else 2000,
            "competitive_target_count": int(option > 10),
            "opponent_target_count": int(option > 10),
            "rollout_statuses": "" if option == 0 else "0:completed,1:keep",
            "rollout_overridden_actions": 0 if option == 0 else 5,
            "rollout_max_own_workers": 2,
            "rollout_bundle_end_turn": 50 + 10 * epoch + (0 if option == 0 else 10),
            "root_plan_count": 20,
            "generic_plan_count": 10,
            "competitive_plan_count": 10,
            "root_natural_plants": 5,
            "root_own_plants": 3,
            "root_opponent_plants": 4,
            "executed_end_turn": 50 + 10 * epoch + 10 if option == 11 else -1,
            "execution_statuses": "0:completed,1:keep" if option == 11 else "",
            "execution_overridden_actions": 5 if option == 11 else 0,
            "execution_terminal": int(epoch == 1 and option == 11),
            "execution_prefix_match": int(option == 11),
            "selected_rollout_replay_match": int(option == 11),
            "one_shot_catalog": "competitive",
            "one_shot_key": plan_key(11),
            "selected_noncontrol_epochs": 2,
            "selected_competitive_epochs": 2,
            "stop_reason": "terminal",
            "repeated_max_own_workers": 2,
            "repeated_terminal_hash": seed * 100 + seat * 10 + OPPONENTS.index(opponent) + 1,
        }
    )
    set_outcome(row, "farm", 100, 100, 301)
    set_outcome(row, "resident", 100, 0, 301)
    set_outcome(row, "one_shot", 180, 80, 301)
    set_outcome(row, "repeated", 200, 50, 70)
    if epoch == 0 and option == 0:
        set_outcome(row, "rollout", 100, 100, 301)
    elif epoch == 0 and option == 11:
        set_outcome(row, "rollout", 180, 80, 301)
    elif epoch == 1 and option == 0:
        set_outcome(row, "rollout", 180, 80, 301)
    elif epoch == 1 and option == 11:
        set_outcome(row, "rollout", 200, 50, 70)
    else:
        set_outcome(row, "rollout", 90, 100, 301)
    row.update(
        {
            "repeated_margin_delta_farm": row["repeated_margin"] - row["farm_margin"],
            "repeated_own_score_delta_farm": row["repeated_own_score"]
            - row["farm_own_score"],
            "repeated_opponent_score_delta_farm": row["repeated_opponent_score"]
            - row["farm_opponent_score"],
            "repeated_margin_delta_resident": row["repeated_margin"]
            - row["resident_margin"],
            "repeated_own_score_delta_resident": row["repeated_own_score"]
            - row["resident_own_score"],
            "repeated_opponent_score_delta_resident": row[
                "repeated_opponent_score"
            ]
            - row["resident_opponent_score"],
            "repeated_margin_delta_one_shot": row["repeated_margin"]
            - row["one_shot_margin"],
            "repeated_own_score_delta_one_shot": row["repeated_own_score"]
            - row["one_shot_own_score"],
            "repeated_opponent_score_delta_one_shot": row[
                "repeated_opponent_score"
            ]
            - row["one_shot_opponent_score"],
            "one_shot_margin_delta_farm": row["one_shot_margin"]
            - row["farm_margin"],
            "one_shot_own_score_delta_farm": row["one_shot_own_score"]
            - row["farm_own_score"],
            "one_shot_opponent_score_delta_farm": row["one_shot_opponent_score"]
            - row["farm_opponent_score"],
            "one_shot_margin_delta_resident": row["one_shot_margin"]
            - row["resident_margin"],
            "one_shot_own_score_delta_resident": row["one_shot_own_score"]
            - row["resident_own_score"],
            "one_shot_opponent_score_delta_resident": row[
                "one_shot_opponent_score"
            ]
            - row["resident_opponent_score"],
        }
    )
    return row


def complete_rows() -> list[dict]:
    return [
        base_row(seed, seat, opponent, epoch, option)
        for seed in TEST_SEEDS
        for seat in (0, 1)
        for opponent in OPPONENTS
        for epoch in (0, 1)
        for option in range(21)
    ]


def complete_manifest() -> list[dict]:
    rows = []
    for seed in TEST_SEEDS:
        for seat in (0, 1):
            for opponent in OPPONENTS:
                row = {
                    "seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "eligible": 1,
                    "start_turn": 50,
                    "prefix_attribution_failures": 0,
                    "farm_attribution_failures": 0,
                    "start_history_mismatch": 0,
                    "start_cell_mismatch": 0,
                    "farm_max_own_workers": 2,
                }
                set_outcome(row, "farm", 100, 100, 301)
                set_outcome(row, "resident", 100, 0, 301)
                rows.append(row)
    return rows


def weaken_repeated_suppression(rows: list[dict]) -> None:
    for row in rows:
        set_outcome(row, "repeated", 200, 90, 70)
        if row["epoch"] == 1 and row["option"] == 11:
            set_outcome(row, "rollout", 200, 90, 70)
        row.update(
            {
                "repeated_margin_delta_farm": row["repeated_margin"]
                - row["farm_margin"],
                "repeated_own_score_delta_farm": row["repeated_own_score"]
                - row["farm_own_score"],
                "repeated_opponent_score_delta_farm": row[
                    "repeated_opponent_score"
                ]
                - row["farm_opponent_score"],
                "repeated_margin_delta_resident": row["repeated_margin"]
                - row["resident_margin"],
                "repeated_own_score_delta_resident": row["repeated_own_score"]
                - row["resident_own_score"],
                "repeated_opponent_score_delta_resident": row[
                    "repeated_opponent_score"
                ]
                - row["resident_opponent_score"],
                "repeated_margin_delta_one_shot": row["repeated_margin"]
                - row["one_shot_margin"],
                "repeated_own_score_delta_one_shot": row["repeated_own_score"]
                - row["one_shot_own_score"],
                "repeated_opponent_score_delta_one_shot": row[
                    "repeated_opponent_score"
                ]
                - row["one_shot_opponent_score"],
            }
        )


def test_tie_break_prefers_control_then_fewer_overrides() -> None:
    control = {
        "rollout_margin": 10,
        "option": 0,
        "rollout_overridden_actions": 0,
        "plan_key": "control",
    }
    tied = {
        "rollout_margin": 10,
        "option": 1,
        "rollout_overridden_actions": 0,
        "plan_key": "a",
    }
    assert select_rollout([tied, control]) is control
    costly = dict(tied, rollout_margin=11, rollout_overridden_actions=3)
    cheap = dict(tied, rollout_margin=11, rollout_overridden_actions=2)
    assert select_rollout([costly, cheap]) is cheap


def test_complete_repeated_oracle_passes_frozen_gates() -> None:
    report = analyze(complete_rows(), complete_manifest(), TEST_SEEDS)
    assert report["integrity"]["complete"]
    assert report["repeated_oracle"]["passes_all_gates"]
    assert report["confirmation_authorized"]
    assert report["decision"] == "open_sealed_confirmation_export_scheduler_dataset"


def test_epoch_chain_error_refuses_outcome_selection() -> None:
    rows = complete_rows()
    for row in rows:
        if row["epoch"] == 1:
            row["epoch_turn"] += 1
    report = analyze(rows, complete_manifest(), TEST_SEEDS)
    assert not report["integrity"]["complete"]
    assert report["integrity"]["epoch_chain_errors"] > 0
    assert report["decision"] == "invalid_integrity_do_not_select_outcomes"


def test_repeat_mismatch_refuses_outcome_selection() -> None:
    report = analyze(
        complete_rows(),
        complete_manifest(),
        TEST_SEEDS,
        repeat_rows_verified=False,
    )
    assert not report["integrity"]["complete"]
    assert report["decision"] == "invalid_integrity_do_not_select_outcomes"


def test_valid_but_weak_suppression_closes_productive_substrate() -> None:
    rows = complete_rows()
    weaken_repeated_suppression(rows)
    report = analyze(rows, complete_manifest(), TEST_SEEDS)
    assert report["integrity"]["complete"]
    assert not report["repeated_oracle"]["passes_all_gates"]
    assert not report["confirmation_authorized"]
    assert (
        report["decision"]
        == "reject_repeated_productive_farm_advance_resident_joint_objective"
    )
