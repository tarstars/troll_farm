"""Tests for the Arena submission history registry.

The regression fixture at the bottom is the point of the whole module: it encodes the
2026-08-02 selection error so that a future `preflight` cannot repeat it silently.
"""

from __future__ import annotations

import copy
import json
import os

import pytest

from cgauto import submission_history as sh


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def registry() -> dict:
    return sh.build(sh.DEFAULT_MANIFEST)


def _synthetic_registry() -> dict:
    """A minimal well-formed registry that individual tests then corrupt."""
    return {
        "schema_version": sh.SCHEMA_VERSION,
        "sources": [
            {
                "source_id": "alpha",
                "family_id": "a" * 64,
                "path": "x/alpha.rs",
                "bytes": 10,
                "sha256": "a" * 64,
                "language": "rust",
                "recoverability": "in_repo",
                "derived_from_source_id": None,
                "strategy_categories": ["baseline_controller"],
                "notes": None,
            }
        ],
        "submissions": [
            {
                "record_id": "submission-1",
                "submission_id": 1,
                "agent_id": 100,
                "source_id": "alpha",
                "source_attribution_confidence": "hash_verified_in_report",
                "deployed_at": None,
                "era_id": "legend-107",
                "deployment_purpose": "stable_resident_or_fallback",
                "comparison_basis": "same_source_repeat",
                "authority": "frozen_qualified",
                "parent_submission_id": None,
                "replaced_by_submission_id": None,
                "task_id": None,
                "protocol_id": None,
                "disposition": "retained",
                "disposition_rationale": None,
                "provenance": ["docs/somewhere.md"],
                "notes": None,
            }
        ],
        "observations": [
            {
                "observation_id": "obs-1",
                "submission_id": 1,
                "record_id": None,
                "agent_id": 100,
                "observed_at": "2026-07-18T00:00:00Z",
                "observed_at_precision": "exact",
                "observation_scope": "submission_scoped",
                "games_finished": 160,
                "games_pending": 0,
                "score": 24.0,
                "rank": 20,
                "field_size": 107,
                "division_index": 5,
                "wins": None,
                "ties": None,
                "losses": None,
                "mean_margin": None,
                "catastrophic_losses": None,
                "catastrophic_rate": None,
                "negative_margin_mass": None,
                "runtime_faults": 0,
                "identity_faults": 0,
                "is_terminal_audit": True,
                "evidence_maturity": "terminal",
                "maturity_source": "sample_rule",
                "evidence_kind": "checkpoint_json",
                "evidence_path": "x/obs1.json",
                "evidence_sha256": "b" * 64,
                "evidence_quote": None,
            }
        ],
        "unresolved": [],
        "eras": [],
    }


# ---------------------------------------------------------------------------
# Build determinism and manifest integrity
# ---------------------------------------------------------------------------


def test_build_is_deterministic(registry: dict) -> None:
    again = sh.build(sh.DEFAULT_MANIFEST)
    assert sh.dumps(registry) == sh.dumps(again)


def test_checked_in_projection_matches_a_fresh_build(registry: dict) -> None:
    with open(sh.DEFAULT_REGISTRY, "r", encoding="utf-8") as handle:
        assert handle.read() == sh.dumps(registry)


def test_build_refuses_a_hash_mismatch(tmp_path) -> None:
    manifest = sh.load_manifest(sh.DEFAULT_MANIFEST)
    manifest["checkpoint_inputs"][0]["sha256"] = "0" * 64
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(sh.ManifestError, match="hash mismatch"):
        sh.build(str(path))


def test_build_refuses_an_identity_mismatch(tmp_path) -> None:
    manifest = sh.load_manifest(sh.DEFAULT_MANIFEST)
    manifest["checkpoint_inputs"][0]["expect_agent_id"] = 1
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(sh.ManifestError, match="identity mismatch"):
        sh.build(str(path))


def test_build_refuses_a_missing_in_repo_source(tmp_path) -> None:
    manifest = sh.load_manifest(sh.DEFAULT_MANIFEST)
    manifest["sources"][0]["path"] = "cgauto/submissions/does-not-exist.min.rs"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(sh.ManifestError, match="declared in_repo but missing"):
        sh.build(str(path))


def test_real_registry_validates(registry: dict) -> None:
    assert sh.validate(registry) == []


def test_observations_are_in_deterministic_order(registry: dict) -> None:
    keys = [(o["observed_at"] or "", o["observation_id"]) for o in registry["observations"]]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------


