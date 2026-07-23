from cgauto.analyze_d35c_provenance_competitive_bundle_oracle import (
    INTEGER_FIELDS,
    OPPONENTS,
    analyze,
    plan_error,
    select_oracle,
)


TEST_SEEDS = tuple(range(100, 120))


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


def root_control(seed: int, seat: int, opponent: str, checkpoint: int) -> dict:
    row = {field: 0 for field in INTEGER_FIELDS}
    row.update(
        {
            "seed": seed,
            "seat": seat,
            "opponent": opponent,
            "checkpoint": checkpoint,
            "root_turn": checkpoint,
            "catalog": "control",
            "plan_key": "control",
            "role_tuple": "control",
            "target_owners": "none+none",
            "statuses": "",
            "bundle_end_turn": checkpoint,
            "root_plan_count": 16,
            "generic_plan_count": 8,
            "competitive_plan_count": 8,
            "has_competitive_target": 1,
            "has_opponent_fell": 1,
            "has_opponent_renew_or_harvest": 1,
            "root_natural_plants": 5,
            "root_own_plants": 3,
            "root_opponent_plants": 4,
            "root_ambiguous_plants": 0,
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


def plan_row(control: dict, option: int, catalog: str, index: int, role: str) -> dict:
    row = dict(control)
    target = index if catalog == "generic" else index + 100
    owner = "natural" if catalog == "generic" else "opponent"
    fruit = "3" if role in {"harvest_bank", "renew"} else "-"
    plant = f"{target},2" if role == "renew" else "-"
    row.update(
        {
            "option": option,
            "catalog": catalog,
            "plan_key": (
                f"{role}:0:{target},1:{plant}:{fruit}+keep:1:-:-:-|train=none"
            ),
            "role_tuple": f"{role}+keep",
            "target_owners": f"{owner}+none",
            "predicted_eta": 10,
            "predicted_reward": 20,
            "rate_score": 2000,
            "statuses": "0:completed,1:keep",
            "overridden_actions": 5,
            "bundle_end_turn": control["checkpoint"] + 10,
            "competitive_target_count": int(catalog == "competitive"),
            "opponent_target_count": int(catalog == "competitive"),
        }
    )
    fill_outcome(row, 90, 100)
    return row


def root_rows(seed: int, seat: int, opponent: str, checkpoint: int) -> list[dict]:
    control = root_control(seed, seat, opponent, checkpoint)
    rows = [control]
    for index in range(1, 9):
        role = "fell_bank" if index % 2 else "harvest_bank"
        row = plan_row(control, index, "generic", index, role)
        if index == 1:
            fill_outcome(row, 190, 90)
        rows.append(row)
    selected_role = (
        "fell_bank"
        if (seed + seat + OPPONENTS.index(opponent) + checkpoint) % 2
        else "harvest_bank"
    )
    for index in range(1, 9):
        role = selected_role if index == 1 else (
            "fell_bank" if index % 2 else "harvest_bank"
        )
        row = plan_row(control, index + 8, "competitive", index, role)
        if index == 1:
            fill_outcome(row, 170, 50)
        rows.append(row)
    return rows


def complete_rows() -> list[dict]:
    return [
        row
        for seed in TEST_SEEDS
        for seat in (0, 1)
        for opponent in OPPONENTS
        for checkpoint in (50, 100)
        for row in root_rows(seed, seat, opponent, checkpoint)
    ]


def complete_manifest() -> list[dict]:
    return [
        {
            "seed": seed,
            "seat": seat,
            "opponent": opponent,
            "root_count": 2,
            "captured_checkpoints": [50, 100],
            "root_turns": [50, 100],
            "attribution_failures": 0,
            "farm_own_score": 100,
            "farm_opponent_score": 100,
            "farm_margin": 0,
            "farm_own_workers": 2,
            "farm_opponent_workers": 2,
            "farm_terminal_turn": 301,
            "resident_own_score": 100,
            "resident_opponent_score": 100,
            "resident_margin": 0,
            "resident_own_workers": 2,
            "resident_opponent_workers": 2,
            "resident_terminal_turn": 301,
        }
        for seed in TEST_SEEDS
        for seat in (0, 1)
        for opponent in OPPONENTS
    ]


def test_competitive_plan_encoding_and_collision_check() -> None:
    row = root_rows(100, 0, "resident", 50)[9]
    assert plan_error(row) is None
    row["plan_key"] = (
        "fell_bank:0:3,1:-:-+harvest_bank:1:3,1:-:3|train=none"
    )
    row["role_tuple"] = "fell_bank+harvest_bank"
    row["target_owners"] = "opponent+opponent"
    row["competitive_target_count"] = 2
    row["opponent_target_count"] = 2
    assert plan_error(row) == "acquisition_collision"


def test_oracle_tie_prefers_control_then_fewer_overrides() -> None:
    control = {
        "margin": 10,
        "option": 0,
        "overridden_actions": 0,
        "plan_key": "control",
    }
    tied = {
        "margin": 10,
        "option": 1,
        "overridden_actions": 0,
        "plan_key": "a",
    }
    assert select_oracle([tied, control]) is control
    costly = dict(tied, margin=11, overridden_actions=3, plan_key="b")
    cheap = dict(tied, margin=11, overridden_actions=2, plan_key="c")
    assert select_oracle([costly, cheap]) is cheap


def test_complete_provenance_oracle_passes_all_frozen_gates() -> None:
    report = analyze(
        complete_rows(), complete_manifest(), expected_seeds=TEST_SEEDS
    )
    assert report["integrity"]["complete"]
    assert report["oracles"]["passes_all_gates"]
    assert report["confirmation_authorized"]
    assert report["decision"] == "open_sealed_confirmation"


def test_integrity_error_refuses_outcome_selection() -> None:
    rows = complete_rows()
    rows[1]["invalid_direct_commands"] = 1
    report = analyze(rows, complete_manifest(), expected_seeds=TEST_SEEDS)
    assert not report["integrity"]["complete"]
    assert report["decision"] == "invalid_integrity_do_not_select_outcomes"
    assert "oracles" not in report


def test_valid_but_noncompetitive_extension_is_rejected() -> None:
    rows = complete_rows()
    for row in rows:
        if row["catalog"] == "competitive" and row["own_score"] == 170:
            fill_outcome(row, 90, 100)
    report = analyze(rows, complete_manifest(), expected_seeds=TEST_SEEDS)
    assert report["integrity"]["complete"]
    assert not report["oracles"]["passes_all_gates"]
    assert report["decision"] == "reject_provenance_extension_advance_repeated_control"
