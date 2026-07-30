#!/usr/bin/env python3
"""M1: audit observable Legend rating dynamics from immutable D61p snapshots."""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


SNAPSHOT_IDS = (
    "20260721T105508Z-d61p",
    "20260727T130712Z-d61p",
    "20260728T050038Z-d61p",
    "20260728T050038Z-d61p-wide21to50",
    "20260728T110709Z-d61p-wide",
    "20260729T021701Z-d61p-wide",
    "20260730T021701Z-d61p-wide",
)
MANIFEST_SCHEMA = "troll-farm-d61p-snapshot-v1"
SCORE_TOLERANCE = 1e-12
RESIDENT_AGENT_ID = 6561795


def parse_time(value: Any) -> dt.datetime:
    if isinstance(value, bool):
        raise ValueError(f"invalid timestamp: {value!r}")
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds /= 1000.0
        return dt.datetime.fromtimestamp(seconds, tz=dt.timezone.utc)
    if isinstance(value, str):
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            dt.timezone.utc
        )
    raise ValueError(f"invalid timestamp: {value!r}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def leaderboard_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("users"), list):
        return [row for row in payload["users"] if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    raise ValueError("leaderboard payload has no users list")


def exact_agent_id(row: dict[str, Any], key: str = "agentId") -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise ValueError(f"invalid {key}: {value!r}")
    return int(value)


@dataclass(frozen=True)
class BattleObservation:
    snapshot_id: str
    agent_id: int
    requested_at: str
    response_sha256: str
    game_ids: frozenset[int]
    ordered_game_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class GameAgent:
    agent_id: int
    score: float
    rank: int
    result: float
    opponent_scores: tuple[float, ...]


@dataclass(frozen=True)
class GameSummary:
    game_id: int
    response_sha256: str
    agents: dict[int, GameAgent]


@dataclass(frozen=True)
class Epoch:
    agent_id: int
    score: float
    game_ids: tuple[int, ...]


def verify_manifest_file(
    snapshot_dir: Path,
    manifest: dict[str, Any],
    relative_path: str,
) -> str:
    record = manifest.get("files", {}).get(relative_path)
    if not isinstance(record, dict) or not isinstance(record.get("sha256"), str):
        raise ValueError(
            f"{snapshot_dir.name}: manifest has no hash for {relative_path}"
        )
    path = snapshot_dir / relative_path
    actual = sha256_file(path)
    if actual != record["sha256"]:
        raise ValueError(
            f"{snapshot_dir.name}: hash mismatch for {relative_path}: "
            f"{actual} != {record['sha256']}"
        )
    return actual


def request_times(
    requests: Sequence[dict[str, Any]],
) -> tuple[dict[int, tuple[str, str]], list[str]]:
    out: dict[int, tuple[str, str]] = {}
    errors: list[str] = []
    for row in requests:
        if row.get("service") != "gamesPlayersRanking/findLastBattlesByAgentId":
            continue
        context = row.get("context")
        if not isinstance(context, dict) or context.get("source_agent") is None:
            continue
        agent_id = int(context["source_agent"])
        when = row.get("requested_at_utc")
        response_hash = row.get("response_sha256")
        if not isinstance(when, str) or not isinstance(response_hash, str):
            errors.append(f"agent {agent_id}: incomplete battle request record")
            continue
        current = out.get(agent_id)
        candidate = (when, response_hash)
        if current is not None and current != candidate:
            errors.append(f"agent {agent_id}: duplicate battle request records")
        out[agent_id] = candidate
    return out, errors


def load_sources(snapshot_root: Path) -> dict[str, Any]:
    source_hashes: dict[str, dict[str, str]] = {}
    leaderboard_observations: list[dict[str, Any]] = []
    battle_observations: list[BattleObservation] = []
    game_index: dict[int, dict[str, Any]] = {}
    failed_game_index_rows: list[dict[str, Any]] = []
    integrity_errors: list[str] = []
    request_errors: list[str] = []

    for snapshot_id in SNAPSHOT_IDS:
        snapshot_dir = snapshot_root / snapshot_id
        manifest = read_json(snapshot_dir / "manifest.json")
        if manifest.get("schema") != MANIFEST_SCHEMA or not manifest.get("complete"):
            raise ValueError(f"{snapshot_id}: incomplete or wrong-schema manifest")

        verified: dict[str, str] = {}
        for relative in ("leaderboard.json", "requests.json", "games.json"):
            verified[relative] = verify_manifest_file(
                snapshot_dir, manifest, relative
            )
        source_hashes[snapshot_id] = verified

        requests = read_json(snapshot_dir / "requests.json")
        battle_requests, errors = request_times(requests)
        request_errors.extend(f"{snapshot_id}: {error}" for error in errors)

        leaderboard = read_json(snapshot_dir / "leaderboard.json")
        rows: dict[int, dict[str, Any]] = {}
        for row in leaderboard_rows(leaderboard):
            try:
                agent_id = exact_agent_id(row)
                rows[agent_id] = {
                    "agent_id": agent_id,
                    "score": float(row["score"]),
                    "rank": row.get("localRank", row.get("rank")),
                    "creation_time": row.get("creationTime"),
                    "update_time": row.get("updateTime"),
                }
            except (KeyError, TypeError, ValueError):
                continue
        leaderboard_observations.append(
            {
                "snapshot_id": snapshot_id,
                "completed_at_utc": manifest["completed_at_utc"],
                "leaderboard_sha256": verified["leaderboard.json"],
                "rows": rows,
            }
        )

        for relative in sorted(manifest.get("files", {})):
            if not relative.startswith("battles/") or not relative.endswith(".json"):
                continue
            verified[relative] = verify_manifest_file(
                snapshot_dir, manifest, relative
            )
            agent_id = int(Path(relative).stem)
            request = battle_requests.get(agent_id)
            if request is None:
                request_errors.append(
                    f"{snapshot_id}: agent {agent_id}: no request timestamp"
                )
                continue
            when, response_hash = request
            if response_hash != verified[relative]:
                integrity_errors.append(
                    f"{snapshot_id}: agent {agent_id}: request/file hash mismatch"
                )
            payload = read_json(snapshot_dir / relative)
            ordered_ids = tuple(
                int(row["gameId"])
                for row in payload
                if isinstance(row, dict) and row.get("gameId") is not None
            )
            ids = frozenset(ordered_ids)
            if len(ids) != len(payload):
                integrity_errors.append(
                    f"{snapshot_id}: agent {agent_id}: duplicate/invalid battle row"
                )
            battle_observations.append(
                BattleObservation(
                    snapshot_id=snapshot_id,
                    agent_id=agent_id,
                    requested_at=when,
                    response_sha256=response_hash,
                    game_ids=ids,
                    ordered_game_ids=ordered_ids,
                )
            )

        index_rows = read_json(snapshot_dir / "games.json")
        for row in index_rows:
            game_id = int(row["game_id"])
            response_hash = row.get("response_sha256")
            cache_file = row["cache_file"]
            sources = {
                int(source["agent_id"])
                for source in row.get("sources", [])
                if source.get("agent_id") is not None
            }
            if (
                row.get("status") not in {"fetched", "already_present"}
                or not isinstance(response_hash, str)
                or not response_hash
            ):
                failed_game_index_rows.append(
                    {
                        "snapshot_id": snapshot_id,
                        "game_id": game_id,
                        "status": row.get("status"),
                        "source_agents": sorted(sources),
                    }
                )
                continue
            prior = game_index.get(game_id)
            if prior is None:
                game_index[game_id] = {
                    "game_id": game_id,
                    "response_sha256": response_hash,
                    "cache_file": cache_file,
                    "sources": sources,
                    "snapshots": {snapshot_id},
                }
            else:
                if (
                    prior["response_sha256"] != response_hash
                    or prior["cache_file"] != cache_file
                ):
                    integrity_errors.append(
                        f"game {game_id}: inconsistent cached response"
                    )
                prior["sources"].update(sources)
                prior["snapshots"].add(snapshot_id)

    return {
        "source_hashes": source_hashes,
        "leaderboards": leaderboard_observations,
        "battle_observations": battle_observations,
        "game_index": game_index,
        "failed_game_index_rows": failed_game_index_rows,
        "integrity_errors": integrity_errors,
        "request_errors": request_errors,
    }


def decode_game(payload: dict[str, Any], expected_hash: str) -> GameSummary:
    game_id = int(payload["gameId"])
    ranks = payload.get("ranks")
    agents = payload.get("agents")
    if not isinstance(ranks, list) or not isinstance(agents, list):
        raise ValueError(f"game {game_id}: missing ranks/agents")
    parsed: list[tuple[int, int, float]] = []
    for row in agents:
        index = int(row["index"])
        rank = int(ranks[index])
        parsed.append((exact_agent_id(row), rank, float(row["score"])))
    best = min(rank for _, rank, _ in parsed)
    winners = sum(rank == best for _, rank, _ in parsed)
    out: dict[int, GameAgent] = {}
    for agent_id, rank, score in parsed:
        result = 1.0 if rank == best and winners == 1 else 0.5 if rank == best else 0.0
        out[agent_id] = GameAgent(
            agent_id=agent_id,
            score=score,
            rank=rank,
            result=result,
            opponent_scores=tuple(
                other_score
                for other_id, _, other_score in parsed
                if other_id != agent_id
            ),
        )
    return GameSummary(
        game_id=game_id,
        response_sha256=expected_hash,
        agents=out,
    )


def load_games(
    snapshot_root: Path,
    index: dict[int, dict[str, Any]],
    battle_observations: Sequence[BattleObservation],
) -> tuple[dict[int, GameSummary], list[str], list[int], int]:
    wanted_by_agent: dict[int, set[int]] = collections.defaultdict(set)
    for observation in battle_observations:
        wanted_by_agent[observation.agent_id].update(observation.game_ids)
    wanted = set().union(*wanted_by_agent.values()) if wanted_by_agent else set()
    raw_root = snapshot_root.parent
    summaries: dict[int, GameSummary] = {}
    integrity_errors: list[str] = []
    unavailable_game_ids: list[int] = []
    bytes_hashed = 0
    for game_id in sorted(wanted):
        row = index.get(game_id)
        if row is None:
            unavailable_game_ids.append(game_id)
            continue
        path = raw_root / row["cache_file"]
        if not path.is_file():
            integrity_errors.append(
                f"game {game_id}: missing raw file {row['cache_file']}"
            )
            continue
        bytes_hashed += path.stat().st_size
        actual = sha256_file(path)
        if actual != row["response_sha256"]:
            integrity_errors.append(f"game {game_id}: raw response hash mismatch")
            continue
        try:
            summary = decode_game(read_json(path), actual)
        except (KeyError, TypeError, ValueError, IndexError) as error:
            integrity_errors.append(f"game {game_id}: decode error: {error}")
            continue
        if summary.game_id != game_id:
            integrity_errors.append(f"game {game_id}: payload id {summary.game_id}")
            continue
        summaries[game_id] = summary
    return summaries, integrity_errors, unavailable_game_ids, bytes_hashed


def coalesced_leaderboard_intervals(
    observations: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for observation in observations:
        digest = observation["leaderboard_sha256"]
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        unique.append(observation)
    unique.sort(key=lambda row: parse_time(row["completed_at_utc"]))
    intervals: list[dict[str, Any]] = []
    for before, after in zip(unique, unique[1:]):
        for agent_id in sorted(before["rows"].keys() & after["rows"].keys()):
            left = before["rows"][agent_id]
            right = after["rows"][agent_id]
            delta = right["score"] - left["score"]
            try:
                advanced = parse_time(right["update_time"]) > parse_time(
                    left["update_time"]
                )
            except (TypeError, ValueError, OSError, OverflowError):
                advanced = False
            intervals.append(
                {
                    "agent_id": agent_id,
                    "from_snapshot": before["snapshot_id"],
                    "to_snapshot": after["snapshot_id"],
                    "score_before": left["score"],
                    "score_after": right["score"],
                    "score_delta": delta,
                    "score_changed": abs(delta) > SCORE_TOLERANCE,
                    "update_advanced": advanced,
                }
            )
    return unique, intervals


def build_battle_diagnostics(
    observations: Sequence[BattleObservation],
) -> tuple[list[dict[str, Any]], dict[int, list[BattleObservation]]]:
    by_agent: dict[int, list[BattleObservation]] = collections.defaultdict(list)
    for observation in observations:
        by_agent[observation.agent_id].append(observation)
    rows: list[dict[str, Any]] = []
    for agent_id, agent_observations in by_agent.items():
        agent_observations.sort(key=lambda row: parse_time(row.requested_at))
        previous: BattleObservation | None = None
        for observation in agent_observations:
            current = observation.game_ids
            rows.append(
                {
                    "agent_id": agent_id,
                    "snapshot_id": observation.snapshot_id,
                    "requested_at_utc": observation.requested_at,
                    "length": len(current),
                    "minimum_game_id": min(current) if current else None,
                    "maximum_game_id": max(current) if current else None,
                    "added_since_prior": (
                        len(current - previous.game_ids) if previous else None
                    ),
                    "dropped_since_prior": (
                        len(previous.game_ids - current) if previous else None
                    ),
                    "overlap_with_prior": (
                        len(previous.game_ids & current) if previous else None
                    ),
                }
            )
            previous = observation
    return rows, by_agent


def score_epochs(
    agent_id: int,
    game_ids: Iterable[int],
    games: dict[int, GameSummary],
) -> tuple[list[Epoch], list[int]]:
    observations: list[tuple[int, float]] = []
    missing: list[int] = []
    for game_id in sorted(set(game_ids)):
        game = games.get(game_id)
        if game is None or agent_id not in game.agents:
            missing.append(game_id)
            continue
        observations.append((game_id, game.agents[agent_id].score))
    epochs: list[Epoch] = []
    for game_id, score in observations:
        if not epochs or abs(epochs[-1].score - score) > SCORE_TOLERANCE:
            epochs.append(Epoch(agent_id=agent_id, score=score, game_ids=(game_id,)))
        else:
            prior = epochs[-1]
            epochs[-1] = Epoch(
                agent_id=agent_id,
                score=prior.score,
                game_ids=prior.game_ids + (game_id,),
            )
    return epochs, missing


def epoch_outcomes(
    epoch: Epoch,
    games: dict[int, GameSummary],
) -> dict[str, Any]:
    wins = losses = ties = 0
    expected_residuals: dict[str, float] = {}
    scales = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
    for scale in scales:
        expected_residuals[str(scale)] = 0.0
    opponent_scores: list[float] = []
    for game_id in epoch.game_ids:
        record = games[game_id].agents[epoch.agent_id]
        if record.result == 1.0:
            wins += 1
        elif record.result == 0.0:
            losses += 1
        else:
            ties += 1
        opponent_scores.extend(record.opponent_scores)
        for scale in scales:
            expected = statistics.mean(
                1.0 / (1.0 + 10.0 ** ((opponent - record.score) / scale))
                for opponent in record.opponent_scores
            )
            expected_residuals[str(scale)] += record.result - expected
    return {
        "games": len(epoch.game_ids),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "net_wins": wins - losses,
        "opponent_score_mean": (
            statistics.mean(opponent_scores) if opponent_scores else None
        ),
        "elo_residuals": expected_residuals,
    }


def complete_epoch(
    epoch_index: int,
    epochs: Sequence[Epoch],
    observations: Sequence[BattleObservation],
    games: dict[int, GameSummary] | None = None,
) -> bool:
    if epoch_index <= 0 or epoch_index >= len(epochs) - 1:
        return False
    previous_ids = set(epochs[epoch_index - 1].game_ids)
    epoch_ids = set(epochs[epoch_index].game_ids)
    next_ids = set(epochs[epoch_index + 1].game_ids)
    for observation in observations:
        if not (
            epoch_ids.issubset(observation.game_ids)
            and bool(previous_ids & observation.game_ids)
            and bool(next_ids & observation.game_ids)
        ):
            continue
        if games is None or not observation.ordered_game_ids:
            return True
        positions = {
            game_id: position
            for position, game_id in enumerate(observation.ordered_game_ids)
        }
        previous_positions = [
            positions[game_id] for game_id in previous_ids if game_id in positions
        ]
        epoch_positions = [
            positions[game_id] for game_id in epoch_ids if game_id in positions
        ]
        next_positions = [
            positions[game_id] for game_id in next_ids if game_id in positions
        ]
        previous_median = statistics.median(previous_positions)
        epoch_median = statistics.median(epoch_positions)
        next_median = statistics.median(next_positions)
        if next_median < epoch_median < previous_median:
            left = max(next_positions)
            right = min(previous_positions)
        elif previous_median < epoch_median < next_median:
            left = max(previous_positions)
            right = min(next_positions)
        else:
            continue
        span = observation.ordered_game_ids[min(left, right) : max(left, right) + 1]
        if all(
            game_id in games
            and epochs[epoch_index].agent_id in games[game_id].agents
            for game_id in span
        ):
            return True
    return False


def build_transitions(
    by_agent: dict[int, list[BattleObservation]],
    games: dict[int, GameSummary],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, list[Epoch]]]:
    transitions: list[dict[str, Any]] = []
    epoch_rows: list[dict[str, Any]] = []
    epochs_by_agent: dict[int, list[Epoch]] = {}
    for agent_id, observations in sorted(by_agent.items()):
        union_ids = set().union(*(row.game_ids for row in observations))
        epochs, missing = score_epochs(agent_id, union_ids, games)
        epochs_by_agent[agent_id] = epochs
        for index, epoch in enumerate(epochs):
            outcomes = epoch_outcomes(epoch, games)
            epoch_rows.append(
                {
                    "agent_id": agent_id,
                    "epoch_index": index,
                    "score": epoch.score,
                    "first_game_id": min(epoch.game_ids),
                    "last_game_id": max(epoch.game_ids),
                    **outcomes,
                    "varied_outcomes": outcomes["wins"] > 0
                    and outcomes["losses"] > 0,
                    "missing_agent_games": len(missing),
                }
            )
        for index in range(len(epochs) - 1):
            epoch = epochs[index]
            outcomes = epoch_outcomes(epoch, games)
            next_outcomes = epoch_outcomes(epochs[index + 1], games)
            transitions.append(
                {
                    "agent_id": agent_id,
                    "from_epoch": index,
                    "to_epoch": index + 1,
                    "from_score": epoch.score,
                    "to_score": epochs[index + 1].score,
                    "score_delta": epochs[index + 1].score - epoch.score,
                    **outcomes,
                    "internal": index > 0,
                    "outcome_complete": complete_epoch(
                        index, epochs, observations, games
                    ),
                    "next_games": next_outcomes["games"],
                    "next_wins": next_outcomes["wins"],
                    "next_losses": next_outcomes["losses"],
                    "next_ties": next_outcomes["ties"],
                    "next_net_wins": next_outcomes["net_wins"],
                    "next_opponent_score_mean": next_outcomes[
                        "opponent_score_mean"
                    ],
                    "next_elo_residuals": next_outcomes["elo_residuals"],
                    "next_outcome_complete": complete_epoch(
                        index + 1, epochs, observations, games
                    ),
                }
            )
    return transitions, epoch_rows, epochs_by_agent


def leaderboard_alignment(
    leaderboards: Sequence[dict[str, Any]],
    battle_observations: Sequence[BattleObservation],
    games: dict[int, GameSummary],
) -> dict[str, Any]:
    leaderboard_by_snapshot = {
        row["snapshot_id"]: row for row in leaderboards
    }
    comparisons: list[dict[str, Any]] = []
    for observation in battle_observations:
        if not observation.game_ids:
            continue
        game_id = max(observation.game_ids)
        game = games.get(game_id)
        leaderboard = leaderboard_by_snapshot[observation.snapshot_id]
        ladder_row = leaderboard["rows"].get(observation.agent_id)
        if (
            game is None
            or observation.agent_id not in game.agents
            or ladder_row is None
        ):
            continue
        raw_score = game.agents[observation.agent_id].score
        ladder_score = ladder_row["score"]
        comparisons.append(
            {
                "snapshot_id": observation.snapshot_id,
                "agent_id": observation.agent_id,
                "game_id": game_id,
                "game_score": raw_score,
                "leaderboard_score": ladder_score,
                "absolute_rounded_difference": abs(round(raw_score, 2) - ladder_score),
                "matches_to_0_01": abs(round(raw_score, 2) - ladder_score) <= 0.0100001,
            }
        )
    return {
        "comparisons": len(comparisons),
        "matches_to_0_01": sum(row["matches_to_0_01"] for row in comparisons),
        "match_rate": (
            statistics.mean(row["matches_to_0_01"] for row in comparisons)
            if comparisons
            else 0.0
        ),
        "median_absolute_rounded_difference": (
            statistics.median(
                row["absolute_rounded_difference"] for row in comparisons
            )
            if comparisons
            else None
        ),
        "maximum_absolute_rounded_difference": (
            max(row["absolute_rounded_difference"] for row in comparisons)
            if comparisons
            else None
        ),
        "rows": comparisons,
    }


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-10:
            augmented[column][column] += 1e-8
            pivot = column
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row], augmented[column]
                )
            ]
    return [augmented[row][-1] for row in range(size)]