def test_duplicate_submission_id_is_rejected() -> None:
    reg = _synthetic_registry()
    dupe = copy.deepcopy(reg["submissions"][0])
    dupe["record_id"] = "submission-1-copy"
    dupe["agent_id"] = 101
    reg["submissions"].append(dupe)
    assert any("duplicate submission_id: 1" in p for p in sh.validate(reg))


def test_duplicate_agent_id_is_rejected() -> None:
    reg = _synthetic_registry()
    dupe = copy.deepcopy(reg["submissions"][0])
    dupe["record_id"] = "submission-2"
    dupe["submission_id"] = 2
    reg["submissions"].append(dupe)
    assert any("duplicate agent_id: 100" in p for p in sh.validate(reg))


def test_duplicate_observation_id_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["observations"].append(copy.deepcopy(reg["observations"][0]))
    assert any("duplicate observation_id" in p for p in sh.validate(reg))


def test_conflicting_hash_across_sources_is_rejected() -> None:
    reg = _synthetic_registry()
    clash = copy.deepcopy(reg["sources"][0])
    clash["source_id"] = "beta"
    reg["sources"].append(clash)
    assert any("conflicting hash" in p for p in sh.validate(reg))


def test_unknown_strategy_category_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["sources"][0]["strategy_categories"] = ["definitely_not_a_category"]
    assert any("unknown strategy category" in p for p in sh.validate(reg))


def test_unknown_disposition_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["submissions"][0]["disposition"] = "vibes"
    assert any("unknown disposition" in p for p in sh.validate(reg))


def test_missing_provenance_link_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["submissions"][0]["source_id"] = "no-such-source"
    assert any("does not resolve" in p for p in sh.validate(reg))


def test_dangling_replaced_by_reference_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["submissions"][0]["replaced_by_submission_id"] = 999
    assert any("replaced_by_submission_id 999 does not resolve" in p for p in sh.validate(reg))


def test_observation_without_any_owner_is_rejected() -> None:
    reg = _synthetic_registry()
    reg["observations"][0]["submission_id"] = None
    reg["observations"][0]["record_id"] = None
    assert any("neither submission_id nor record_id" in p for p in sh.validate(reg))


# ---------------------------------------------------------------------------
# Evidence maturity — acceptance rule 6
# ---------------------------------------------------------------------------


def test_faulted_observation_cannot_be_mature() -> None:
    reg = _synthetic_registry()
    reg["observations"][0]["identity_faults"] = 1
    assert any("faulted observation promoted" in p for p in sh.validate(reg))


def test_public_leaderboard_read_cannot_be_mature() -> None:
    reg = _synthetic_registry()
    reg["observations"][0]["observation_scope"] = "public_leaderboard"
    assert any("public leaderboard read promoted" in p for p in sh.validate(reg))


def test_classify_maturity_rules() -> None:
    common = {"is_terminal_audit": False, "override": None, "override_allowed": False}
    assert sh.classify_maturity(games_finished=200, faults=True, **common)[0] == "invalid"
    assert sh.classify_maturity(games_finished=None, faults=False, **common)[0] == "provisional"
    assert sh.classify_maturity(games_finished=9, faults=False, **common)[0] == "cold_start"
    assert sh.classify_maturity(games_finished=63, faults=False, **common)[0] == "provisional"
    assert sh.classify_maturity(games_finished=160, faults=False, **common)[0] == "mature"
    assert (
        sh.classify_maturity(
            games_finished=160, faults=False, is_terminal_audit=True, override=None,
            override_allowed=False,
        )[0]
        == "terminal"
    )


def test_maturity_override_is_refused_when_not_allowed() -> None:
    with pytest.raises(sh.ManifestError, match="override refused"):
        sh.classify_maturity(
            games_finished=None,
            faults=False,
            is_terminal_audit=False,
            override="mature",
            override_allowed=False,
        )


def test_a_fault_beats_an_override() -> None:
    maturity, source = sh.classify_maturity(
        games_finished=160,
        faults=True,
        is_terminal_audit=False,
        override="mature",
        override_allowed=True,
    )
    assert maturity == "invalid"
    assert source == "fault_rule"


def test_the_nine_game_far_denial_checkpoint_is_cold_start(registry: dict) -> None:
    obs = next(o for o in registry["observations"] if o["observation_id"] == "obs-41079354-initial9")
    assert obs["games_finished"] == 9
    assert obs["evidence_maturity"] == "cold_start"


def test_the_displaced_opponent_crop_checkpoint_is_provisional(registry: dict) -> None:
    obs = next(
        o
        for o in registry["observations"]
        if o["observation_id"] == "obs-41079653-health21"
    )
    assert obs["games_finished"] == 21
    assert obs["score"] == 13.58
    assert obs["evidence_maturity"] == "provisional"
    assert obs["runtime_faults"] == 0
    assert obs["identity_faults"] == 0


