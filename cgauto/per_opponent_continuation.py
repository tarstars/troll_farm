#!/usr/bin/env python3
"""Compare population and identity-conditioned repeated-agent continuations."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.replay_conditioned_continuation import (
    ACTION_VERBS,
    CUTOFFS,
    MAP_FEATURES,
    PHASE_BY_CUTOFF,
    REPRESENTATIONS,
    TARGET_FIELDS,
    TARGET_SCALES,
    interval,
    numeric_fields,
    prediction_error,
    relative_reduction,
    retrieve,
    target_mean,
)


K_VALUES = (1, 3, 5)
POOL_TYPES = ("population", "identity")


def observable_first_spec(row: dict, cutoff: int) -> list[int]:
    events = sorted(
        (
            event
            for event in row.get("training_events") or []
            if int(event["ordinal"]) == 1 and int(event["turn"]) <= cutoff
        ),
        key=lambda event: int(event["turn"]),
    )
    if not events:
        return [0, 0, 0, 0]
    spec = [int(value) for value in events[0]["spec"]]
    if len(spec) != 4:
        raise ValueError(f"bad first-worker spec in {row.get('game_id')}")
    return spec


def build_examples(panel: dict) -> list[dict]:
    rows = panel.get("rows") or []
    occurrence_ids = {(int(row["agent_id"]), int(row["game_id"])) for row in rows}
    if len(rows) != 144 or len(occurrence_ids) != 144:
        raise ValueError("expected exact unique six-agent x 24-game panel")
    counts = {}
    for row in rows:
        counts.setdefault(int(row["agent_id"]), {"discovery": 0, "confirmation": 0})
        counts[int(row["agent_id"])][row["partition"]] += 1
    if len(counts) != 6 or any(
        value != {"discovery": 16, "confirmation": 8} for value in counts.values()
    ):
        raise ValueError(f"bad per-agent split counts: {counts}")

    examples = []
    for row in rows:
        opening = row.get("opening") or {}
        map_features = numeric_fields(opening, MAP_FEATURES, "map_")
        map_features["map_has_iron"] = float(bool(row["has_iron"]))
        for cutoff in CUTOFFS:
            snapshot = (row.get("snapshots") or {}).get(str(cutoff))
            if snapshot is None:
                raise ValueError(f"game {row['game_id']} has no cutoff {cutoff}")
            state_features = numeric_fields(snapshot, TARGET_FIELDS, "state_")
            recent = interval(row, cutoff - 49, cutoff)
            future = interval(row, cutoff + 1, cutoff + 50)
            history_features = dict(state_features)
            history_features.update(numeric_fields(recent, TARGET_FIELDS, "recent_"))
            actions = (row.get("scheduler") or {}).get("phase_actions", {}).get(
                PHASE_BY_CUTOFF[cutoff], {}
            )
            history_features.update(
                {
                    f"action_{verb.lower()}_rate": float(actions.get(verb, 0)) / 50.0
                    for verb in ACTION_VERBS
                }
            )
            history_features.update(
                {
                    f"first_worker_stat_{index}": float(value)
                    for index, value in enumerate(observable_first_spec(row, cutoff))
                }
            )
            examples.append(
                {
                    "agent_name": row["agent_name"],
                    "agent_id": int(row["agent_id"]),
                    "game_id": int(row["game_id"]),
                    "partition": row["partition"],
                    "cutoff": cutoff,
                    "target": {field: float(future[field]) for field in TARGET_FIELDS},
                    "features": {
                        "map": map_features,
                        "state": state_features,
                        "history": history_features,
                    },
                }
            )
    identities = {
        (row["agent_id"], row["game_id"], row["cutoff"]) for row in examples
    }
    if len(examples) != 288 or len(identities) != 288:
        raise ValueError("expected 288 unique cutoff occurrences")
    return sorted(
        examples,
        key=lambda row: (row["agent_id"], row["game_id"], row["cutoff"]),
    )


def training_pool(
    examples: list[dict], query: dict, pool_type: str, discovery_only: bool
) -> list[dict]:
    rows = [
        row
        for row in examples
        if row["cutoff"] == query["cutoff"]
        and row["game_id"] != query["game_id"]
        and (not discovery_only or row["partition"] == "discovery")
    ]
    if pool_type == "identity":
        rows = [row for row in rows if row["agent_id"] == query["agent_id"]]
    elif pool_type != "population":
        raise ValueError(f"unknown pool {pool_type}")
    return rows


def select_k(examples: list[dict]) -> tuple[dict, dict]:
    discovery = [row for row in examples if row["partition"] == "discovery"]
    selected = {}
    details = {}
    for pool_type in POOL_TYPES:
        for representation in REPRESENTATIONS:
            label = f"{pool_type}_{representation}"
            ranking = []
            for k in K_VALUES:
                errors = []
                for query in discovery:
                    training = training_pool(
                        discovery, query, pool_type, discovery_only=False
                    )
                    predicted, _neighbors = retrieve(
                        query, training, representation, k
                    )
                    errors.append(
                        prediction_error(query["target"], predicted)["normalized"]
                    )
                ranking.append(
                    {"k": k, "normalized_mae": statistics.mean(errors)}
                )
            ranking.sort(key=lambda row: (row["normalized_mae"], row["k"]))
            selected[label] = ranking[0]["k"]
            details[label] = {"selected_k": ranking[0]["k"], "ranking": ranking}
    return selected, details


def confirmation_rows(examples: list[dict], selected_k: dict) -> list[dict]:
    tests = [row for row in examples if row["partition"] == "confirmation"]
    output = []
    for query in tests:
        models = {}
        pool_sizes = {}
        for pool_type in POOL_TYPES:
            training = training_pool(examples, query, pool_type, discovery_only=True)
            if len(training) < max(K_VALUES):
                raise ValueError(f"too few {pool_type} rows for {query['game_id']}")
            pool_sizes[pool_type] = len(training)
            mean_prediction = target_mean(training)
            mean_label = f"{pool_type}_mean"
            models[mean_label] = {
                "prediction": mean_prediction,
                "neighbors": [],
                **prediction_error(query["target"], mean_prediction),
            }
            for representation in REPRESENTATIONS:
                label = f"{pool_type}_{representation}"
                predicted, neighbors = retrieve(
                    query,
                    training,
                    representation,
                    selected_k[label],
                )
                models[label] = {
                    "prediction": predicted,
                    "neighbors": neighbors,
                    **prediction_error(query["target"], predicted),
                }
        output.append(
            {
                "agent_name": query["agent_name"],
                "agent_id": query["agent_id"],
                "game_id": query["game_id"],
                "cutoff": query["cutoff"],
                "pool_sizes": pool_sizes,
                "target": query["target"],
                "models": models,
            }
        )
    return output


def metrics(rows: list[dict]) -> dict:
    model_names = tuple(rows[0]["models"])
    models = {}
    for model in model_names:
        models[model] = {
            "normalized_mae": statistics.mean(
                row["models"][model]["normalized"] for row in rows
            ),
            "per_field_mae": {
                field: statistics.mean(
                    row["models"][model]["absolute"][field] for row in rows
                )
                for field in TARGET_FIELDS
            },
        }
    identity = [row["models"]["identity_history"]["normalized"] for row in rows]
    population = [row["models"]["population_state"]["normalized"] for row in rows]
    return {
        "examples": len(rows),
        "models": models,
        "relative_reductions": {
            "identity_history_vs_population_state": relative_reduction(
                models["population_state"]["normalized_mae"],
                models["identity_history"]["normalized_mae"],
            ),
            "identity_history_vs_identity_mean": relative_reduction(
                models["identity_mean"]["normalized_mae"],
                models["identity_history"]["normalized_mae"],
            ),
        },
        "paired_wins": {
            "identity_history_vs_population_state": sum(
                first < second for first, second in zip(identity, population)
            ),
            "identity_history_vs_population_state_rate": sum(
                first < second for first, second in zip(identity, population)
            )
            / len(rows),
        },
    }


def analyze(panel: dict) -> dict:
    examples = build_examples(panel)
    selected_k, discovery_selection = select_k(examples)
    rows = confirmation_rows(examples, selected_k)
    overall = metrics(rows)
    by_cutoff = {
        str(cutoff): metrics([row for row in rows if row["cutoff"] == cutoff])
        for cutoff in CUTOFFS
    }
    agent_names = sorted({row["agent_name"] for row in rows})
    by_agent = {
        name: metrics([row for row in rows if row["agent_name"] == name])
        for name in agent_names
    }
    winning_agents = sum(
        result["models"]["identity_history"]["normalized_mae"]
        < result["models"]["population_state"]["normalized_mae"]
        for result in by_agent.values()
    )
    gates = {
        "integrity": len(examples) == 288 and len(rows) == 96,
        "identity_history_vs_population_state": (
            overall["relative_reductions"][
                "identity_history_vs_population_state"
            ]
            is not None
            and overall["relative_reductions"][
                "identity_history_vs_population_state"
            ]
            >= 0.10
        ),
        "identity_history_vs_identity_mean": (
            overall["relative_reductions"]["identity_history_vs_identity_mean"]
            is not None
            and overall["relative_reductions"]["identity_history_vs_identity_mean"]
            >= 0.05
        ),
        "turn100_identity_history_vs_population_state": (
            by_cutoff["100"]["relative_reductions"][
                "identity_history_vs_population_state"
            ]
            is not None
            and by_cutoff["100"]["relative_reductions"][
                "identity_history_vs_population_state"
            ]
            >= 0.10
        ),
        "winning_agents": winning_agents >= 4,
        "paired_wins": (
            overall["paired_wins"][
                "identity_history_vs_population_state_rate"
            ]
            >= 0.55
        ),
    }
    passed = all(gates.values())
    return {
        "schema": 1,
        "scope": "held-game per-opponent continuation feasibility; not candidate evidence",
        "agents": len(agent_names),
        "games": 144,
        "examples": len(examples),
        "split_examples": {"discovery": 192, "confirmation": 96},
        "feature_counts": {
            representation: len(examples[0]["features"][representation])
            for representation in REPRESENTATIONS
        },
        "selected_k": selected_k,
        "discovery_selection": discovery_selection,
        "confirmation": {
            "overall": overall,
            "by_cutoff": by_cutoff,
            "by_agent": by_agent,
            "identity_history_winning_agents": winning_agents,
            "rows": rows,
        },
        "gates": gates,
        "passed": passed,
        "decision": (
            "identity-conditioned history passes; distill the best-supported agent"
            if passed
            else "identity-conditioned aggregates fail; close proxy reconstruction"
        ),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(json.loads(args.panel.read_text()))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "agents": payload["agents"],
        "games": payload["games"],
        "examples": payload["examples"],
        "split_examples": payload["split_examples"],
        "feature_counts": payload["feature_counts"],
        "selected_k": payload["selected_k"],
        "confirmation": {
            "overall": payload["confirmation"]["overall"],
            "by_cutoff": payload["confirmation"]["by_cutoff"],
            "by_agent": payload["confirmation"]["by_agent"],
            "identity_history_winning_agents": payload["confirmation"][
                "identity_history_winning_agents"
            ],
        },
        "gates": payload["gates"],
        "passed": payload["passed"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