def ordinary_least_squares(
    rows: Sequence[dict[str, Any]],
    fields: Sequence[str],
) -> list[float]:
    dimensions = len(fields) + 1
    xtx = [[0.0] * dimensions for _ in range(dimensions)]
    xty = [0.0] * dimensions
    for row in rows:
        features = [1.0] + [float(row[field]) for field in fields]
        target = float(row["score_delta"])
        for left in range(dimensions):
            xty[left] += features[left] * target
            for right in range(dimensions):
                xtx[left][right] += features[left] * features[right]
    for index in range(dimensions):
        xtx[index][index] += 1e-10
    return solve_linear(xtx, xty)


def predict_linear(
    row: dict[str, Any],
    fields: Sequence[str],
    coefficients: Sequence[float],
) -> float:
    return coefficients[0] + sum(
        coefficient * float(row[field])
        for field, coefficient in zip(fields, coefficients[1:])
    )


def metrics(actual: Sequence[float], predicted: Sequence[float]) -> dict[str, float]:
    residuals = [prediction - truth for truth, prediction in zip(actual, predicted)]
    absolute = [abs(value) for value in residuals]
    return {
        "mae": statistics.mean(absolute),
        "median_absolute_error": statistics.median(absolute),
        "bias": statistics.mean(residuals),
        "maximum_absolute_error": max(absolute),
        "zero_change_baseline_mae": statistics.mean(abs(value) for value in actual),
    }


