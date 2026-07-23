from __future__ import annotations

from cgauto.d14_resident_residual_smoke import analyze
from cgauto.rl_resident_residual_env import OPPONENTS


def payload(policy: str, random_delta: int = 0) -> dict:
    rows = []
    for scenario in range(240):
        margin = 10 + (random_delta if policy == "random" else 0)
        rows.append(
            {
                "scenario": scenario,
                "map_seed": scenario // 12,
                "seat": (scenario // 6) % 2,
                "opponent": OPPONENTS[scenario % 6],
                "turn": 301,
                "return": margin / 100,
                "margin": margin,
                "wood_edge": 2,
                "workers": 2,
                "opponent_workers": 2,
                "overrides": int(policy == "random"),
                "residual_attempts": int(policy == "random"),
                "rejected_actions": 0,
            }
        )
    return {
        "policy": policy,
        "rows": rows,
        "mean_wood_edge": 2,
        "transitions": 1000,
        "transitions_per_second": 1000,
        "mask_legal_min": 1,
        "mask_legal_max": 7,
        "keep_missing_observations": 0,
        "override_episode_rate": int(policy == "random"),
        "residual_attempt_episode_rate": int(policy == "random"),
        "rejected_actions": 0,
    }


def references() -> dict[tuple[int, int, str], dict]:
    return {
        (seed, seat, opponent): {
            "margin": 10,
            "wood_edge": 2,
            "terminal_turn": 301,
            "workers": 2,
            "opponent_workers": 2,
        }
        for seed in range(20)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def test_qualifies_exact_keep_and_harmful_random(tmp_path):
    keep_path = tmp_path / "keep.json"
    random_path = tmp_path / "random.json"
    reference_path = tmp_path / "reference.tsv"
    keep_path.write_text("keep\n")
    random_path.write_text("random\n")
    reference_path.write_text("reference\n")
    result = analyze(
        payload("keep"),
        payload("random", random_delta=-1),
        references(),
        keep_path,
        random_path,
        [reference_path],
    )

    assert result["keep"]["parity_matches"] == 240
    assert result["random"]["changed_terminal_margins"] == 240
    assert result["qualification"]["qualified_for_short_ppo_signal_run"] is True