def test_the_displaced_opponent_crop_repeat_is_mature(registry: dict) -> None:
    obs = next(
        o
        for o in registry["observations"]
        if o["observation_id"] == "obs-41079653-mature160"
    )
    assert obs["games_finished"] == 160
    assert obs["score"] == 23.12
    assert obs["evidence_maturity"] == "mature"
    assert obs["runtime_faults"] == 0
    assert obs["identity_faults"] == 0


def test_the_live_banana_factory_checkpoint_is_clean_but_provisional(registry: dict) -> None:
    obs = next(
        o
        for o in registry["observations"]
        if o["observation_id"] == "obs-41081195-reconvergence98"
    )
    assert obs["games_finished"] == 98
    assert obs["score"] == 12.99
    assert obs["rank"] == 127
    assert obs["field_size"] == 131
    assert obs["evidence_maturity"] == "provisional"
    assert obs["runtime_faults"] == 0
    assert obs["identity_faults"] == 0


def test_the_19_37_read_is_provisional_with_no_game_count(registry: dict) -> None:
    """It is a public-leaderboard placement row, not a "19.37/160 mature repeat"."""
    obs = next(o for o in registry["observations"] if o["observation_id"] == "obs-41079354-public-t40")
    assert obs["score"] == 19.37
    assert obs["games_finished"] is None
    assert obs["observation_scope"] == "public_leaderboard"
    assert obs["evidence_maturity"] == "provisional"
    assert obs["evidence_maturity"] not in sh.MATURE_CLASS


# ---------------------------------------------------------------------------
# Run aggregation and ranking
# ---------------------------------------------------------------------------


def test_repeated_checkpoints_of_one_deployment_count_as_one_run(registry: dict) -> None:
    """41012256 was read at 15, 60, 122 and 160 games. That is one run, not four."""
    runs, _ = sh.representative_runs(registry, "preseed-orchard-coverage-slim")
    for_41012256 = [r for r in runs if r["submission"]["submission_id"] == 41012256]
    assert len(for_41012256) == 1
    assert for_41012256[0]["observation"]["games_finished"] == 160


def test_best_is_not_ranked_by_maximum(registry: dict) -> None:
    ranked = sh.rank_sources(registry)
    by_id = {s["source_id"]: s for s in ranked}
    preseed = by_id["preseed-orchard-coverage-slim"]
    far = by_id["owner-far-denial-no-return-d3-slim"]
    assert preseed["median_score"] > far["median_score"]
    assert preseed["mature_runs"] == 4
    assert far["mature_runs"] == 1
    assert ranked.index(preseed) < ranked.index(far)


def test_sources_without_mature_evidence_sort_last(registry: dict) -> None:
    ranked = sh.rank_sources(registry)
    medians = [s["median_score"] for s in ranked]
    seen_none = False
    for median in medians:
        if median is None:
            seen_none = True
        else:
            assert not seen_none, "a scored source sorted below an unscored one"


def test_min_finished_gate_excludes_small_samples(registry: dict) -> None:
    """The funding-first 11-game 16.97 read must never enter an aggregate."""
    runs, excluded = sh.representative_runs(
        registry, "second-funding-first-diagonal-denial-slim"
    )
    scores = [r["observation"]["score"] for r in runs]
    assert scores == [16.37]
    assert 16.97 not in scores


def test_rejected_source_warning_survives_a_live_mature_repeat(registry: dict) -> None:
    ranked = sh.rank_sources(registry)
    by_id = {summary["source_id"]: summary for summary in ranked}
    opponent_crop = by_id["opponent-crop-b100-e6-slim"]
    assert opponent_crop["best_score"] == 24.89
    assert opponent_crop["mature_runs"] == 2
    assert any(w.startswith("REJECTED_SOURCE") for w in opponent_crop["warnings"])
    assert any(w.startswith("CROSS_ERA") for w in opponent_crop["warnings"])


def test_repeated_e7a_evidence_now_ranks_above_preseed_and_opponent_crop(
    registry: dict,
) -> None:
    ranked = sh.rank_sources(registry)
    assert ranked[0]["source_id"] == "preseed-e7a-lemon-near-tie"
    assert ranked[0]["mature_runs"] == 2
    assert ranked[0]["median_score"] == pytest.approx(24.41)
    assert ranked[0]["median_score"] > ranked[1]["median_score"]
    assert ranked[1]["source_id"] == "preseed-orchard-coverage-slim"
    assert ranked[2]["source_id"] == "opponent-crop-b100-e6-slim"


