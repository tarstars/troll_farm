#!/usr/bin/env python3
"""Freeze and run the independent secure-orchard official-prefix replication."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.make_idle_harvest_probe import instrument_minified  # noqa: E402
from cgauto.recent_resident_field_census import game_row  # noqa: E402
from cgauto.secure_orchard_conversion_audit import (  # noqa: E402
    audit_game,
    CENSUS,
    RESIDENT,
    save,
    summarize,
)


REPO = Path(__file__).resolve().parent.parent
MANIFEST = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "secure-orchard-conversion-replication-manifest-2026-07-19.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "secure-orchard-conversion-replication-2026-07-19.json"
)
RESIDENT_AGENT_ID = 6560353
RESIDENT_SUBMISSION_ID = 41012883


def ids_digest(ids: list[int]) -> str:
    return hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()


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


def build_manifest(battles: list[dict], recent_ids: list[int]) -> dict:
    recent = set(recent_ids)
    positions = [
        index for index, battle in enumerate(battles) if battle.get("gameId") in recent
    ]
    if len(positions) != 80 or positions != list(range(80)):
        raise ValueError("recent-80 ids are not the first contiguous battle-list block")
    older = [battle for battle in battles[80:] if battle.get("done")]
    if len(older) != 80:
        raise ValueError(f"expected exactly 80 older finished battles, found {len(older)}")
    if any(resident_player(battle) is None for battle in older):
        raise ValueError("older block contains a different resident agent or submission")
    ids = [int(battle["gameId"]) for battle in older]
    return {
        "schema": 1,
        "scope": (
            "result-blind metadata freeze of the 80 exact-resident battles immediately older "
            "than the consumed recent-80 discovery corpus"
        ),
        "battle_rows_listed": len(battles),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "resident_submission_id": RESIDENT_SUBMISSION_ID,
        "excluded_recent_80": {
            "count": len(recent_ids),
            "ids_sha256": ids_digest(recent_ids),
        },
        "replication": {
            "count": len(ids),
            "ids_sha256": ids_digest(ids),
            "game_ids": ids,
        },
    }


def freeze_manifest(path: Path) -> dict:
    from cgauto import battle_taxonomy as arena

    recent = json.loads(CENSUS.read_text())
    recent_ids = [int(row["game_id"]) for row in recent["rows"]]
    battles = arena.call(
        "gamesPlayersRanking/findLastBattlesByTestSessionHandle", [arena.TSH, None]
    )
    payload = build_manifest(battles, recent_ids)
    encoded = json.dumps(payload, indent=1) + "\n"
    if path.exists() and path.read_text() != encoded:
        raise RuntimeError("refusing to replace a differing frozen replication manifest")
    save(path, payload)
    return payload


def analyze_replication(
    rows: list[dict], failures: list[dict], manifest: dict
) -> dict:
    activated = [row for row in rows if row["post_seed_replacement_forces"] > 0]
    opponents = sorted({row["opponent"] for row in activated})
    losses = [row for row in activated if row["margin"] < 0]
    post_forces = sum(row["post_seed_replacement_forces"] for row in activated)
    checks = {
        "all_frozen_games_fetched_and_decoded": len(rows) == 80 and not failures,
        "all_probe_streams_stdout_neutral": all(
            row["probe_resident_stdout_equal"] for row in rows
        ),
        "zero_unknown_diff_updates": all(
            row["unknown_diff_updates"] == 0 for row in rows
        ),
        "minimum_full_resident_reproductions": sum(
            row["resident_full_stream_exact"] for row in rows
        )
        >= 40,
        "all_admissible_forces_are_ripe_apple": all(
            row["all_forces_on_ripe_apple"] for row in rows
        ),
        "minimum_sustained_activated_games": len(activated) >= 5,
        "minimum_distinct_activated_opponents": len(opponents) >= 3,
        "minimum_post_seed_replacement_forces": post_forces >= 200,
        "minimum_activated_losses": len(losses) >= 2,
    }
    passed = all(checks.values())
    return {
        "schema": 1,
        "scope": (
            "independent read-only exact-prefix replication of sustained secure-orchard "
            "reservation; not a counterfactual release outcome"
        ),
        "manifest": manifest,
        "fetch_failures": failures,
        "integrity_and_replication_checks": checks,
        "passed": passed,
        "aggregate": summarize(rows),
        "full_resident_reproductions": sum(
            row["resident_full_stream_exact"] for row in rows
        ),
        "sustained_activated_games": len(activated),
        "distinct_activated_opponents": opponents,
        "post_seed_replacement_forces": post_forces,
        "activated_losses": len(losses),
        "activated_loss_games": [row["game_id"] for row in losses],
        "rows": rows,
        "decision": {
            "open_fresh_local_release_discovery": passed,
            "construct_or_submit_candidate": False,
            "reason": (
                "mechanism breadth and downside independently replicate"
                if passed
                else "one or more frozen integrity/replication gates failed"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--freeze-only", action="store_true")
    parser.add_argument("--fetch-workers", type=int, default=8)
    parser.add_argument("--audit-workers", type=int, default=16)
    args = parser.parse_args()
    if not 1 <= args.fetch_workers <= 20 or not 1 <= args.audit_workers <= 20:
        parser.error("worker counts must be between 1 and 20")
    manifest = freeze_manifest(args.manifest)
    print(
        f"frozen {manifest['replication']['count']} games "
        f"({manifest['replication']['ids_sha256'][:16]})"
    )
    if args.freeze_only:
        return 0

    from cgauto import battle_taxonomy as arena

    game_ids = manifest["replication"]["game_ids"]
    games: dict[int, dict] = {}
    failures = []

    def fetch(game_id: int) -> tuple[int, dict]:
        return game_id, arena.call("gameResult/findByGameId", [game_id, None])

    with ThreadPoolExecutor(max_workers=args.fetch_workers) as executor:
        futures = {executor.submit(fetch, game_id): game_id for game_id in game_ids}
        for index, future in enumerate(as_completed(futures), 1):
            game_id = futures[future]
            try:
                key, game = future.result()
                games[key] = game
            except Exception as error:  # noqa: BLE001 - retain the read audit
                failures.append(
                    {
                        "game_id": game_id,
                        "stage": "fetch",
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
            if index % 20 == 0 or index == len(futures):
                print(f"fetched {index}/80 ({len(failures)} failures)", flush=True)

    with tempfile.TemporaryDirectory(prefix="orchard-conversion-replication-") as directory:
        temp = Path(directory)
        resident_binary = temp / "resident"
        probe_source = temp / "probe.rs"
        probe_binary = temp / "probe"
        probe_source.write_text(instrument_minified(RESIDENT.read_text()))
        compile_source(RESIDENT, resident_binary, "orchard_replication_resident")
        compile_source(probe_source, probe_binary, "orchard_replication_probe")

        def run(game_id: int) -> dict:
            census_row = game_row(games[game_id], {})
            if census_row is None or census_row["agent_id"] != RESIDENT_AGENT_ID:
                raise ValueError("game does not decode as the frozen exact resident")
            return audit_game(
                games[game_id], census_row, resident_binary, probe_binary
            )

        rows = []
        eligible = [game_id for game_id in game_ids if game_id in games]
        with ThreadPoolExecutor(max_workers=args.audit_workers) as executor:
            futures = {executor.submit(run, game_id): game_id for game_id in eligible}
            for index, future in enumerate(as_completed(futures), 1):
                game_id = futures[future]
                try:
                    rows.append(future.result())
                except Exception as error:  # noqa: BLE001 - retain the audit failure
                    failures.append(
                        {
                            "game_id": game_id,
                            "stage": "audit",
                            "error": f"{type(error).__name__}: {error}",
                        }
                    )
                if index % 20 == 0 or index == len(futures):
                    print(
                        f"audited {index}/{len(futures)} ({len(failures)} failures)",
                        flush=True,
                    )
    rows.sort(key=lambda row: game_ids.index(row["game_id"]))
    payload = analyze_replication(rows, failures, manifest)
    save(args.output, payload)
    print(
        json.dumps(
            {
                "passed": payload["passed"],
                "checks": payload["integrity_and_replication_checks"],
                "aggregate": payload["aggregate"],
                "activated_opponents": payload["distinct_activated_opponents"],
                "activated_loss_games": payload["activated_loss_games"],
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