def cross_validate_linear(
    rows: Sequence[dict[str, Any]],
    fields: Sequence[str],
) -> dict[str, Any]:
    agents = sorted({int(row["agent_id"]) for row in rows})
    predictions: list[tuple[dict[str, Any], float]] = []
    for held_agent in agents:
        train = [row for row in rows if int(row["agent_id"]) != held_agent]
        held = [row for row in rows if int(row["agent_id"]) == held_agent]
        if not train:
            continue
        coefficients = ordinary_least_squares(train, fields)
        predictions.extend(
            (row, predict_linear(row, fields, coefficients)) for row in held
        )
    actual = [float(row["score_delta"]) for row, _ in predictions]
    predicted = [prediction for _, prediction in predictions]
    full_coefficients = ordinary_least_squares(rows, fields)
    by_agent: dict[str, dict[str, float]] = {}
    for agent_id in agents:
        held = [
            (row, prediction)
            for row, prediction in predictions
            if int(row["agent_id"]) == agent_id
        ]
        residuals = [
            prediction - float(row["score_delta"]) for row, prediction in held
        ]
        by_agent[str(agent_id)] = {
            "held_transitions": len(held),
            "mean_residual": statistics.mean(residuals),
        }
    return {
        "fields": list(fields),
        "coefficients": full_coefficients,
        "validation": metrics(actual, predicted),
        "held_predictions": [
            {
                "agent_id": row["agent_id"],
                "from_epoch": row.get("from_epoch"),
                "actual": row["score_delta"],
                "predicted": prediction,
                "residual": prediction - row["score_delta"],
            }
            for row, prediction in predictions
        ],
        "by_agent": by_agent,
    }


