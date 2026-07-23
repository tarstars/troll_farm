from cgauto.analyze_d35b_factorized_joint_bundle_oracle import (
    INTEGER_FIELDS,
    OPPONENTS,
    analyze,
    parse_plan_key,
    plan_key_error,
    select_oracle,
)


def encoded_job(role: str, unit_id: int, index: int) -> str:
    if role == "keep":
        return f"keep:{unit_id}:-:-:-"
    if role == "bank":
        return f"bank:{unit_id}:-:-:-"
    target = f"{index},1"
    plant = f"{index},2" if role == "renew" else "-"
    fruit = "3" if role in {"renew", "harvest_bank"} else "-"
    return f"{role}:{unit_id}:{target}:{plant}:{fruit}"


def fill_outcome(row: dict, own: int, opponent: int) -> None:
    row.update(
        {
            "own_score": own,
            "opponent_score": opponent,
            "margin": own - opponent,
            "margin_delta_farm": own - opponent,
            "own_score_delta_farm": own - 100,
            "opponent_score_delta_farm": opponent - 100,
            "margin_delta_resident": own - opponent,
            "own_score_delta_resident": own - 100,
            "opponent_score_delta_resident": opponent - 100,
        }
    )


def base_row(seed: int, seat: int, opponent: str, checkpoint: int) -> dict:
    row = {field: 0 for field in INTEGER_FIELDS}
    row.update(
        {
            "seed": seed,
            "seat": seat,
            "opponent": opponent,
            "checkpoint": checkpoint,
            "root_turn": checkpoint,
            "plan_key": "control",
            "role_tuple": "control",
            "train_goal": "none",
            "statuses": "",
            "bundle_end_turn": checkpoint,
            "root_plan_count": 32,
            "has_renew": 1,
            "has_fell": 1,
            "has_mine": 1,
            "has_train_goal": 1,
            "own_wood": 25,
            "opponent_wood": 25,
            "own_workers": 2,
            "opponent_workers": 2,
            "max_own_workers": 2,
            "terminal_turn": 301,
            "farm_own_score": 100,
            "farm_opponent_score": 100,
            "farm_margin": 0,
            "farm_own_wood": 25,
            "farm_opponent_wood": 25,
            "farm_terminal_turn": 301,
            "resident_own_score": 100,
            "resident_opponent_score": 100,
            "resident_margin": 0,
            "resident_own_wood": 25,
            "resident_opponent_wood": 25,
            "control_identity_match": 1,
        }
    )
    fill_outcome(row, 100, 100)
    return row


def root_rows(seed: int, seat: int, opponent: str, checkpoint: int) -> list[dict]:
    control = base_row(seed, seat, opponent, checkpoint)
    rows = [control]
    option = 1
    keep_key = encoded_job("keep", 0, 0) + "+" + encoded_job("keep", 1, 0)
    for goal in ("producer_2211", "chopper_2202"):
        row = dict(control)
        row.update(
            {
                "option": option,
                "plan_key": f"{keep_key}|train={goal}",
                "role_tuple": "keep+keep",
                "train_goal": goal,
                "statuses": "0:keep,1:keep",
                "bundle_end_turn": checkpoint + 1,
            }
        )
        fill_outcome(row, 90, 100)
        rows.append(row)
        option += 1

    opponent_index = OPPONENTS.index(opponent)
    selected_role = (
        "renew"
        if (seed + seat + opponent_index + checkpoint) % 2 == 0
        else "fell_bank"
    )
    other_roles = [
        "renew",
        "fell_bank",
        "mine_bank",
        "harvest_bank",
        "bank",
        "renew",
        "fell_bank",
        "mine_bank",
        "harvest_bank",
    ]
    roles = [selected_role, *other_roles]
    for index, role in enumerate(roles, start=1):
        unit_key = encoded_job(role, 0, index) + "+" + encoded_job("keep", 1, 0)
        for goal in ("none", "producer_2211", "chopper_2202"):
            row = dict(control)
            row.update(
                {
                    "option": option,
                    "plan_key": f"{unit_key}|train={goal}",
                    "role_tuple": f"{role}+keep",
                    "train_goal": goal,
                    "predicted_eta": 10,
                    "predicted_reward": 20,
                    "rate_score": 2000,
                    "statuses": "0:completed,1:keep",
                    "overridden_actions": 5,
                    "bundle_end_turn": checkpoint + 10,
                }
            )
            if index == 1 and goal == "none":
                fill_outcome(row, 190, 30)
            else:
                fill_outcome(row, 90, 100)
            rows.append(row)
            option += 1
    assert option == 33
    return rows


