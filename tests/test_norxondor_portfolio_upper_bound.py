from __future__ import annotations

from cgauto.norxondor_portfolio_upper_bound import (
    RESIDENT,
    THREE_WORKER,
    analyze,
    evaluate,
    fit_confident_opponent_selector,
    fit_opponent_selector,
)


def row(candidate: str, opponent: str, seed: int, seat: int, margin: int) -> dict:
    return {
        "candidate": candidate,
        "opponent": opponent,
        "seed": seed,
        "seat": seat,
        "margin": margin,
    }


def tiny_grid() -> list[dict]:
    rows = []
    for seed in (10, 11, 12, 13):
        for seat in (0, 1):
            for opponent, resident_margin, alternative_margin in (
                ("adaptive", 5, 1),
                ("compact", 2, 8),
            ):
                rows.append(row(RESIDENT, opponent, seed, seat, resident_margin))
                rows.append(row(THREE_WORKER, opponent, seed, seat, alternative_margin))
    return rows


def test_opponent_selector_preserves_complementary_policies() -> None:
    rows = tiny_grid()
    selector = fit_opponent_selector(rows)
    report = evaluate(rows, selector)

    assert selector == {"adaptive": RESIDENT, "compact": THREE_WORKER}
    assert report["frozen_opponent_selector"]["delta_vs_resident"]["mean"] == 3
    assert report["cell_oracle"]["mean_gain_vs_resident"] == 3


def test_discovery_mapping_is_applied_unchanged_to_validation() -> None:
    payload = analyze(tiny_grid(), discovery_seed_count=2)

    assert payload["split"] == {
        "discovery_seeds": [10, 11],
        "validation_seeds": [12, 13],
    }
    assert payload["opening_signature_gate"]["passed"] is True
    assert payload["decision"]["build_observable_opening_signature_study"] is True
    assert payload["decision"]["build_online_selector"] is False


def test_confidence_selector_requires_a_positive_lower_bound() -> None:
    selector, evidence = fit_confident_opponent_selector(tiny_grid())

    assert selector == {"adaptive": RESIDENT, "compact": THREE_WORKER}
    assert evidence["adaptive"]["normal_95_lower"] < 0
    assert evidence["compact"]["normal_95_lower"] > 0


def test_confidence_gate_requires_only_selected_branches_to_hold() -> None:
    payload = analyze(tiny_grid(), discovery_seed_count=2, selector_method="lower95")

    assert payload["opening_signature_gate"]["passed"] is True
