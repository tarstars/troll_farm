"""Canonical Arena submission history: build, validate and query.

Why this exists
---------------
On 2026-08-02 a "best bot" selection searched only the recent owner-directed lineage and
picked the far-denial source from a single 22.99/160 run.  It never compared the complete
source history, where the exact stable preseed resident had *repeated* mature runs at 24.4,
24.1/142, 24.77/160, 24.28/160 and 23.05/171.  The repeat terminated at 19.37.

The two failure modes were lineage-scoped search and single-maximum selection.  Every query
here is built to make both hard:

* `best` and `preflight` are **source-level, not run-level** — they aggregate repeated
  deployments of one exact SHA-256 and report median / range / worst, never the maximum
  alone;
* any category or lineage filter is echoed back prominently, and `preflight` *always*
  prints the unfiltered all-history comparator table underneath whatever was filtered.

The registry is a derived projection.  The immutable checkpoints, execution reports and
platform reads named in the input manifest remain the sources of truth; this file never
writes to them and never discovers inputs by scanning the filesystem.

Usage
-----
    python3 cgauto/submission_history.py build [--check]
    python3 cgauto/submission_history.py validate
    python3 cgauto/submission_history.py timeline
    python3 cgauto/submission_history.py current
    python3 cgauto/submission_history.py source --sha256 <sha>
    python3 cgauto/submission_history.py submission --id <id>
    python3 cgauto/submission_history.py compare-source <sha-or-family> [...]
    python3 cgauto/submission_history.py best [--min-finished N] [--evidence mature]
                                              [--scope all|<strategy-category>]
    python3 cgauto/submission_history.py preflight <candidate-source-path>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
from typing import Any, Iterable

SCHEMA_VERSION = "arena-submission-history/1"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MANIFEST = os.path.join(
    REPO_ROOT, "data", "analysis", "arena-submission-history-inputs.json"
)
DEFAULT_REGISTRY = os.path.join(
    REPO_ROOT, "data", "analysis", "arena-submission-history.json"
)

# ---------------------------------------------------------------------------
# Controlled enums.  One flat label must never conflate strategy, lifecycle and
# evidence quality, so each axis is validated separately.
# ---------------------------------------------------------------------------

STRATEGY_CATEGORIES = frozenset(
    {
        "baseline_controller",
        "economy_planting_harvest_conversion",
        "denial_opponent_resource",
        "movement_coordination_banking_deadlock",
        "workforce_training",
        "search_rollout",
        "learned_policy_value",
        "packaging_slimming_runtime_parity",
        "composite_other",
    }
)

DEPLOYMENT_PURPOSES = frozenset(
    {
        "stable_resident_or_fallback",
        "same_source_capacity_control",
        "frozen_protocol_qualified_candidate",
        "owner_directed_live_experiment",
        "incident_fix",
        "safety_restore",
        "packaging_parity_resubmission",
        "unknown_historical",
    }
)

EVIDENCE_MATURITIES = frozenset(
    {
        "cold_start",
        "provisional",
        "mature",
        "later_confirmed",
        "terminal",
        "invalid",
    }
)

#: Maturities that may be used for a promotion or selection comparison.
MATURE_CLASS = frozenset({"mature", "later_confirmed", "terminal"})

DISPOSITIONS = frozenset(
    {
        "active",
        "promoted",
        "retained",
        "restored",
        "rejected",
        "failed",
        "displaced_superseded",
        "pending_unknown",
    }
)

COMPARISON_BASES = frozenset(
    {
        "same_source_repeat",
        "same_era_control",
        "a_a",
        "candidate_vs_control",
        "cross_era_historical",
        "incomparable",
    }
)

AUTHORITIES = frozenset(
    {
        "frozen_qualified",
        "owner_directed_override",
        "standing_restore_authority",
        "emergency_action",
        "unknown",
    }
)

OBSERVATION_SCOPES = frozenset(
    {"submission_scoped", "arena_room", "public_leaderboard", "projection"}
)

TIMESTAMP_PRECISIONS = frozenset({"exact", "approximate", "unknown"})

RECOVERABILITIES = frozenset({"in_repo", "external_storage", "platform_only", "lost"})

#: A read below this many finished games says more about placement than about strength.
COLD_START_GAMES = 20
#: The project's own promotion protocols treat roughly this sample as mature.
MATURE_GAMES = 100
#: Arena's own noise band (docs/STATE.md §3); differences under it are unmeasurable.
ARENA_NOISE_BAND = 0.5


class ManifestError(RuntimeError):
    """The declared inputs are unusable — never fall back to guessing."""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _resolve(path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)


def load_manifest(path: str = DEFAULT_MANIFEST) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def classify_maturity(
    *,
    games_finished: int | None,
    faults: bool,
    is_terminal_audit: bool,
    override: str | None,
    override_allowed: bool,
) -> tuple[str, str]:
    """Return ``(maturity, maturity_source)``.

    A faulted observation is ``invalid`` and no override can lift it — that is acceptance
    rule 6, and it is the one rule with no escape hatch.  An unknown sample size is
    ``provisional`` by default: not knowing how many games produced a score is not the same
    as knowing the score is settled.
    """
    if faults:
        return "invalid", "fault_rule"
    if override is not None:
        if not override_allowed:
            raise ManifestError(
                "maturity override refused: only fault-free, non-public-leaderboard "
                "observations carrying an explicit reason may be overridden"
            )
        return override, "manifest_override"
    if games_finished is None:
        return "provisional", "unknown_sample_rule"
    if games_finished < COLD_START_GAMES:
        return "cold_start", "sample_rule"
    if games_finished < MATURE_GAMES:
        return "provisional", "sample_rule"
    return ("terminal" if is_terminal_audit else "mature"), "sample_rule"


def _observation_from_checkpoint(entry: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(entry["path"])
    actual = sha256_file(path)
    if actual != entry["sha256"]:
        raise ManifestError(
            f"checkpoint hash mismatch for {entry['path']}: "
            f"manifest {entry['sha256']}, file {actual}"
        )
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    agent_id = raw.get("agent_id")
    submission_id = raw.get("submission_id")
    if agent_id != entry["expect_agent_id"] or submission_id != entry["expect_submission_id"]:
        raise ManifestError(
            f"identity mismatch in {entry['path']}: file has {agent_id}/{submission_id}, "
            f"manifest expects {entry['expect_agent_id']}/{entry['expect_submission_id']}"
        )

    arena = raw.get("arena") or {}
    summary = raw.get("summary") or {}
    runtime_faults = len(summary.get("validity_runtime_signals") or [])
    identity_faults = len(raw.get("unexpected_rows") or []) + len(
        raw.get("fetch_failures") or []
    )
    # The room read and the filtered ladder read must agree on who is deployed.
    filtered = raw.get("filtered_ladder") or {}
    if filtered.get("agent_id") not in (None, agent_id):
        identity_faults += 1

    games_finished = raw.get("matching_finished")
    parsed = raw.get("parsed_results")
    if games_finished is not None and parsed is not None and parsed != games_finished:
        # A partially parsed stream is not a clean sample.
        identity_faults += 1

    maturity, maturity_source = classify_maturity(
        games_finished=games_finished,
        faults=bool(runtime_faults or identity_faults),
        is_terminal_audit=bool(entry.get("is_terminal_audit")),
        override=None,
        override_allowed=False,
    )

    observed_at = entry.get("observed_at_override") or raw.get("observed_at")
    precision = "exact" if raw.get("observed_at") else "approximate"
    if entry.get("observed_at_override"):
        precision = "approximate"

    return {
        "observation_id": entry["observation_id"],
        "submission_id": submission_id,
        "record_id": None,
        "agent_id": agent_id,
        "observed_at": observed_at,
        "observed_at_precision": precision,
        "observation_scope": entry["observation_scope"],
        "games_finished": games_finished,
        "games_pending": raw.get("matching_pending"),
        "score": arena.get("score"),
        "rank": arena.get("rank"),
        "field_size": arena.get("total"),
        "division_index": arena.get("division_index"),
        "wins": summary.get("wins"),
        "ties": summary.get("ties"),
        "losses": summary.get("losses"),
        "mean_margin": summary.get("mean_margin"),
        "catastrophic_losses": summary.get("catastrophic_losses"),
        "catastrophic_rate": summary.get("catastrophic_rate"),
        "negative_margin_mass": summary.get("negative_margin_mass"),
        "runtime_faults": runtime_faults,
        "identity_faults": identity_faults,
        "is_terminal_audit": bool(entry.get("is_terminal_audit")),
        "evidence_maturity": maturity,
        "maturity_source": maturity_source,
        "evidence_kind": "checkpoint_json",
        "evidence_path": entry["path"],
        "evidence_sha256": entry["sha256"],
        "evidence_quote": None,
    }


def _observation_from_curated(entry: dict[str, Any]) -> dict[str, Any]:
    path = _resolve(entry["evidence_path"])
    actual = sha256_file(path)
    if actual != entry["evidence_sha256"]:
        raise ManifestError(
            f"evidence hash mismatch for {entry['evidence_path']}: "
            f"manifest {entry['evidence_sha256']}, file {actual}"
        )

    runtime_faults = entry.get("runtime_faults")
    identity_faults = entry.get("identity_faults")
    faults = bool(runtime_faults) or bool(identity_faults)

    override = entry.get("evidence_maturity_override")
    override_allowed = (
        override is not None
        and not faults
        and bool(entry.get("evidence_maturity_override_reason"))
        and entry["observation_scope"] != "public_leaderboard"
    )
    maturity, maturity_source = classify_maturity(
        games_finished=entry.get("games_finished"),
        faults=faults,
        is_terminal_audit=bool(entry.get("is_terminal_audit")),
        override=override,
        override_allowed=override_allowed,
    )

    return {
        "observation_id": entry["observation_id"],
        "submission_id": entry.get("submission_id"),
        "record_id": entry.get("record_id"),
        "agent_id": entry.get("agent_id"),
        "observed_at": entry.get("observed_at"),
        "observed_at_precision": entry.get("observed_at_precision", "unknown"),
        "observation_scope": entry["observation_scope"],
        "games_finished": entry.get("games_finished"),
        "games_pending": entry.get("games_pending"),
        "score": entry.get("score"),
        "rank": entry.get("rank"),
        "field_size": entry.get("field_size"),
        "division_index": entry.get("division_index"),
        "wins": entry.get("wins"),
        "ties": entry.get("ties"),
        "losses": entry.get("losses"),
        "mean_margin": entry.get("mean_margin"),
        "catastrophic_losses": entry.get("catastrophic_losses"),
        "catastrophic_rate": entry.get("catastrophic_rate"),
        "negative_margin_mass": entry.get("negative_margin_mass"),
        "runtime_faults": runtime_faults,
        "identity_faults": identity_faults,
        "is_terminal_audit": bool(entry.get("is_terminal_audit")),
        "evidence_maturity": maturity,
        "maturity_source": maturity_source,
        "evidence_kind": "curated",
        "evidence_path": entry["evidence_path"],
        "evidence_sha256": entry["evidence_sha256"],
        "evidence_quote": entry.get("evidence_quote"),
        "maturity_override_reason": entry.get("evidence_maturity_override_reason"),
    }


def build(manifest_path: str = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Generate the projection.  Deterministic: no wall clock, no directory scan."""
    manifest = load_manifest(manifest_path)
    manifest_sha256 = sha256_file(manifest_path)

    sources = []
    for entry in manifest["sources"]:
        path = _resolve(entry["path"])
        recorded = entry["sha256"]
        if os.path.exists(path):
            actual = sha256_file(path)
            if actual != recorded:
                raise ManifestError(
                    f"source hash mismatch for {entry['path']}: "
                    f"manifest {recorded}, file {actual}"
                )
            recoverability = entry.get("recoverability", "in_repo")
            bytes_on_disk = os.path.getsize(path)
            if bytes_on_disk != entry["bytes"]:
                raise ManifestError(
                    f"source size mismatch for {entry['path']}: "
                    f"manifest {entry['bytes']}, file {bytes_on_disk}"
                )
        else:
            if entry.get("recoverability") == "in_repo":
                raise ManifestError(
                    f"source declared in_repo but missing: {entry['path']}"
                )
            recoverability = entry.get("recoverability", "lost")
        sources.append(
            {
                "source_id": entry["source_id"],
                "family_id": recorded,  # source families are keyed by exact SHA-256
                "path": entry["path"],
                "bytes": entry["bytes"],
                "sha256": recorded,
                "language": entry.get("language"),
                "recoverability": recoverability,
                "derived_from_source_id": entry.get("derived_from_source_id"),
                "strategy_categories": sorted(entry.get("strategy_categories") or []),
                "notes": entry.get("notes"),
            }
        )

    submissions = []
    for entry in manifest["submissions"]:
        submissions.append(
            {
                "record_id": entry.get("record_id")
                or f"submission-{entry['submission_id']}",
                "submission_id": entry.get("submission_id"),
                "agent_id": entry.get("agent_id"),
                "source_id": entry.get("source_id"),
                "source_attribution_confidence": entry.get(
                    "source_attribution_confidence", "unknown"
                ),
                "deployed_at": entry.get("deployed_at"),
                "era_id": entry.get("era_id"),
                "deployment_purpose": entry["deployment_purpose"],
                "comparison_basis": entry["comparison_basis"],
                "authority": entry["authority"],
                "parent_submission_id": entry.get("parent_submission_id"),
                "replaced_by_submission_id": entry.get("replaced_by_submission_id"),
                "task_id": entry.get("task_id"),
                "protocol_id": entry.get("protocol_id"),
                "disposition": entry["disposition"],
                "disposition_rationale": entry.get("disposition_rationale"),
                "provenance": list(entry.get("provenance") or []),
                "notes": entry.get("notes"),
            }
        )

    observations = [
        _observation_from_checkpoint(entry) for entry in manifest["checkpoint_inputs"]
    ]
    observations += [
        _observation_from_curated(entry) for entry in manifest["curated_observations"]
    ]
    observations.sort(key=lambda o: (o["observed_at"] or "", o["observation_id"]))

    registry = {
        "schema_version": SCHEMA_VERSION,
        "generator": "cgauto/submission_history.py",
        "manifest_path": os.path.relpath(manifest_path, REPO_ROOT),
        "manifest_sha256": manifest_sha256,
        "counts": {
            "sources": len(sources),
            "submissions": len(submissions),
            "observations": len(observations),
            "unresolved": len(manifest.get("unresolved") or []),
        },
        "eras": manifest.get("eras", []),
        "sources": sorted(sources, key=lambda s: s["source_id"]),
        "submissions": sorted(
            submissions, key=lambda s: (s["submission_id"] or 0, s["record_id"])
        ),
        "observations": observations,
        "unresolved": list(manifest.get("unresolved") or []),
    }
    return registry


