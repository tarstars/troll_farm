from cgauto.analyze_d36_resident_constrained_joint_oracle import (
    INTEGER_FIELDS,
    OPPONENTS,
    analyze,
    select_constrained,
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


def base_row(
    seed: int,
    seat: int,
    opponent: str,
    epoch: int,
    option: int,
    one_own: int,
    repeated_own: int,
) -> dict:
    task_id = seed * 100 + seat * 10 + OPPONENTS.index(opponent)
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
            "unconstrained_selected": int(epoch == 0 and option == 12),
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
            "rollout_bundle_end_turn": 50
            + 10 * epoch
            + (0 if option == 0 else 10),
            "rollout_execution_terminal": int(epoch == 1 and option == 11),
            "rollout_max_own_workers": 2,
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
            "one_shot_terminal_hash": task_id + 2_000_000,
            "unconstrained_catalog": "competitive",
            "unconstrained_key": plan_key(12),
            "unconstrained_terminal_hash": task_id + 3_000_000,
            "selected_noncontrol_epochs": 2,
            "selected_competitive_epochs": 2,
            "stop_reason": "terminal",
            "repeated_max_own_workers": 2,
            "repeated_terminal_hash": task_id + 4_000_000,
            "resident_terminal_hash": task_id + 1_000_000,
            "opponent_excess_ceiling": 65,
        }
    )
    set_outcome(row, "resident", 100, 100, 301)
    set_outcome(row, "one_shot", one_own, 140, 301)
    set_outcome(row, "unconstrained", one_own + 50, 170, 301)
    set_outcome(row, "repeated", repeated_own, 145, 70)
    if epoch == 0 and option == 0:
        set_outcome(row, "rollout", 100, 100, 301)
        row["rollout_terminal_hash"] = row["resident_terminal_hash"]
    elif epoch == 0 and option == 11:
        set_outcome(row, "rollout", one_own, 140, 301)
        row["rollout_terminal_hash"] = row["one_shot_terminal_hash"]
    elif epoch == 0 and option == 12:
        set_outcome(row, "rollout", one_own + 50, 170, 301)
        row["rollout_terminal_hash"] = row["unconstrained_terminal_hash"]
    elif epoch == 1 and option == 0:
        set_outcome(row, "rollout", one_own, 140, 301)
        row["rollout_terminal_hash"] = row["one_shot_terminal_hash"]
    elif epoch == 1 and option == 11:
        set_outcome(row, "rollout", repeated_own, 145, 70)
        row["rollout_terminal_hash"] = row["repeated_terminal_hash"]
    else:
        set_outcome(row, "rollout", 90, 100, 301)
        row["rollout_terminal_hash"] = task_id + 5_000_000 + epoch * 100 + option
    row["feasible"] = int(row["rollout_opponent_score"] - 100 <= 65)
    row.update(
        {
            "repeated_margin_delta_resident": row["repeated_margin"]
            - row["resident_margin"],
            "repeated_own_score_delta_resident": row["repeated_own_score"]
            - row["resident_own_score"],
            "repeated_opponent_score_delta_resident": row[
                "repeated_opponent_score"
            ]
            - row["resident_opponent_score"],
            "one_shot_margin_delta_resident": row["one_shot_margin"]
            - row["resident_margin"],
            "one_shot_own_score_delta_resident": row["one_shot_own_score"]
            - row["resident_own_score"],
            "one_shot_opponent_score_delta_resident": row[
                "one_shot_opponent_score"
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
            "unconstrained_margin_delta_resident": row["unconstrained_margin"]
            - row["resident_margin"],
            "unconstrained_own_score_delta_resident": row[
                "unconstrained_own_score"
            ]
            - row["resident_own_score"],
            "unconstrained_opponent_score_delta_resident": row[
                "unconstrained_opponent_score"
            ]
            - row["resident_opponent_score"],
            "repeated_opponent_excess": row["repeated_opponent_score"]
            - row["resident_opponent_score"],
            "one_shot_opponent_excess": row["one_shot_opponent_score"]
            - row["resident_opponent_score"],
            "unconstrained_opponent_excess": row[
                "unconstrained_opponent_score"
            ]
            - row["resident_opponent_score"],
        }
    )
    return row


def complete_rows(one_own: int = 170, repeated_own: int = 180) -> list[dict]:
    return [
        base_row(seed, seat, opponent, epoch, option, one_own, repeated_own)
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
                task_id = seed * 100 + seat * 10 + OPPONENTS.index(opponent)
                row = {
                    "seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "eligible": 1,
                    "start_turn": 50,
                    "prefix_attribution_failures": 0,
                    "start_history_mismatch": 0,
                    "start_cell_mismatch": 0,
                    "independent_resident_match": 1,
                    "resident_attribution_failures": 0,
                    "resident_history_mismatch": 0,
                    "resident_cell_mismatch": 0,
                    "resident_max_own_workers": 2,
                    "resident_terminal_hash": task_id + 1_000_000,
                }
                set_outcome(row, "resident", 100, 100, 301)
                rows.append(row)
    return rows


def test_constrained_order_rejects_infeasible_high_own_score() -> None:
    control = {
        "feasible": 1,
        "rollout_own_score": 100,
        "rollout_opponent_score": 100,
        "option": 0,
        "rollout_overridden_actions": 0,
        "plan_key": "control",
    }
    infeasible = {
        "feasible": 0,
        "rollout_own_score": 1000,
        "rollout_opponent_score": 200,
        "option": 1,
        "rollout_overridden_actions": 1,
        "plan_key": "a",
    }
    assert select_constrained([infeasible, control]) is control


def test_complete_resident_constrained_oracle_passes_frozen_gates() -> None:
    report = analyze(complete_rows(), complete_manifest(), TEST_SEEDS)
    assert report["integrity"]["complete"]
    assert report["resident_constrained_oracle"]["passes_all_gates"]
    assert report["confirmation_authorized"]
    assert (
        report["decision"]
        == "open_sealed_confirmation_export_constraint_scheduler_dataset"
    )


def test_false_feasibility_label_refuses_outcome_selection() -> None:
    rows = complete_rows()
    rows[12]["feasible"] = 1
    report = analyze(rows, complete_manifest(), TEST_SEEDS)
    assert not report["integrity"]["complete"]
    assert report["integrity"]["constraint_errors"] > 0
    assert report["decision"] == "invalid_integrity_do_not_select_outcomes"


def test_epoch_chain_corruption_refuses_outcome_selection() -> None:
    rows = complete_rows()
    for row in rows:
        if row["epoch"] == 1:
            row["epoch_turn"] += 1
    report = analyze(rows, complete_manifest(), TEST_SEEDS)
    assert not report["integrity"]["complete"]
    assert report["integrity"]["epoch_chain_errors"] > 0


def test_valid_but_weak_resident_overlay_is_rejected() -> None:
    report = analyze(
        complete_rows(one_own=130, repeated_own=150),
        complete_manifest(),
        TEST_SEEDS,
    )
    assert report["integrity"]["complete"]
    assert not report["resident_constrained_oracle"]["passes_all_gates"]
    assert not report["confirmation_authorized"]
    assert (
        report["decision"]
        == "reject_resident_overlay_advance_complete_learned_controller"
    )
