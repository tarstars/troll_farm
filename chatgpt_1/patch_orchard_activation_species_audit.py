#!/usr/bin/env python3
"""Patch the tracked orchard analyzer to its final exact-prefix/kill-safety form."""
from __future__ import annotations

from pathlib import Path

PATH = Path(__file__).with_name("orchard_activation_species_audit.py")


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def main() -> None:
    source = PATH.read_text(encoding="utf-8")

    source = replace_once(
        source,
        '''    if outputs[deployed_name] != recorded:
        mismatch = first_divergence(outputs[deployed_name], recorded)
        raise RuntimeError(
            f"game {replay['gameId']} deployed parity failed at turn "
            f"{None if mismatch is None else mismatch + 1}: "
            f"bot={outputs[deployed_name][mismatch or 0]} recorded={recorded[mismatch or 0]}"
        )
''',
        '''    deployed_mismatch_index = first_divergence(outputs[deployed_name], recorded)
''',
        "deployed parity",
    )

    source = replace_once(
        source,
        '''    activation_indices = {
        "current_apple": first_divergence(outputs["apple_current"], baseline),
        "apple_idle": first_divergence(outputs["apple_idle"], baseline),
        "banana": first_divergence(outputs["banana_current"], baseline),
        "banana_idle": first_divergence(outputs["banana_idle"], baseline),
    }
    # Only divergences through turn 100 can be orchard activation; fail closed on later first changes.
    for name, index in activation_indices.items():
        if index is not None and index >= 100:
            raise RuntimeError(f"game {replay['gameId']} {name} first diverges after orchard window")
''',
        '''    raw_activation_indices = {
        "current_apple": first_divergence(outputs["apple_current"], baseline),
        "apple_idle": first_divergence(outputs["apple_idle"], baseline),
        "banana": first_divergence(outputs["banana_current"], baseline),
        "banana_idle": first_divergence(outputs["banana_idle"], baseline),
    }
    activation_indices = {}
    for name, index in raw_activation_indices.items():
        exact_prefix = (
            index is not None
            and index < 100
            and (deployed_mismatch_index is None or index < deployed_mismatch_index)
        )
        # Once the deployed APPLE wrapper has diverged, other generated wrappers are no
        # longer on their own exact state trajectory. Measure those on no-orchard legs.
        if deployed_variant == "orchard" and name != "current_apple":
            exact_prefix = False
        activation_indices[name] = index if exact_prefix else None
''',
        "activation prefix",
    )

    source = replace_once(
        source,
        '''    "deployed_variant",
    "seat",
''',
        '''    "deployed_variant",
    "deployed_first_mismatch_turn",
    "seat",
''',
        "CSV deployed mismatch",
    )

    source = replace_once(
        source,
        '''    "enemy_eta",
    "apple_first_bank_eta",
''',
        '''    "enemy_eta",
    "apple_enemy_kill_eta",
    "banana_enemy_kill_eta",
    "apple_kill_safe",
    "banana_kill_safe",
    "apple_first_bank_eta",
''',
        "CSV kill safety",
    )

    source = replace_once(
        source,
        '''def state_fingerprint(map_data: dict[str, Any], state0: dict[str, Any], seat: int) -> tuple[str, str]:
''',
        '''def earliest_enemy_kill_eta(
    state: dict[str, Any],
    seat: int,
    mother: tuple[int, int],
    walkable: set[tuple[int, int]],
    species: str,
    plant_turn_offset: int,
) -> int | None:
    """Earliest adversarial kill under continuous chopping after arrival.

    MOVE consumes an action, a just-planted tree is not choppable on its plant turn, and
    plant growth happens after CHOP. This is a conservative mechanical safety bound, not
    a prediction that the real opponent will choose to attack.
    """
    base = {"APPLE": 8, "BANANA": 2}[species]
    slope = {"APPLE": 3, "BANANA": 1}[species]
    cooldown_effective = effective_cooldown(species)
    distances = bfs(walkable, [mother])
    arrivals: list[tuple[int, int]] = []
    for unit in state["units"]:
        if int(unit["player"]) != 1 - seat or int(unit["chop"]) <= 0:
            continue
        cell = (int(unit["x"]), int(unit["y"]))
        if cell not in distances:
            continue
        speed = max(1, int(unit["ms"]))
        arrival = (distances[cell] + speed - 1) // speed
        arrivals.append((arrival, int(unit["chop"])))
    if not arrivals:
        return None

    size = 0
    health = base
    cooldown = 0
    for offset in range(plant_turn_offset, TOTAL_TURNS + 1):
        if offset == plant_turn_offset:
            # PLANT resolves before CHOP, but new trees are excluded from that turn's
            # choppable-cell snapshot. The end-of-turn tick immediately creates size 1.
            size = 1
            health = base + slope
            cooldown = cooldown_effective
            continue

        damage = sum(chop for arrival, chop in arrivals if offset >= arrival + 1)
        health -= damage
        if health <= 0:
            return offset

        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0:
            if size < 4:
                size += 1
                health += slope
            cooldown = cooldown_effective
    return None


def state_fingerprint(map_data: dict[str, Any], state0: dict[str, Any], seat: int) -> tuple[str, str]:
''',
        "kill simulator insertion",
    )

    source = replace_once(
        source,
        '''    apple_eta = None
    banana_eta = None
    apple_safe = None
''',
        '''    apple_eta = None
    banana_eta = None
    apple_kill_eta = None
    banana_kill_eta = None
    apple_kill_safe = None
    banana_kill_safe = None
    apple_safe = None
''',
        "kill locals",
    )

    source = replace_once(
        source,
        '''        apple_eta = first_bank_eta("APPLE", travel_turns)
        banana_eta = first_bank_eta("BANANA", travel_turns)
        apple_safe = eta_enemy > apple_eta
        banana_safe = eta_enemy > banana_eta
''',
        '''        apple_eta = first_bank_eta("APPLE", travel_turns)
        banana_eta = first_bank_eta("BANANA", travel_turns)
        plant_turn_offset = travel_turns + 1
        apple_kill_eta = earliest_enemy_kill_eta(
            activation_state, seat, mother, board["walkable"], "APPLE", plant_turn_offset
        )
        banana_kill_eta = earliest_enemy_kill_eta(
            activation_state, seat, mother, board["walkable"], "BANANA", plant_turn_offset
        )
        # HARVEST resolves before CHOP. If the mother dies on the first harvest turn,
        # the carried fruit can still be dropped on the following turn.
        apple_kill_safe = apple_kill_eta is None or apple_kill_eta >= apple_eta - 1
        banana_kill_safe = banana_kill_eta is None or banana_kill_eta >= banana_eta - 1
        # Retain the older travel-only discriminator as a deliberately conservative audit.
        apple_safe = eta_enemy > apple_eta
        banana_safe = eta_enemy > banana_eta
''',
        "kill computation",
    )

    source = replace_once(
        source,
        '''        "deployed_variant": deployed_variant,
        "seat": seat,
''',
        '''        "deployed_variant": deployed_variant,
        "deployed_first_mismatch_turn": (
            None if deployed_mismatch_index is None else deployed_mismatch_index + 1
        ),
        "seat": seat,
''',
        "row deployed mismatch",
    )

    source = replace_once(
        source,
        '''        "enemy_eta": eta_enemy,
        "apple_first_bank_eta": apple_eta,
''',
        '''        "enemy_eta": eta_enemy,
        "apple_enemy_kill_eta": apple_kill_eta,
        "banana_enemy_kill_eta": banana_kill_eta,
        "apple_kill_safe": apple_kill_safe,
        "banana_kill_safe": banana_kill_safe,
        "apple_first_bank_eta": apple_eta,
''',
        "row kill fields",
    )

    source = replace_once(
        source,
        '''    payback_kept = [row for row in active if row["apple_payback_safe"]]
    payback_blocked = [row for row in active if not row["apple_payback_safe"]]
    combined = [row for row in active if row["starter_base_verb"] == "WAIT" and row["apple_payback_safe"]]
''',
        '''    payback_kept = [row for row in active if row["apple_payback_safe"]]
    payback_blocked = [row for row in active if not row["apple_payback_safe"]]
    kill_kept = [row for row in active if row["apple_kill_safe"]]
    kill_blocked = [row for row in active if not row["apple_kill_safe"]]
    combined = [row for row in active if row["starter_base_verb"] == "WAIT" and row["apple_kill_safe"]]
''',
        "summary kill groups",
    )

    source = replace_once(
        source,
        '''        "payback_safe_kept": len(payback_kept),
        "payback_safe_blocked": len(payback_blocked),
        "combined_kept": len(combined),
''',
        '''        "payback_safe_kept": len(payback_kept),
        "payback_safe_blocked": len(payback_blocked),
        "kill_safe_kept": len(kill_kept),
        "kill_safe_blocked": len(kill_blocked),
        "combined_kept": len(combined),
''',
        "summary kill counts",
    )

    source = replace_once(
        source,
        '''        "payback_safe_kept_outcomes": summarize_outcomes(payback_kept),
        "payback_safe_blocked_outcomes": summarize_outcomes(payback_blocked),
        "combined_kept_outcomes": summarize_outcomes(combined),
''',
        '''        "payback_safe_kept_outcomes": summarize_outcomes(payback_kept),
        "payback_safe_blocked_outcomes": summarize_outcomes(payback_blocked),
        "kill_safe_kept_outcomes": summarize_outcomes(kill_kept),
        "kill_safe_blocked_outcomes": summarize_outcomes(kill_blocked),
        "combined_kept_outcomes": summarize_outcomes(combined),
''',
        "summary kill outcomes",
    )

    source = replace_once(
        source,
        '''                    "payback_safe": bool(orchard_row["apple_payback_safe"]),
                    "margin_delta": int(orchard_row["margin"]) - int(no_row["margin"]),
''',
        '''                    "payback_safe": bool(orchard_row["apple_payback_safe"]),
                    "kill_safe": bool(orchard_row["apple_kill_safe"]),
                    "margin_delta": int(orchard_row["margin"]) - int(no_row["margin"]),
''',
        "pair kill field",
    )

    source = replace_once(
        source,
        '''        "activation_payback_unsafe": pair_summary(
            [row for row in pairs if row["activation"] and not row["payback_safe"]]
        ),
        "rows": pairs,
''',
        '''        "activation_payback_unsafe": pair_summary(
            [row for row in pairs if row["activation"] and not row["payback_safe"]]
        ),
        "activation_kill_safe": pair_summary(
            [row for row in pairs if row["activation"] and row["kill_safe"]]
        ),
        "activation_kill_unsafe": pair_summary(
            [row for row in pairs if row["activation"] and not row["kill_safe"]]
        ),
        "rows": pairs,
''',
        "pair kill summaries",
    )

    source = replace_once(
        source,
        '''        ("first-bank-safe kept", actual["payback_safe_kept_outcomes"]),
        ("first-bank-safe blocked", actual["payback_safe_blocked_outcomes"]),
        ("idle + first-bank-safe", actual["combined_kept_outcomes"]),
''',
        '''        ("enemy-arrival-after-bank kept", actual["payback_safe_kept_outcomes"]),
        ("enemy-arrival-after-bank blocked", actual["payback_safe_blocked_outcomes"]),
        ("adversarial-kill-safe kept", actual["kill_safe_kept_outcomes"]),
        ("adversarial-kill-safe blocked", actual["kill_safe_blocked_outcomes"]),
        ("idle + adversarial-kill-safe", actual["combined_kept_outcomes"]),
''',
        "report kill strata",
    )

    source = replace_once(
        source,
        '''        ("activation_payback_unsafe", "activation: first-bank unsafe"),
    ]:
''',
        '''        ("activation_payback_unsafe", "activation: enemy arrives before bank"),
        ("activation_kill_safe", "activation: survives continuous attack to first harvest"),
        ("activation_kill_unsafe", "activation: cannot survive continuous attack to first harvest"),
    ]:
''',
        "report pair kill strata",
    )

    source = replace_once(
        source,
        '''    payback_blocked = actual["payback_safe_blocked_outcomes"]
    payback_kept = actual["payback_safe_kept_outcomes"]
''',
        '''    payback_blocked = actual["payback_safe_blocked_outcomes"]
    payback_kept = actual["payback_safe_kept_outcomes"]
    kill_blocked = actual["kill_safe_blocked_outcomes"]
    kill_kept = actual["kill_safe_kept_outcomes"]
''',
        "direction kill locals",
    )

    source = replace_once(
        source,
        '''    if idle_direction:
''',
        '''    kill_direction = (
        kill_kept["mean_margin"] is not None
        and kill_blocked["mean_margin"] is not None
        and kill_kept["mean_margin"] > kill_blocked["mean_margin"]
        and kill_kept["catastrophe_rate"] <= kill_blocked["catastrophe_rate"]
    )
    if idle_direction:
''',
        "kill direction",
    )

    source = replace_once(
        source,
        '''        f"first-bank safety has {'favorable' if payback_direction else 'non-decisive'} direction. "
''',
        '''        f"travel-only first-bank safety has {'favorable' if payback_direction else 'non-decisive'} direction; "
        f"adversarial kill safety has {'favorable' if kill_direction else 'non-decisive'} direction. "
''',
        "verdict kill direction",
    )

    source = replace_once(
        source,
        '''            "first_bank_safety_favorable": payback_direction,
''',
        '''            "first_bank_safety_favorable": payback_direction,
            "adversarial_kill_safety_favorable": kill_direction,
''',
        "machine kill direction",
    )

    source = replace_once(
        source,
        '''            "deployed_command_parity_games": len(rows),
            "packages": 8,
''',
        '''            "deployed_command_parity_games": sum(
                row["deployed_first_mismatch_turn"] is None for row in rows
            ),
            "deployed_prefix_exact_through_turn_100_games": sum(
                row["deployed_first_mismatch_turn"] is None
                or int(row["deployed_first_mismatch_turn"]) > 100
                for row in rows
            ),
            "packages": 8,
''',
        "quality prefix counts",
    )

    source = replace_once(
        source,
        '''            f"- command-parity games: {report['quality']['deployed_command_parity_games']}/1280;",
''',
        '''            f"- full command-parity games: {report['quality']['deployed_command_parity_games']}/1280;",
            f"- exact deployed command prefix through the activation window: "
            f"{report['quality']['deployed_prefix_exact_through_turn_100_games']}/1280;",
''',
        "report quality",
    )

    PATH.write_text(source, encoding="utf-8")
    print(f"patched {PATH}: {len(source.encode())} bytes")


if __name__ == "__main__":
    main()