def dumps(registry: dict[str, Any]) -> str:
    return json.dumps(registry, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------


def validate(registry: dict[str, Any]) -> list[str]:
    problems: list[str] = []

    by_source_id: dict[str, dict[str, Any]] = {}
    by_sha: dict[str, str] = {}
    for source in registry["sources"]:
        sid = source["source_id"]
        if sid in by_source_id:
            problems.append(f"duplicate source_id: {sid}")
        by_source_id[sid] = source
        sha = source["sha256"]
        if sha in by_sha and by_sha[sha] != sid:
            problems.append(
                f"conflicting hash: {sha} claimed by both {by_sha[sha]} and {sid}"
            )
        by_sha[sha] = sid
        if source["recoverability"] not in RECOVERABILITIES:
            problems.append(f"{sid}: bad recoverability {source['recoverability']!r}")
        for category in source["strategy_categories"]:
            if category not in STRATEGY_CATEGORIES:
                problems.append(f"{sid}: unknown strategy category {category!r}")
        parent = source["derived_from_source_id"]
        if parent is not None and parent not in {s["source_id"] for s in registry["sources"]}:
            problems.append(f"{sid}: derived_from_source_id {parent!r} does not resolve")

    seen_submission_ids: set[int] = set()
    seen_agent_ids: set[int] = set()
    seen_record_ids: set[str] = set()
    known_submission_ids = {
        s["submission_id"] for s in registry["submissions"] if s["submission_id"]
    }
    for sub in registry["submissions"]:
        rid = sub["record_id"]
        if rid in seen_record_ids:
            problems.append(f"duplicate record_id: {rid}")
        seen_record_ids.add(rid)

        sid = sub["submission_id"]
        if sid is not None:
            if sid in seen_submission_ids:
                problems.append(f"duplicate submission_id: {sid}")
            seen_submission_ids.add(sid)

        aid = sub["agent_id"]
        if aid is not None:
            if aid in seen_agent_ids:
                problems.append(f"duplicate agent_id: {aid}")
            seen_agent_ids.add(aid)

        if sub["source_id"] is not None and sub["source_id"] not in by_source_id:
            problems.append(f"{rid}: source_id {sub['source_id']!r} does not resolve")
        if sub["deployment_purpose"] not in DEPLOYMENT_PURPOSES:
            problems.append(f"{rid}: unknown deployment_purpose {sub['deployment_purpose']!r}")
        if sub["disposition"] not in DISPOSITIONS:
            problems.append(f"{rid}: unknown disposition {sub['disposition']!r}")
        if sub["comparison_basis"] not in COMPARISON_BASES:
            problems.append(f"{rid}: unknown comparison_basis {sub['comparison_basis']!r}")
        if sub["authority"] not in AUTHORITIES:
            problems.append(f"{rid}: unknown authority {sub['authority']!r}")
        for field in ("parent_submission_id", "replaced_by_submission_id"):
            ref = sub[field]
            if ref is not None and ref not in known_submission_ids:
                problems.append(f"{rid}: {field} {ref} does not resolve")

    seen_observation_ids: set[str] = set()
    known_record_ids = {s["record_id"] for s in registry["submissions"]}
    for obs in registry["observations"]:
        oid = obs["observation_id"]
        if oid in seen_observation_ids:
            problems.append(f"duplicate observation_id: {oid}")
        seen_observation_ids.add(oid)

        if obs["submission_id"] is not None:
            if obs["submission_id"] not in known_submission_ids:
                problems.append(f"{oid}: submission_id {obs['submission_id']} does not resolve")
        elif obs["record_id"] is not None:
            if obs["record_id"] not in known_record_ids:
                problems.append(f"{oid}: record_id {obs['record_id']!r} does not resolve")
        else:
            problems.append(f"{oid}: neither submission_id nor record_id is set")

        if obs["evidence_maturity"] not in EVIDENCE_MATURITIES:
            problems.append(f"{oid}: unknown evidence_maturity {obs['evidence_maturity']!r}")
        if obs["observation_scope"] not in OBSERVATION_SCOPES:
            problems.append(f"{oid}: unknown observation_scope {obs['observation_scope']!r}")
        if obs["observed_at_precision"] not in TIMESTAMP_PRECISIONS:
            problems.append(
                f"{oid}: unknown observed_at_precision {obs['observed_at_precision']!r}"
            )
        # Acceptance 6: a faulted observation can never be mature-class.
        if (obs["runtime_faults"] or obs["identity_faults"]) and obs[
            "evidence_maturity"
        ] in MATURE_CLASS:
            problems.append(f"{oid}: faulted observation promoted to {obs['evidence_maturity']}")
        if obs["observation_scope"] == "public_leaderboard" and obs[
            "evidence_maturity"
        ] in MATURE_CLASS:
            problems.append(
                f"{oid}: public leaderboard read promoted to {obs['evidence_maturity']}"
            )

    ordered = [(o["observed_at"] or "", o["observation_id"]) for o in registry["observations"]]
    if ordered != sorted(ordered):
        problems.append("observations are not in deterministic order")

    return problems


# ---------------------------------------------------------------------------
# Query model
# ---------------------------------------------------------------------------


def index(registry: dict[str, Any]) -> dict[str, Any]:
    subs_by_key: dict[Any, dict[str, Any]] = {}
    for sub in registry["submissions"]:
        if sub["submission_id"] is not None:
            subs_by_key[sub["submission_id"]] = sub
        subs_by_key[sub["record_id"]] = sub
    return {
        "sources_by_id": {s["source_id"]: s for s in registry["sources"]},
        "sources_by_sha": {s["sha256"]: s for s in registry["sources"]},
        "submissions": subs_by_key,
        "observations_by_submission": _group_observations(registry),
    }


def _group_observations(registry: dict[str, Any]) -> dict[Any, list[dict[str, Any]]]:
    grouped: dict[Any, list[dict[str, Any]]] = {}
    for obs in registry["observations"]:
        key = obs["submission_id"] if obs["submission_id"] is not None else obs["record_id"]
        grouped.setdefault(key, []).append(obs)
    return grouped


def resolve_source(registry: dict[str, Any], token: str) -> dict[str, Any] | None:
    """Accept a full SHA-256, a hash prefix, or a source_id."""
    idx = index(registry)
    if token in idx["sources_by_sha"]:
        return idx["sources_by_sha"][token]
    if token in idx["sources_by_id"]:
        return idx["sources_by_id"][token]
    prefix_hits = [s for s in registry["sources"] if s["sha256"].startswith(token)]
    if len(prefix_hits) == 1:
        return prefix_hits[0]
    return None


def submissions_for_source(
    registry: dict[str, Any], source_id: str
) -> list[dict[str, Any]]:
    return [s for s in registry["submissions"] if s["source_id"] == source_id]


def representative_runs(
    registry: dict[str, Any],
    source_id: str,
    *,
    min_finished: int = MATURE_GAMES,
    evidence: Iterable[str] = MATURE_CLASS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """One representative observation per deployment, plus the excluded ones.

    A source redeployed five times has five *runs*; five checkpoints of one deployment are
    one run observed five times.  Collapsing them is what makes "repeated mature runs"
    meaningful instead of a count of how often somebody pressed refresh.
    """
    idx = index(registry)
    allowed = set(evidence)
    kept: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for sub in submissions_for_source(registry, source_id):
        key = sub["submission_id"] if sub["submission_id"] is not None else sub["record_id"]
        candidates = idx["observations_by_submission"].get(key, [])
        eligible = []
        for obs in candidates:
            if obs["evidence_maturity"] not in allowed:
                continue
            if obs["games_finished"] is None or obs["games_finished"] < min_finished:
                excluded.append({"submission": sub, "observation": obs})
                continue
            eligible.append(obs)
        if eligible:
            eligible.sort(
                key=lambda o: (o["games_finished"], o["observed_at"] or "", o["observation_id"])
            )
            kept.append({"submission": sub, "observation": eligible[-1]})
    kept.sort(key=lambda r: (r["observation"]["observed_at"] or "", r["observation"]["observation_id"]))
    excluded.sort(
        key=lambda r: (r["observation"]["observed_at"] or "", r["observation"]["observation_id"])
    )
    return kept, excluded


def latest_observation(registry: dict[str, Any], source_id: str) -> dict[str, Any] | None:
    idx = index(registry)
    found: list[dict[str, Any]] = []
    for sub in submissions_for_source(registry, source_id):
        key = sub["submission_id"] if sub["submission_id"] is not None else sub["record_id"]
        found.extend(idx["observations_by_submission"].get(key, []))
    if not found:
        return None
    found.sort(key=lambda o: (o["observed_at"] or "", o["observation_id"]))
    return found[-1]


def source_summary(
    registry: dict[str, Any],
    source: dict[str, Any],
    *,
    min_finished: int = MATURE_GAMES,
    evidence: Iterable[str] = MATURE_CLASS,
) -> dict[str, Any]:
    runs, excluded = representative_runs(
        registry, source["source_id"], min_finished=min_finished, evidence=evidence
    )
    scores = [r["observation"]["score"] for r in runs if r["observation"]["score"] is not None]
    latest = latest_observation(registry, source["source_id"])
    deployments = submissions_for_source(registry, source["source_id"])

    dispositions = sorted({d["disposition"] for d in deployments})
    summary = {
        "source_id": source["source_id"],
        "family_id": source["family_id"],
        "sha256": source["sha256"],
        "bytes": source["bytes"],
        "path": source["path"],
        "strategy_categories": source["strategy_categories"],
        "dispositions": dispositions,
        "deployments": len(deployments),
        "mature_runs": len(runs),
        "runs": runs,
        "excluded_observations": excluded,
        "median_score": statistics.median(scores) if scores else None,
        "worst_score": min(scores) if scores else None,
        "best_score": max(scores) if scores else None,
        "score_range": (max(scores) - min(scores)) if len(scores) > 1 else None,
        "latest_observation": latest,
        "eras": sorted({d["era_id"] for d in deployments if d["era_id"]}),
        "evidence_eras": sorted(
            {
                run["submission"]["era_id"]
                for run in runs
                if run["submission"]["era_id"]
            }
        ),
        "warnings": [],
    }
    summary["warnings"] = _warnings(registry, summary)
    return summary


def _warnings(registry: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    dispositions = set(summary.get("dispositions") or [])
    # A later owner-directed redeployment is an action, not evidence that the frozen
    # rejection disappeared. Keep the historical warning attached to the exact source.
    if dispositions & {"rejected", "failed"}:
        warnings.append(
            "REJECTED_SOURCE: this exact hash has a rejected or failed deployment "
            f"({', '.join(sorted(dispositions))}); a high score or later owner-directed "
            "redeployment does not overturn the verdict its protocol reached against a "
            "matched control"
        )
    if summary["mature_runs"] == 0:
        warnings.append(
            "NO_MATURE_EVIDENCE: this source has never produced a mature run at the "
            "requested sample size; any score attached to it is placement noise"
        )
    elif summary["mature_runs"] == 1:
        warnings.append(
            "SINGLE_MATURE_RUN: one mature run cannot distinguish the source's level "
            "from a lucky draw; the 2026-08-02 selection error had exactly this shape"
        )
    if (
        summary["median_score"] is not None
        and summary["best_score"] is not None
        and summary["best_score"] - summary["median_score"] > ARENA_NOISE_BAND
    ):
        warnings.append(
            f"MAX_EXCEEDS_MEDIAN: best {summary['best_score']:.2f} is "
            f"{summary['best_score'] - summary['median_score']:.2f} above median "
            f"{summary['median_score']:.2f} — do not select on the maximum"
        )
    latest = summary["latest_observation"]
    if (
        latest is not None
        and latest["score"] is not None
        and summary["median_score"] is not None
        and latest["evidence_maturity"] not in MATURE_CLASS
        and latest["score"] < summary["median_score"] - ARENA_NOISE_BAND
    ):
        warnings.append(
            f"LATEST_BELOW_MEDIAN: the newest observation ({latest['score']:.2f}, "
            f"{latest['evidence_maturity']}) sits below the mature median "
            f"{summary['median_score']:.2f}; it is not yet comparable evidence, but it is "
            f"not confirmation either"
        )
    if summary["excluded_observations"]:
        warnings.append(
            f"UNKNOWN_OR_SMALL_SAMPLE_EXCLUDED: {len(summary['excluded_observations'])} "
            "observation(s) were kept out of the aggregate for unknown or insufficient "
            "game counts; see the source view"
        )
    live_eras = sorted(
        {
            s["era_id"]
            for s in registry["submissions"]
            if s["disposition"] == "active" and s["era_id"]
        }
    )
    evidence_eras = summary.get("evidence_eras") or []
    if len(evidence_eras) > 1:
        warnings.append(
            f"CROSS_ERA: its mature aggregate mixes {', '.join(evidence_eras)}; "
            "the pool changed between runs, so treat the median as historical context"
        )
    elif live_eras and evidence_eras and not set(evidence_eras) & set(live_eras):
        warnings.append(
            f"CROSS_ERA: its mature evidence comes from {', '.join(evidence_eras)} but the "
            f"live field is {', '.join(live_eras)}; the pool has changed under it"
        )
    return warnings


def rank_sources(
    registry: dict[str, Any],
    *,
    min_finished: int = MATURE_GAMES,
    evidence: Iterable[str] = MATURE_CLASS,
    scope: str = "all",
) -> list[dict[str, Any]]:
    """Rank by median of repeated mature runs — never by a single maximum."""
    summaries = []
    for source in registry["sources"]:
        if scope != "all" and scope not in source["strategy_categories"]:
            continue
        summaries.append(
            source_summary(registry, source, min_finished=min_finished, evidence=evidence)
        )
    summaries.sort(
        key=lambda s: (
            s["median_score"] is None,
            -(s["median_score"] or 0.0),
            -(s["worst_score"] or 0.0),
            -s["mature_runs"],
            s["source_id"],
        )
    )
    return summaries


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _fmt(value: Any, width: int = 0, nd: int | None = None) -> str:
    if value is None:
        text = "unknown"
    elif nd is not None and isinstance(value, (int, float)):
        text = f"{value:.{nd}f}"
    else:
        text = str(value)
    return text.rjust(width) if width else text


def render_scope_banner(scope: str, min_finished: int, evidence: Iterable[str]) -> str:
    ev = ",".join(sorted(evidence))
    if scope == "all":
        scope_line = "SCOPE: all history, no category or lineage filter"
    else:
        scope_line = (
            f"SCOPE FILTER ACTIVE >>> strategy category = {scope!r} <<< "
            "results below EXCLUDE every other category"
        )
    return (
        f"{scope_line}\n"
        f"gates: min-finished={min_finished}, evidence in {{{ev}}}\n"
        + "-" * 78
    )


def render_source_table(summaries: list[dict[str, Any]]) -> str:
    lines = [
        f"{'source_id':42} {'runs':>4} {'median':>7} {'worst':>7} {'best':>7} "
        f"{'latest':>7}  dispositions",
        "-" * 100,
    ]
    for s in summaries:
        latest = s["latest_observation"]
        latest_score = latest["score"] if latest else None
        lines.append(
            f"{s['source_id'][:42]:42} {_fmt(s['mature_runs'], 4)} "
            f"{_fmt(s['median_score'], 7, 2)} {_fmt(s['worst_score'], 7, 2)} "
            f"{_fmt(s['best_score'], 7, 2)} {_fmt(latest_score, 7, 2)}  "
            f"{', '.join(s.get('dispositions') or []) or 'unknown'}"
        )
    return "\n".join(lines)


def render_source_detail(registry: dict[str, Any], summary: dict[str, Any]) -> str:
    lines = [
        f"source_id      : {summary['source_id']}",
        f"sha256         : {summary['sha256']}",
        f"bytes          : {summary['bytes']}",
        f"path           : {summary['path']}",
        f"categories     : {', '.join(summary['strategy_categories']) or 'none'}",
        f"deployments    : {summary['deployments']}",
        f"mature runs    : {summary['mature_runs']}",
        "",
        "Deployments of this exact hash:",
    ]
    for sub in submissions_for_source(registry, summary["source_id"]):
        lines.append(
            f"  submission {_fmt(sub['submission_id'])} / agent {_fmt(sub['agent_id'])} "
            f"| {sub['deployment_purpose']} | {sub['disposition']} | era {_fmt(sub['era_id'])}"
        )
    lines.append("")
    lines.append("Observations (all maturities):")
    idx = index(registry)
    for sub in submissions_for_source(registry, summary["source_id"]):
        key = sub["submission_id"] if sub["submission_id"] is not None else sub["record_id"]
        for obs in idx["observations_by_submission"].get(key, []):
            marker = "*" if obs["evidence_maturity"] in MATURE_CLASS else " "
            lines.append(
                f" {marker} {(obs['observed_at'] or 'unknown')[:26]:26} "
                f"score {_fmt(obs['score'], 6, 2)} rank {_fmt(obs['rank'], 4)}/"
                f"{_fmt(obs['field_size'])} games {_fmt(obs['games_finished'], 4)} "
                f"[{obs['evidence_maturity']}, {obs['observation_scope']}]"
            )
    if summary["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  ! {w}" for w in summary["warnings"])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_build(args: argparse.Namespace) -> int:
    registry = build(args.manifest)
    text = dumps(registry)
    if args.check:
        if not os.path.exists(args.out):
            print(f"FAIL: {args.out} does not exist", file=sys.stderr)
            return 1
        with open(args.out, "r", encoding="utf-8") as handle:
            existing = handle.read()
        if existing != text:
            print(f"FAIL: {args.out} is not byte-identical to a fresh build", file=sys.stderr)
            return 1
        print(f"OK: {args.out} is byte-identical to a fresh build")
        return 0
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(text)
    counts = registry["counts"]
    print(
        f"wrote {args.out}: {counts['sources']} sources, {counts['submissions']} "
        f"submissions, {counts['observations']} observations, "
        f"{counts['unresolved']} unresolved items"
    )
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    registry = build(args.manifest)
    problems = validate(registry)
    if problems:
        for problem in problems:
            print(f"INVALID: {problem}", file=sys.stderr)
        return 1
    print(f"OK: {len(registry['observations'])} observations validate cleanly")
    return 0


def cmd_timeline(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    idx = index(registry)
    print(f"{'observed_at':28} {'sub':>9} {'agent':>8} {'score':>6} {'games':>6}  maturity / source")
    print("-" * 100)
    for obs in registry["observations"]:
        key = obs["submission_id"] if obs["submission_id"] is not None else obs["record_id"]
        sub = idx["submissions"].get(key, {})
        stamp = obs["observed_at"] or "unknown"
        if obs["observed_at_precision"] != "exact":
            stamp = f"~{stamp}"
        print(
            f"{stamp[:28]:28} {_fmt(obs['submission_id'], 9)} {_fmt(obs['agent_id'], 8)} "
            f"{_fmt(obs['score'], 6, 2)} {_fmt(obs['games_finished'], 6)}  "
            f"{obs['evidence_maturity']:12} {sub.get('source_id', 'unknown')}"
        )
    return 0


def cmd_current(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    live = [s for s in registry["submissions"] if s["disposition"] == "active"]
    if not live:
        print("no submission is marked active in the registry")
        return 0
    for sub in live:
        source = index(registry)["sources_by_id"].get(sub["source_id"])
        print(f"LIVE: submission {sub['submission_id']} / agent {sub['agent_id']}")
        print(f"  source     : {sub['source_id']} ({source['sha256'] if source else 'unknown'})")
        print(f"  purpose    : {sub['deployment_purpose']}  authority: {sub['authority']}")
        print(f"  task       : {_fmt(sub['task_id'])}")
        print(f"  deployed   : {_fmt(sub['deployed_at'])}")
        print()
        if source:
            summary = source_summary(
                registry, source, min_finished=args.min_finished, evidence=MATURE_CLASS
            )
            print(render_source_detail(registry, summary))
    return 0


def cmd_source(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    source = resolve_source(registry, args.sha256)
    if source is None:
        print(f"no source matches {args.sha256!r}", file=sys.stderr)
        return 1
    summary = source_summary(
        registry, source, min_finished=args.min_finished, evidence=MATURE_CLASS
    )
    print(render_source_detail(registry, summary))
    return 0


def cmd_submission(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    idx = index(registry)
    sub = idx["submissions"].get(args.id)
    if sub is None:
        print(f"no submission {args.id}", file=sys.stderr)
        return 1
    for key, value in sub.items():
        print(f"{key:32}: {value}")
    print()
    print("Observations:")
    key = sub["submission_id"] if sub["submission_id"] is not None else sub["record_id"]
    for obs in idx["observations_by_submission"].get(key, []):
        print(
            f"  {_fmt(obs['observed_at'], 26)} score {_fmt(obs['score'], 6, 2)} "
            f"games {_fmt(obs['games_finished'], 4)} [{obs['evidence_maturity']}] "
            f"<- {obs['evidence_path']}"
        )
    return 0


def cmd_compare_source(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    summaries = []
    for token in args.tokens:
        source = resolve_source(registry, token)
        if source is None:
            print(f"no source matches {token!r}", file=sys.stderr)
            return 1
        summaries.append(
            source_summary(registry, source, min_finished=args.min_finished, evidence=MATURE_CLASS)
        )
    print(render_scope_banner("all", args.min_finished, MATURE_CLASS))
    print(render_source_table(summaries))
    eras = {tuple(s["eras"]) for s in summaries}
    if len(eras) > 1:
        print()
        print(
            "! CROSS_ERA_COMPARISON: these sources were measured against different fields; "
            "their scores are not directly comparable."
        )
    for summary in summaries:
        print()
        print(render_source_detail(registry, summary))
    return 0


def cmd_best(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    summaries = rank_sources(
        registry,
        min_finished=args.min_finished,
        evidence=MATURE_CLASS if args.evidence == "mature" else EVIDENCE_MATURITIES,
        scope=args.scope,
    )
    print(render_scope_banner(args.scope, args.min_finished, MATURE_CLASS))
    print(render_source_table(summaries))
    print()
    print("Ranked by MEDIAN of repeated mature runs, then by worst run. Not by maximum.")
    for summary in summaries:
        if summary["warnings"]:
            print()
            print(f"{summary['source_id']}:")
            for warning in summary["warnings"]:
                print(f"  ! {warning}")
    return 0


def cmd_preflight(args: argparse.Namespace) -> int:
    registry = _load_registry(args)
    path = _resolve(args.path)
    if not os.path.exists(path):
        print(f"candidate source not found: {args.path}", file=sys.stderr)
        return 1
    digest = sha256_file(path)
    size = os.path.getsize(path)

    print("=" * 78)
    print("ARENA PREFLIGHT")
    print("=" * 78)
    print(f"candidate path : {args.path}")
    print(f"bytes          : {size}")
    print(f"sha256         : {digest}")
    print()

    source = index(registry)["sources_by_sha"].get(digest)
    if source is None:
        print("This exact hash has NEVER been deployed and has no history in the registry.")
        print("Treat every score attached to it as a projection, not a measurement.")
    else:
        summary = source_summary(
            registry, source, min_finished=args.min_finished, evidence=MATURE_CLASS
        )
        print(f"known source   : {source['source_id']}")
        print()
        print(render_source_detail(registry, summary))
        print()

    print("=" * 78)
    print("UNFILTERED ALL-HISTORY COMPARATOR  (always printed, never scoped)")
    print("=" * 78)
    print(render_scope_banner("all", args.min_finished, MATURE_CLASS))
    everything = rank_sources(registry, min_finished=args.min_finished, scope="all")
    print(render_source_table(everything))
    print()

    if source is not None:
        mine = next(s for s in everything if s["source_id"] == source["source_id"])
        stronger = [
            s
            for s in everything
            if s["median_score"] is not None
            and (mine["median_score"] is None or s["median_score"] > mine["median_score"])
        ]
        if stronger:
            print("STRONGER HISTORICAL SOURCE FAMILIES THAN THIS CANDIDATE:")
            for s in stronger:
                print(
                    f"  {s['source_id']}: median {s['median_score']:.2f} over "
                    f"{s['mature_runs']} mature run(s), worst {s['worst_score']:.2f}, "
                    f"best {s['best_score']:.2f}"
                )
                # Print the individual runs, not just the aggregate: a reviewer must be
                # able to see the repeats that make the aggregate trustworthy.
                for run in s["runs"]:
                    obs, sub = run["observation"], run["submission"]
                    print(
                        f"      {_fmt(obs['score'], 6, 2)} over "
                        f"{_fmt(obs['games_finished'])} games "
                        f"(submission {_fmt(sub['submission_id'])}, "
                        f"{obs['evidence_maturity']})"
                    )
                for run in s["excluded_observations"]:
                    obs, sub = run["observation"], run["submission"]
                    print(
                        f"      {_fmt(obs['score'], 6, 2)} over "
                        f"{_fmt(obs['games_finished'])} games "
                        f"(submission {_fmt(sub['submission_id'])}, "
                        f"{obs['evidence_maturity']}, EXCLUDED from the aggregate)"
                    )
            print()
            print(
                "  Selecting this candidate over the above requires a stated reason. A single"
            )
            print(
                "  high historical run is NOT such a reason — that is the 2026-08-02 error."
            )
        else:
            print("No historical source family has a higher mature median than this candidate.")
        print()
        if mine["warnings"]:
            print("CANDIDATE WARNINGS:")
            for warning in mine["warnings"]:
                print(f"  ! {warning}")
            print()

    print("EVIDENCE GAPS RECORDED IN THE REGISTRY:")
    for item in registry["unresolved"]:
        print(f"  - {item['item']}")
        print(f"      reason: {item['reason']}")
    print()
    print(f"scope used: all history, no category or lineage filter; min-finished={args.min_finished}")
    return 0


def _load_registry(args: argparse.Namespace) -> dict[str, Any]:
    """Always build from the manifest so a stale checked-in projection cannot mislead."""
    return build(args.manifest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--min-finished", type=int, default=MATURE_GAMES)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="regenerate the JSON projection")
    p.add_argument("--out", default=DEFAULT_REGISTRY)
    p.add_argument("--check", action="store_true", help="fail unless the file is byte-identical")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("validate", help="check identities, categories and references")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("timeline", help="every observation in chronological order")
    p.set_defaults(func=cmd_timeline)

    p = sub.add_parser("current", help="the live submission and its source history")
    p.set_defaults(func=cmd_current)

    p = sub.add_parser("source", help="one source family in full")
    p.add_argument("--sha256", required=True, help="full hash, hash prefix, or source_id")
    p.set_defaults(func=cmd_source)

    p = sub.add_parser("submission", help="one submission record")
    p.add_argument("--id", required=True, type=int)
    p.set_defaults(func=cmd_submission)

    p = sub.add_parser("compare-source", help="compare source families side by side")
    p.add_argument("tokens", nargs="+")
    p.set_defaults(func=cmd_compare_source)

    p = sub.add_parser("best", help="source-level ranking by median of repeated mature runs")
    p.add_argument(
        "--min-finished",
        type=int,
        default=argparse.SUPPRESS,
        help="minimum finished games for a run to enter the source aggregate",
    )
    p.add_argument("--evidence", default="mature", choices=["mature", "any"])
    p.add_argument("--scope", default="all")
    p.set_defaults(func=cmd_best)

    p = sub.add_parser("preflight", help="pre-submission check for a candidate source file")
    p.add_argument("path")
    p.add_argument(
        "--min-finished",
        type=int,
        default=argparse.SUPPRESS,
        help="minimum finished games for the unfiltered historical comparator",
    )
    p.set_defaults(func=cmd_preflight)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
