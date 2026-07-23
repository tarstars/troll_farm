#!/usr/bin/env python3
"""Freeze and run the independent official-prefix crop activation replication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.opponent_crop_field_activation import (  # noqa: E402
    audit_game,
    CANDIDATE,
    CENSUS,
    instrument_crop_probe,
    RESIDENT,
    save,
)
from cgauto.recent_resident_field_census import game_row  # noqa: E402


MANIFEST = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-field-prefix-manifest-2026-07-18.json"
)
DISCOVERY_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-field-prefix-discovery-2026-07-18.json"
)
REPLICATION_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-field-prefix-replication-2026-07-18.json"
)
RESIDENT_AGENT_ID = 6559583
RESIDENT_SUBMISSION_ID = 41009991


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids_digest(ids: list[int]) -> str:
    encoded = json.dumps(ids, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def resident_player(battle: dict) -> dict | None:
    return next(
        (
            player
            for player in battle.get("players", [])
            if player.get("playerAgentId") == RESIDENT_AGENT_ID
            and player.get("submissionId") == RESIDENT_SUBMISSION_ID
        ),
        None,
    )


def build_manifest(battles: list[dict], fixed_recent_ids: list[int]) -> dict:
    old = set(fixed_recent_ids)
    positions = [
        index for index, battle in enumerate(battles) if battle.get("gameId") in old
    ]
    if len(positions) != 80 or positions != list(range(min(positions), max(positions) + 1)):
        raise ValueError("the frozen recent-80 corpus is not one contiguous battle-list block")
    older = [battle for battle in battles[max(positions) + 1 :] if battle.get("done")]
    if len(older) != 82:
        raise ValueError(f"expected 82 untouched older battles, found {len(older)}")
    if any(resident_player(battle) is None for battle in older):
        raise ValueError("untouched block contains a different resident agent or submission")
    ids = [int(battle["gameId"]) for battle in older]
    discovery = ids[:40]
    replication = ids[40:]
    return {
        "schema": 1,
        "scope": (
            "result-blind ID freeze from read-only battle metadata; 82 completed resident "
            "games immediately older than the Phase-19 recent-80 block"
        ),
        "battle_rows_listed": len(battles),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "resident_submission_id": RESIDENT_SUBMISSION_ID,
        "resident_source_sha256": digest(RESIDENT),
        "candidate_source_sha256": digest(CANDIDATE),
        "excluded_recent_80": {
            "count": len(fixed_recent_ids),
            "ids_sha256": ids_digest(fixed_recent_ids),
        },
        "discovery": {
            "count": len(discovery),
            "ids_sha256": ids_digest(discovery),
            "game_ids": discovery,
        },
        "replication": {
            "count": len(replication),
            "ids_sha256": ids_digest(replication),
            "game_ids": replication,
        },
    }


def freeze_manifest(path: Path) -> dict:
    from cgauto import battle_taxonomy as arena

    census = json.loads(CENSUS.read_text())
    fixed_ids = [row["game_id"] for row in census["rows"]]
    battles = arena.call(
        "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
    )
    payload = build_manifest(battles, fixed_ids)
    encoded = json.dumps(payload, indent=1) + "\n"
    if path.exists() and path.read_text() != encoded:
        raise RuntimeError("refusing to replace a differing frozen prefix manifest")
    save(path, payload)
    return payload


def stable_prefix(row: dict, continuation_turns: int = 10) -> bool:
    divergence = row["candidate_first_divergence_turn"]
    if not row["admissible_first_divergence"] or divergence is None:
        return False
    required_through = min(row["turns"], divergence + continuation_turns)
    mismatch = row["resident_first_mismatch_turn"]
    return mismatch is None or mismatch > required_through


def block_report(
    phase: str, rows: list[dict], failures: list[dict], expected: int, minimum: int
) -> dict:
    admissible = [row for row in rows if row["admissible_first_divergence"]]
    stable = [row for row in admissible if stable_prefix(row)]
    explained = [
        row
        for row in admissible
        if row["first_divergence_explanation"]
        and row["first_divergence_explanation"]["explained"]
    ]
    opponents = sorted({row["opponent"] for row in stable})
    checks = {
        "all_fixed_games_fetched_and_decoded": len(rows) == expected and not failures,
        "no_unknown_diff_updates": all(row["unknown_diff_updates"] == 0 for row in rows),
        "minimum_stable_prefix_activations": len(stable) >= minimum,
        "minimum_distinct_activated_opponents": len(opponents) >= 8,
        "all_admissible_divergences_explained": len(explained) == len(admissible),
        "no_production_stderr": True,
    }
    full_exact = sum(row["resident_full_stream_exact"] for row in rows)
    catastrophic = [row for row in stable if row["margin"] <= -100]
    return {
        "schema": 1,
        "phase": phase,
        "scope": (
            "independent official-state stable-prefix activation replication; read-only "
            "mechanism evidence, not counterfactual outcome replay"
        ),
        "games": len(rows),
        "fetch_failures": failures,
        "resident_full_stream_exact": full_exact,
        "admissible_activations": len(admissible),
        "stable_prefix_activations": len(stable),
        "stable_prefix_activation_rate": len(stable) / len(rows) if rows else 0,
        "distinct_stable_activated_opponents": len(opponents),
        "stable_activated_opponents": opponents,
        "explained_admissible_divergences": len(explained),
        "stable_catastrophic_activations": len(catastrophic),
        "stable_catastrophic_opponents": sorted({row["opponent"] for row in catastrophic}),
        "prospective_gate_checks": checks,
        "prospective_gate_passed": all(checks.values()),
        "rows": rows,
        "decision": {
            "continue_to_replication": phase == "discovery" and all(checks.values()),
            "draft_controlled_transfer_protocol": phase == "replication"
            and all(checks.values()),
            "play_or_submit": False,
        },
    }


def audit_block(
    phase: str,
    game_ids: list[int],
    resident_binary: Path,
    candidate_binary: Path,
    probe_binary: Path,
    minimum: int,
) -> dict:
    from cgauto import battle_taxonomy as arena

    rows = []
    failures = []
    for index, game_id in enumerate(game_ids, 1):
        try:
            game = arena.call("gameResult/findByGameId", [game_id, None])
            census_row = game_row(game, {})
            if census_row is None or census_row["agent_id"] != RESIDENT_AGENT_ID:
                raise ValueError("game does not decode as the frozen resident")
            rows.append(
                audit_game(
                    game,
                    census_row,
                    resident_binary,
                    candidate_binary,
                    probe_binary,
                )
            )
        except Exception as error:  # noqa: BLE001 - preserve complete read audit
            failures.append(
                {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
            )
        if index % 10 == 0 or index == len(game_ids):
            print(
                f"{phase}: audited {index}/{len(game_ids)} ({len(failures)} failures)",
                flush=True,
            )
    return block_report(phase, rows, failures, len(game_ids), minimum)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    manifest = freeze_manifest(args.manifest)
    print(
        f"frozen discovery={manifest['discovery']['count']} "
        f"({manifest['discovery']['ids_sha256'][:12]}), "
        f"replication={manifest['replication']['count']} "
        f"({manifest['replication']['ids_sha256'][:12]})"
    )
    if args.freeze_only:
        return 0

    with tempfile.TemporaryDirectory(prefix="crop-prefix-replication-") as directory:
        temp = Path(directory)
        resident_binary = temp / "resident"
        candidate_binary = temp / "candidate"
        probe_source = temp / "probe.rs"
        probe_binary = temp / "probe"
        probe_source.write_text(instrument_crop_probe(CANDIDATE.read_text()))
        compile_source(RESIDENT, resident_binary, "crop_prefix_resident")
        compile_source(CANDIDATE, candidate_binary, "crop_prefix_candidate")
        compile_source(probe_source, probe_binary, "crop_prefix_probe")
        discovery = audit_block(
            "discovery",
            manifest["discovery"]["game_ids"],
            resident_binary,
            candidate_binary,
            probe_binary,
            24,
        )
        save(DISCOVERY_OUTPUT, discovery)
        print(json.dumps({
            "phase": "discovery",
            "passed": discovery["prospective_gate_passed"],
            "stable_activations": discovery["stable_prefix_activations"],
            "opponents": discovery["distinct_stable_activated_opponents"],
            "full_exact": discovery["resident_full_stream_exact"],
            "checks": discovery["prospective_gate_checks"],
        }, indent=1))
        if not discovery["prospective_gate_passed"]:
            return 1
        replication = audit_block(
            "replication",
            manifest["replication"]["game_ids"],
            resident_binary,
            candidate_binary,
            probe_binary,
            25,
        )
        save(REPLICATION_OUTPUT, replication)
        print(json.dumps({
            "phase": "replication",
            "passed": replication["prospective_gate_passed"],
            "stable_activations": replication["stable_prefix_activations"],
            "opponents": replication["distinct_stable_activated_opponents"],
            "full_exact": replication["resident_full_stream_exact"],
            "checks": replication["prospective_gate_checks"],
        }, indent=1))
        return 0 if replication["prospective_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