def complete_rows() -> list[dict]:
    return [
        row
        for seed in range(100, 110)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for checkpoint in (50, 100)
        for row in root_rows(seed, seat, opponent, checkpoint)
    ]


def scenario_manifest_rows(zero_task: tuple[int, int, str] | None = None) -> list[dict]:
    rows = []
    for seed in range(100, 110):
        for seat in (0, 1):
            for opponent in OPPONENTS:
                task = seed, seat, opponent
                checkpoints = [] if task == zero_task else [50, 100]
                rows.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "opponent": opponent,
                        "root_count": len(checkpoints),
                        "captured_checkpoints": checkpoints,
                        "root_turns": list(checkpoints),
                        "farm_own_score": 100,
                        "farm_opponent_score": 100,
                        "farm_margin": 0,
                        "farm_own_workers": 1 if task == zero_task else 2,
                        "farm_opponent_workers": 2,
                        "farm_terminal_turn": 301,
                        "resident_own_score": 100,
                        "resident_opponent_score": 100,
                        "resident_margin": 0,
                        "resident_own_workers": 2,
                        "resident_opponent_workers": 2,
                        "resident_terminal_turn": 301,
                    }
                )
    return rows


def test_plan_key_parser_and_collision_detection() -> None:
    jobs, train = parse_plan_key(
        "renew:0:3,4:5,6:2+keep:1:-:-:-|train=producer_2211"
    )
    assert train == "producer_2211"
    assert jobs[0]["target"] == (3, 4)
    row = root_rows(100, 0, "resident", 50)[3]
    row["plan_key"] = (
        "fell_bank:0:3,4:-:-+renew:1:3,4:5,6:2|train=none"
    )
    row["role_tuple"] = "fell_bank+renew"
    assert plan_key_error(row) == "acquisition_collision"


def test_oracle_tie_break_prefers_control_then_cost_and_no_train() -> None:
    control = {
        "margin": 10,
        "option": 0,
        "overridden_actions": 0,
        "train_goal": "none",
        "plan_key": "control",
    }
    tied = {
        "margin": 10,
        "option": 1,
        "overridden_actions": 0,
        "train_goal": "none",
        "plan_key": "a",
    }
    assert select_oracle([tied, control]) is control
    costly = dict(tied, margin=11, overridden_actions=3, plan_key="b")
    cheap_train = dict(
        tied,
        margin=11,
        overridden_actions=2,
        train_goal="producer_2211",
        plan_key="c",
    )
    cheap_no_train = dict(cheap_train, train_goal="none", plan_key="d")
    assert select_oracle([costly, cheap_train]) is cheap_train
    assert select_oracle([cheap_train, cheap_no_train]) is cheap_no_train


def test_complete_high_value_oracle_passes_every_frozen_gate() -> None:
    report = analyze(complete_rows(), seed_start=100, seed_count=10)
    assert report["integrity"]["complete"]
    assert report["oracle"]["passes_all_representation_gates"]
    assert report["confirmation_authorized"]
    assert report["decision"] == "open_sealed_confirmation"
    assert len(report["oracle"]["role_tuples_selected_at_least_10_times"]) == 2


def test_integrity_failure_prevents_outcome_selection() -> None:
    rows = complete_rows()
    rows[1]["invalid_direct_commands"] = 1
    report = analyze(rows, seed_start=100, seed_count=10)
    assert not report["integrity"]["complete"]
    assert report["decision"] == "invalid_integrity_do_not_select_outcomes"
    assert "oracle" not in report


def test_valid_but_valueless_grammar_is_rejected() -> None:
    rows = complete_rows()
    for row in rows:
        if row["own_score"] == 190:
            fill_outcome(row, 100, 100)
    report = analyze(rows, seed_start=100, seed_count=10)
    assert report["integrity"]["complete"]
    assert not report["oracle"]["passes_all_representation_gates"]
    assert not report["confirmation_authorized"]
    assert report["decision"] == "reject_bundle_grammar_leave_confirmation_sealed"


def test_manifest_distinguishes_ineligible_root_from_dropped_task() -> None:
    zero_task = (100, 0, "resident")
    rows = [
        row
        for row in complete_rows()
        if (row["seed"], row["seat"], row["opponent"]) != zero_task
    ]
    report = analyze(
        rows,
        seed_start=100,
        seed_count=10,
        scenario_manifest_rows=scenario_manifest_rows(zero_task),
    )
    assert report["scenario_manifest"]["complete"]
    assert report["scenario_manifest"]["eligible_roots"] == 318
    assert report["integrity"]["complete"]