def test_repeated_e7a_no_longer_has_single_run_warning(registry: dict) -> None:
    ranked = sh.rank_sources(registry)
    by_id = {summary["source_id"]: summary for summary in ranked}
    e7a = by_id["preseed-e7a-lemon-near-tie"]
    assert e7a["mature_runs"] == 2
    assert not any(w.startswith("SINGLE_MATURE_RUN") for w in e7a["warnings"])


def test_cross_era_comparison_is_flagged(registry: dict) -> None:
    source = sh.resolve_source(registry, "preseed-orchard-coverage-slim")
    summary = sh.source_summary(registry, source)
    assert summary["eras"] == ["legend-104", "legend-107"]
    assert any(w.startswith("CROSS_ERA") for w in summary["warnings"])


def test_single_mature_run_is_flagged(registry: dict) -> None:
    source = sh.resolve_source(registry, "owner-far-denial-no-return-d3-slim")
    summary = sh.source_summary(registry, source)
    assert any(w.startswith("SINGLE_MATURE_RUN") for w in summary["warnings"])


def test_latest_below_median_is_flagged(registry: dict) -> None:
    source = sh.resolve_source(registry, "owner-far-denial-no-return-d3-slim")
    summary = sh.source_summary(registry, source)
    assert any(w.startswith("LATEST_BELOW_MEDIAN") for w in summary["warnings"])


def test_source_resolution_accepts_hash_prefix_and_id(registry: dict) -> None:
    by_full = sh.resolve_source(registry, "307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd")
    by_prefix = sh.resolve_source(registry, "307a0755")
    by_id = sh.resolve_source(registry, "owner-far-denial-no-return-d3-slim")
    assert by_full is by_prefix is by_id
    assert sh.resolve_source(registry, "no-such-thing") is None


# ---------------------------------------------------------------------------
# The 2026-08-02 regression — acceptance rule 4
# ---------------------------------------------------------------------------


def test_far_denial_preflight_reproduces_the_selection_incident(registry, capsys) -> None:
    """An all-history preflight for far-denial must surface everything the human missed.

    The 2026-08-02 selection looked only at the recent owner-directed lineage and saw one
    22.99/160 run. It never saw that the preseed resident had four mature runs, three of
    them above 23. This test fails if that information stops being printed.
    """
    path = "cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs"
    exit_code = sh.main(["preflight", path])
    assert exit_code == 0
    out = capsys.readouterr().out

    # The candidate's own history, honestly labelled.
    assert "22.99" in out
    assert "19.37" in out
    assert "160" in out

    # The preseed resident's repeated mature observations named by the task record.
    assert "24.40" in out
    assert "24.10 over 142 games" in out
    assert "23.05 over 171 games" in out

    # The stronger-family section must exist and name the preseed resident.
    assert "STRONGER HISTORICAL SOURCE FAMILIES" in out
    assert "preseed-orchard-coverage-slim: median 24.19 over 4 mature run(s)" in out

    # The warning against selecting far-denial on its single 22.99 maximum.
    assert "SINGLE_MATURE_RUN" in out
    assert "LATEST_BELOW_MEDIAN" in out
    assert "A single" in out and "high historical run is NOT such a reason" in out

    # The unfiltered comparator is always printed and says so.
    assert "UNFILTERED ALL-HISTORY COMPARATOR" in out
    assert "scope used: all history, no category or lineage filter" in out


def test_preflight_on_an_unknown_source_says_so(registry, capsys, tmp_path) -> None:
    candidate = tmp_path / "brand-new.min.rs"
    candidate.write_text("fn main() {}\n", encoding="utf-8")
    assert sh.main(["preflight", str(candidate)]) == 0
    out = capsys.readouterr().out
    assert "NEVER been deployed" in out
    assert "UNFILTERED ALL-HISTORY COMPARATOR" in out


def test_scope_filter_is_printed_prominently(registry, capsys) -> None:
    assert sh.main(["best", "--scope", "denial_opponent_resource"]) == 0
    out = capsys.readouterr().out
    assert "SCOPE FILTER ACTIVE" in out
    assert "denial_opponent_resource" in out
    assert "EXCLUDE every other category" in out
    # The preseed baseline is not a denial source, so the filter must hide it —
    # which is exactly why `preflight` refuses to run filtered.
    assert "preseed-orchard-coverage-slim" not in out


def test_min_finished_is_accepted_after_best_subcommand(capsys) -> None:
    assert sh.main(["best", "--min-finished", "150", "--scope", "all"]) == 0
    out = capsys.readouterr().out
    assert "min-finished=150" in out