def cross_validate_elo(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    scales = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
    k_values = tuple(index / 1000.0 for index in range(1, 501))
    agents = sorted({int(row["agent_id"]) for row in rows})

    def best_parameters(train: Sequence[dict[str, Any]]) -> tuple[float, float]:
        best: tuple[float, float, float] | None = None
        for scale in scales:
            field = str(scale)
            for k_value in k_values:
                error = statistics.mean(
                    abs(
                        k_value * row["elo_residuals"][field]
                        - row["score_delta"]
                    )
                    for row in train
                )
                candidate = (error, scale, k_value)
                if best is None or candidate < best:
                    best = candidate
        assert best is not None
        return best[1], best[2]

    predictions: list[tuple[dict[str, Any], float]] = []
    folds: dict[str, dict[str, float]] = {}
    for held_agent in agents:
        train = [row for row in rows if int(row["agent_id"]) != held_agent]
        held = [row for row in rows if int(row["agent_id"]) == held_agent]
        scale, k_value = best_parameters(train)
        folds[str(held_agent)] = {"scale": scale, "k": k_value}
        predictions.extend(
            (row, k_value * row["elo_residuals"][str(scale)]) for row in held
        )
    scale, k_value = best_parameters(rows)
    actual = [float(row["score_delta"]) for row, _ in predictions]
    predicted = [prediction for _, prediction in predictions]
    by_agent: dict[str, dict[str, float]] = {}
    for agent_id in agents:
        held = [
            (row, prediction)
            for row, prediction in predictions
            if int(row["agent_id"]) == agent_id
        ]
        residuals = [
            prediction - float(row["score_delta"]) for row, prediction in held
        ]
        by_agent[str(agent_id)] = {
            "held_transitions": len(held),
            "mean_residual": statistics.mean(residuals),
        }
    return {
        "scale": scale,
        "k": k_value,
        "fold_parameters": folds,
        "validation": metrics(actual, predicted),
        "held_predictions": [
            {
                "agent_id": row["agent_id"],
                "from_epoch": row.get("from_epoch"),
                "actual": row["score_delta"],
                "predicted": prediction,
                "residual": prediction - row["score_delta"],
            }
            for row, prediction in predictions
        ],
        "by_agent": by_agent,
    }


def model_gate(model: dict[str, Any], rows: Sequence[dict[str, Any]]) -> dict[str, bool]:
    validation = model["validation"]
    agent_residuals = model["by_agent"].values()
    signs = True
    if model.get("fields") == ["wins", "losses", "ties"]:
        coefficients = model["coefficients"]
        signs = coefficients[1] > 0 and coefficients[2] < 0
    if model.get("fields") == ["net_wins"]:
        signs = model["coefficients"][1] > 0
    return {
        "mae_at_most_0_05": validation["mae"] <= 0.05,
        "mae_half_baseline": validation["mae"]
        <= 0.5 * validation["zero_change_baseline_mae"],
        "median_at_most_0_02": validation["median_absolute_error"] <= 0.02,
        "agent_mean_residual_at_most_0_10": all(
            row["held_transitions"] < 3 or abs(row["mean_residual"]) <= 0.10
            for row in agent_residuals
        ),
        "coherent_signs": signs,
        "positive_and_negative_changes": any(
            row["score_delta"] > 0 for row in rows
        )
        and any(row["score_delta"] < 0 for row in rows),
    }


def fit_candidate_models(
    rows: Sequence[dict[str, Any]],
) -> tuple[dict[str, Any], str | None, dict[str, bool]]:
    agents = {int(row["agent_id"]) for row in rows}
    if len(agents) < 2 or len(rows) < 4:
        return {}, None, {}
    models = {
        "affine": cross_validate_linear(rows, ("wins", "losses", "ties")),
        "net_wins": cross_validate_linear(rows, ("net_wins",)),
        "elo_like": cross_validate_elo(rows),
    }
    selected_name = min(
        models, key=lambda name: models[name]["validation"]["mae"]
    )
    for model in models.values():
        model["recovery_gates"] = model_gate(model, rows)
    return (
        models,
        selected_name,
        models[selected_name]["recovery_gates"],
    )


def next_epoch_convention_rows(
    transitions: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for transition in transitions:
        if not transition["next_outcome_complete"]:
            continue
        out.append(
            {
                **transition,
                "games": transition["next_games"],
                "wins": transition["next_wins"],
                "losses": transition["next_losses"],
                "ties": transition["next_ties"],
                "net_wins": transition["next_net_wins"],
                "opponent_score_mean": transition["next_opponent_score_mean"],
                "elo_residuals": transition["next_elo_residuals"],
            }
        )
    return out


def compact_model_summary(models: dict[str, Any]) -> dict[str, Any]:
    return {
        name: {
            "validation": model["validation"],
            "recovery_gates": model["recovery_gates"],
        }
        for name, model in models.items()
    }


def summarize(
    sources: dict[str, Any],
    games: dict[int, GameSummary],
    game_integrity_errors: list[str],
    unavailable_game_ids: list[int],
    raw_bytes_hashed: int,
) -> dict[str, Any]:
    unique_leaderboards, leaderboard_intervals = coalesced_leaderboard_intervals(
        sources["leaderboards"]
    )
    battle_rows, by_agent = build_battle_diagnostics(
        sources["battle_observations"]
    )
    transitions, epoch_rows, epochs_by_agent = build_transitions(by_agent, games)
    complete = [row for row in transitions if row["outcome_complete"]]
    internal = [row for row in transitions if row["internal"]]
    alignment = leaderboard_alignment(
        sources["leaderboards"], sources["battle_observations"], games
    )

    varied_epochs = sum(
        row["varied_outcomes"] and row["games"] >= 5 for row in epoch_rows
    )
    semantics_resolved = (
        alignment["comparisons"] >= 20
        and alignment["match_rate"] >= 0.80
        and varied_epochs >= 10
    )
    complete_agents = {row["agent_id"] for row in complete}
    both_outcomes = (
        sum(row["wins"] for row in complete) > 0
        and sum(row["losses"] for row in complete) > 0
    )
    both_directions = any(row["score_delta"] > 0 for row in complete) and any(
        row["score_delta"] < 0 for row in complete
    )
    complete_rate = len(complete) / len(internal) if internal else 0.0
    integrity_errors = (
        sources["integrity_errors"]
        + sources["request_errors"]
        + game_integrity_errors
    )

    source_full_eligible = (
        not integrity_errors
        and semantics_resolved
        and len(complete) >= 30
        and len(complete_agents) >= 10
        and complete_rate >= 0.80
        and both_outcomes
        and both_directions
    )
    source_partial = (
        not integrity_errors
        and semantics_resolved
        and len(complete) >= 20
        and len(complete_agents) >= 8
        and both_outcomes
    )

    models, selected_name, selected_gates = fit_candidate_models(complete)
    next_convention = next_epoch_convention_rows(transitions)
    (
        next_models,
        next_selected_name,
        next_selected_gates,
    ) = fit_candidate_models(next_convention)

    sensitivity_observations = [
        row
        for row in sources["battle_observations"]
        if row.snapshot_id != SNAPSHOT_IDS[0]
    ]
    _, sensitivity_by_agent = build_battle_diagnostics(sensitivity_observations)
    sensitivity_transitions, _, _ = build_transitions(
        sensitivity_by_agent, games
    )
    sensitivity_complete = [
        row for row in sensitivity_transitions if row["outcome_complete"]
    ]
    (
        sensitivity_models,
        sensitivity_selected,
        _,
    ) = fit_candidate_models(sensitivity_complete)

    recovered = (
        source_full_eligible
        and selected_name is not None
        and all(selected_gates.values())
    )
    if recovered:
        support = "FULL"
        verdict = "RECOVERED"
    elif source_partial or source_full_eligible:
        support = "PARTIAL"
        verdict = "DESCRIPTIVE_ONLY"
    else:
        support = "UNIDENTIFIABLE"
        verdict = "UNIDENTIFIABLE"

    leaderboard_counts = collections.Counter()
    for row in leaderboard_intervals:
        leaderboard_counts["intervals"] += 1
        leaderboard_counts["score_changed"] += row["score_changed"]
        leaderboard_counts["update_advanced"] += row["update_advanced"]
        leaderboard_counts["score_changed_and_update_advanced"] += (
            row["score_changed"] and row["update_advanced"]
        )

    epoch_counts = collections.Counter(len(rows) for rows in epochs_by_agent.values())
    result = {
        "schema": "troll-farm-m1-rating-system-dynamics-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "protocol": "docs/m1-rating-system-dynamics-protocol-v2-2026-07-30.md",
        "snapshot_ids": list(SNAPSHOT_IDS),
        "source_hashes": sources["source_hashes"],
        "source_integrity": {
            "pass": not integrity_errors,
            "errors": integrity_errors,
            "indexed_games": len(sources["game_index"]),
            "decoded_source_games": len(games),
            "raw_bytes_hashed": raw_bytes_hashed,
            "failed_game_index_rows": len(sources["failed_game_index_rows"]),
            "unindexed_battle_games": len(unavailable_game_ids),
            "unindexed_battle_game_examples": unavailable_game_ids[:20],
        },
        "leaderboard_panel": {
            "raw_observations": len(sources["leaderboards"]),
            "coalesced_observations": len(unique_leaderboards),
            "duplicate_hashes_coalesced": len(sources["leaderboards"])
            - len(unique_leaderboards),
            **dict(leaderboard_counts),
        },
        "battle_panel": {
            "observations": len(sources["battle_observations"]),
            "agents": len(by_agent),
            "length_min": min(row["length"] for row in battle_rows),
            "length_median": statistics.median(
                row["length"] for row in battle_rows
            ),
            "length_max": max(row["length"] for row in battle_rows),
            "rows_with_drops": sum(
                (row["dropped_since_prior"] or 0) > 0 for row in battle_rows
            ),
            "rows_with_additions": sum(
                (row["added_since_prior"] or 0) > 0 for row in battle_rows
            ),
            "diagnostics": battle_rows,
        },
        "score_semantics": {
            "leaderboard_alignment": alignment,
            "constant_score_epochs_with_at_least_5_games_and_both_outcomes": varied_epochs,
            "prior_epoch_to_next_score_convention_resolved": semantics_resolved,
            "reason": (
                "game-associated score aligns with contemporaneous leaderboard rounding "
                "and stays constant across outcome-varying batches"
                if semantics_resolved
                else "stored evidence does not independently resolve score-field convention"
            ),
            "alternative_next_epoch_convention": {
                "outcome_complete_transitions": len(next_convention),
                "selected_model": next_selected_name,
                "selected_model_gates": next_selected_gates,
                "models": compact_model_summary(next_models),
            },
        },
        "score_epochs": {
            "agents_by_epoch_count": {
                str(count): agents for count, agents in sorted(epoch_counts.items())
            },
            "rows": epoch_rows,
        },
        "transitions": {
            "all": len(transitions),
            "internal": len(internal),
            "outcome_complete": len(complete),
            "complete_rate_of_internal": complete_rate,
            "complete_agents": len(complete_agents),
            "complete_wins": sum(row["wins"] for row in complete),
            "complete_losses": sum(row["losses"] for row in complete),
            "complete_ties": sum(row["ties"] for row in complete),
            "both_score_directions": both_directions,
            "rows": transitions,
        },
        "identification": {
            "source_full_eligible_before_model": source_full_eligible,
            "source_partial_eligible_before_model": source_partial,
            "support": support,
            "verdict": verdict,
            "selected_model": selected_name,
            "selected_model_gates": selected_gates,
        },
        "models": models,
        "sensitivity_excluding_20260721_snapshot": {
            "outcome_complete_transitions": len(sensitivity_complete),
            "complete_agents": len(
                {row["agent_id"] for row in sensitivity_complete}
            ),
            "selected_model": sensitivity_selected,
            "models": compact_model_summary(sensitivity_models),
        },
        "wins_per_plus_one": None,
        "minimum_additional_collection": (
            None
            if recovered
            else (
                "Preserve the exact membership and documented pre/post score for each "
                "platform recomputation, or obtain the platform formula: this panel "
                "already has broad transition coverage, but wins/losses and the tested "
                "Elo-like residual do not predict held-agent score changes."
                if source_full_eligible
                else
                "Collect timestamped, paginated battle-event deltas bracketing every "
                "score update, preserve the documented pre/post-update score, and obtain "
                "at least 30 complete transitions across 10 agents with both directions."
            )
        ),
        "resident": {
            "agent_id": RESIDENT_AGENT_ID,
            "battle_observations": len(by_agent.get(RESIDENT_AGENT_ID, [])),
            "score_epochs": len(epochs_by_agent.get(RESIDENT_AGENT_ID, [])),
            "complete_transitions": sum(
                row["agent_id"] == RESIDENT_AGENT_ID for row in complete
            ),
        },
    }
    return result


def markdown_report(result: dict[str, Any]) -> str:
    identification = result["identification"]
    source = result["source_integrity"]
    leaderboard = result["leaderboard_panel"]
    battle = result["battle_panel"]
    transitions = result["transitions"]
    semantics = result["score_semantics"]
    alternative = semantics["alternative_next_epoch_convention"]
    sensitivity = result["sensitivity_excluding_20260721_snapshot"]
    lines = [
        "# M1 rating-system dynamics — result",
        "",
        f"Verdict: **{identification['verdict']}** "
        f"(support: **{identification['support']}**).",
        "",
        "## Source and panel",
        "",
        f"- Source integrity: {'PASS' if source['pass'] else 'FAIL'}; "
        f"{source['decoded_source_games']:,} raw games decoded and "
        f"{source['raw_bytes_hashed']:,} bytes hash-verified.",
        f"- Raw coverage limits: {source['failed_game_index_rows']} recorded fetch "
        f"failures and {source['unindexed_battle_games']:,} battle IDs without an "
        "admitted raw result; bracket completeness excludes them.",
        f"- Leaderboards: {leaderboard['raw_observations']} collections, "
        f"{leaderboard['coalesced_observations']} unique responses, "
        f"{leaderboard['score_changed']} score-changing exact-agent intervals; all "
        f"{leaderboard['score_changed_and_update_advanced']} coincide with advancing "
        "`updateTime`.",
        f"- Battle lists: {battle['observations']} observations for "
        f"{battle['agents']} agents; lengths {battle['length_min']}–"
        f"{battle['length_max']} (median {battle['length_median']}).",
        f"- Score-field convention resolved: "
        f"{semantics['prior_epoch_to_next_score_convention_resolved']}; "
        f"leaderboard alignment {semantics['leaderboard_alignment']['match_rate']:.1%}.",
        "",
        "## Identification",
        "",
        f"- Internal score transitions: {transitions['internal']}; "
        f"outcome-complete: {transitions['outcome_complete']} across "
        f"{transitions['complete_agents']} agents "
        f"({transitions['complete_rate_of_internal']:.1%}).",
        f"- Complete exposure contains {transitions['complete_wins']} wins, "
        f"{transitions['complete_losses']} losses, and "
        f"{transitions['complete_ties']} ties.",
        f"- Source FULL-eligible before fitting: "
        f"{identification['source_full_eligible_before_model']}; "
        f"PARTIAL-eligible: {identification['source_partial_eligible_before_model']}.",
        "",
        "## Candidate-rule validation",
        "",
    ]
    if result["models"]:
        lines.extend(
            [
                "| model | held-agent MAE | median AE | zero baseline |",
                "|---|---:|---:|---:|",
            ]
        )
        for name, model in result["models"].items():
            validation = model["validation"]
            lines.append(
                f"| {name} | {validation['mae']:.6f} | "
                f"{validation['median_absolute_error']:.6f} | "
                f"{validation['zero_change_baseline_mae']:.6f} |"
            )
        best = result["models"][identification["selected_model"]]["validation"]
        improvement = 1.0 - best["mae"] / best["zero_change_baseline_mae"]
        lines.extend(
            [
                "",
                f"The best prior-epoch model improves on predicting zero change by only "
                f"{improvement:.2%}; its MAE is {best['mae']:.6f}, far above the "
                "0.05 recovery gate.",
            ]
        )
    else:
        lines.append("No candidate model was fit because transition support was too small.")
    lines.extend(
        [
            "",
            f"Selected descriptive model: "
            f"`{identification['selected_model'] or 'none'}`. "
            "No wins-per-+1 estimate is reported unless the rule is RECOVERED.",
            "",
            "## Convention and sensitivity checks",
            "",
            f"- Alternative next-epoch convention: "
            f"{alternative['outcome_complete_transitions']} complete transitions; "
            f"best model `{alternative['selected_model'] or 'none'}`; all recovery "
            "gates do not pass.",
            f"- Excluding the first July 21 snapshot: "
            f"{sensitivity['outcome_complete_transitions']} complete transitions across "
            f"{sensitivity['complete_agents']} agents; best model "
            f"`{sensitivity['selected_model'] or 'none'}`; recovery gates still fail.",
            f"- Resident: {result['resident']['score_epochs']} observed score epochs and "
            f"{result['resident']['complete_transitions']} complete transitions.",
            "",
            "## Decision consequence",
            "",
        ]
    )
    if identification["verdict"] == "RECOVERED":
        lines.append(
            "The recovered observable rule may price proposed rating gains in wins."
        )
    else:
        lines.append(
            "The stored panel does not earn a causal wins-per-score conversion. "
            f"{result['minimum_additional_collection']}"
        )
    lines.extend(
        [
            "",
            "This was read-only. The resident and Arena were untouched.",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = [
        key for key, value in rows[0].items() if not isinstance(value, (dict, list))
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def self_test() -> None:
    games = {
        1: GameSummary(
            1,
            "a",
            {
                7: GameAgent(7, 20.0, 0, 1.0, (20.0,)),
                8: GameAgent(8, 20.0, 1, 0.0, (20.0,)),
            },
        ),
        2: GameSummary(
            2,
            "b",
            {
                7: GameAgent(7, 21.0, 1, 0.0, (20.0,)),
                8: GameAgent(8, 20.0, 0, 1.0, (21.0,)),
            },
        ),
        3: GameSummary(
            3,
            "c",
            {
                7: GameAgent(7, 21.0, 0, 1.0, (20.0,)),
                8: GameAgent(8, 20.0, 1, 0.0, (21.0,)),
            },
        ),
        4: GameSummary(
            4,
            "d",
            {
                7: GameAgent(7, 22.0, 0, 1.0, (20.0,)),
                8: GameAgent(8, 20.0, 1, 0.0, (22.0,)),
            },
        ),
    }
    epochs, missing = score_epochs(7, (1, 2, 3, 4), games)
    assert not missing
    assert [epoch.score for epoch in epochs] == [20.0, 21.0, 22.0]
    observation = BattleObservation("s", 7, "2026-01-01T00:00:00Z", "x", frozenset(games))
    assert complete_epoch(1, epochs, [observation])
    outcome = epoch_outcomes(epochs[1], games)
    assert (outcome["wins"], outcome["losses"], outcome["ties"]) == (1, 1, 0)
    rows = [
        {"agent_id": agent, "score_delta": float(net), "net_wins": net}
        for agent in range(10)
        for net in (-2, -1, 1, 2)
    ]
    fitted = cross_validate_linear(rows, ("net_wins",))
    assert fitted["validation"]["mae"] < 1e-8
    assert fitted["coefficients"][1] > 0
    print("self-test: ok")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.snapshot_root is None or args.output_dir is None:
        parser.error("--snapshot-root and --output-dir are required")

    sources = load_sources(args.snapshot_root)
    games, game_integrity_errors, unavailable_game_ids, raw_bytes_hashed = load_games(
        args.snapshot_root,
        sources["game_index"],
        sources["battle_observations"],
    )
    result = summarize(
        sources,
        games,
        game_integrity_errors,
        unavailable_game_ids,
        raw_bytes_hashed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    report_path = args.output_dir / "report.md"
    transitions_path = args.output_dir / "transitions.csv"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.write_text(markdown_report(result), encoding="utf-8")
    write_csv(transitions_path, result["transitions"]["rows"])
    print(
        json.dumps(
            {
                "verdict": result["identification"]["verdict"],
                "support": result["identification"]["support"],
                "decoded_source_games": result["source_integrity"][
                    "decoded_source_games"
                ],
                "outcome_complete_transitions": result["transitions"][
                    "outcome_complete"
                ],
                "output_dir": str(args.output_dir),
            },
            sort_keys=True,
        )
    )
    return 0 if result["source_integrity"]["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