def test_min_finished_is_accepted_after_preflight_subcommand(capsys) -> None:
    path = "cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs"
    assert sh.main(["preflight", path, "--min-finished", "150"]) == 0
    out = capsys.readouterr().out
    assert "min-finished=150" in out


def test_every_deployment_since_the_restored_resident_era_is_covered(registry: dict) -> None:
    """Acceptance 3: no silent gaps in the era this registry is responsible for."""
    covered = {s["submission_id"] for s in registry["submissions"]}
    for submission_id in (
        41009795, 41009911, 41009991, 41012256, 41012399, 41012593,
        41012867, 41012883, 41015603, 41070584, 41070944, 41071034,
        41071067, 41071204, 41071360, 41079354, 41079653, 41081195,
        41081465, 41081503, 41085842, 41086057, 41089629, 41090606,
    ):
        assert submission_id in covered, f"submission {submission_id} is missing"
    assert registry["unresolved"], "the unresolved list must state what is NOT covered"


def test_exactly_one_submission_is_active(registry: dict) -> None:
    # This pin tracks whoever is actually deployed and must be updated by the agent that
    # changes the resident.  Sigma run 4 (2026-08-13, submission 41129543 / agent 6614096)
    # is the current live identity; the previous pin named 41090606 / 6594200, which had in
    # fact been displaced by 41113243 back on 2026-08-12 and was never re-marked -- so this
    # test was failing on `len(live) == 1` with two actives until that disposition was
    # corrected (evidence: coordination/tasks/20260812-readable-no-orchard-rerun-arena.md:147).
    live = [s for s in registry["submissions"] if s["disposition"] == "active"]
    assert len(live) == 1
    assert live[0]["submission_id"] == 41129543
    assert live[0]["agent_id"] == 6614096


def test_every_source_file_still_hashes_to_its_recorded_value(registry: dict) -> None:
    for source in registry["sources"]:
        path = os.path.join(sh.REPO_ROOT, source["path"])
        assert sh.sha256_file(path) == source["sha256"], source["source_id"]


# --- stale arena-room row must not be ingested as the run's own score -------------
#
# The checkpoint reader sets identity_clean=False when the arena room block reports a
# different agent than the deployment being measured (arena_transfer_checkpoint.py:212).
# The builder checked raw['agent_id'] and filtered_ladder['agent_id'] but never
# arena['agent_id'] -- and then took score/rank/field_size from that unchecked block.
# On sigma run 2 (41125448 / agent 6610636) the room served agent 6604529's cached row,
# so the builder recorded score 22.46 / field_size 140 with identity_faults == 0 and
# maturity 'terminal': another deployment's score, admitted to the pooled SD, flagged
# as clean.  22.46 is also 41113243's own genuine terminal score, so the corrupted value
# reads as a plausible duplicate rather than an error.

REAL_RUN2_CHECKPOINT = "data/analysis/arena-noise-band-2026-08/run2-checkpoint-terminal.json"


def _run2_entry() -> dict:
    path = os.path.join(sh.REPO_ROOT, REAL_RUN2_CHECKPOINT)
    return {
        "observation_id": "obs-41125448-terminal160",
        "path": REAL_RUN2_CHECKPOINT,
        "sha256": sh.sha256_file(path),
        "expect_agent_id": 6610636,
        "expect_submission_id": 41125448,
        "observation_scope": "submission_scoped",
        "observed_at_override": None,
        "observed_at_override_evidence": None,
        "is_terminal_audit": True,
    }


def test_stale_arena_room_row_is_faulted_not_silently_ingested() -> None:
    """A room block naming a different agent is an identity fault, so the observation
    cannot reach the mature set that feeds the pooled SD."""
    obs = sh._observation_from_checkpoint(_run2_entry())
    assert obs["identity_faults"] >= 1
    assert obs["evidence_maturity"] == "invalid"
    assert obs["evidence_maturity"] not in sh_mature_set()


def test_checkpoint_self_reported_identity_clean_is_honoured() -> None:
    """The producing tool's own verdict must not be discarded by the consumer."""
    entry = _run2_entry()
    raw = json.load(open(os.path.join(sh.REPO_ROOT, REAL_RUN2_CHECKPOINT), encoding="utf-8"))
    assert raw["identity_clean"] is False, "fixture must be a genuinely unclean read"
    obs = sh._observation_from_checkpoint(entry)
    assert obs["identity_faults"] >= 1


def sh_mature_set() -> frozenset:
    from cgauto import arena_noise_band as anb

    return anb.MATURE
