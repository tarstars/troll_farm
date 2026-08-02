# Arena submission history — schema and queries

Created 2026-08-02 by `claude_1` under task `20260802-arena-submission-history-registry`.
Deliverables: `cgauto/submission_history.py`, `data/analysis/arena-submission-history-inputs.json`
(input manifest), `data/analysis/arena-submission-history.json` (generated projection),
`tests/test_submission_history.py`, and the coverage report
`data/analysis/arena-submission-history-provenance-2026-08-02.md`.

## What this is for

On 2026-08-02 a "best bot" selection searched only the recent owner-directed lineage and
chose the far-denial source from a single 22.99/160 run. The complete source history shows
the exact stable preseed resident with **four** mature runs — 24.1/142, 24.77/160,
24.28/160, 23.05/171, plus a 24.4 room read of unknown sample. The far-denial repeat
terminated at 19.37, rank 73/130.

Two failure modes produced that: **lineage-scoped search** and **single-maximum
selection**. Every query here is shaped against both.

## Trust model

The immutable checkpoints, execution reports, manifests and platform reads are the sources
of truth. This registry is a **derived projection** and holds no unique evidence.

The builder reads **only** the files named in the input manifest and refuses to run if any
declared SHA-256 mismatches. It never globs a directory and never infers a fact from a
filename. Two input kinds:

| kind | how it enters | integrity check |
|---|---|---|
| `checkpoint_inputs` | a submission-scoped `schema: 1` checkpoint JSON, parsed structurally | file SHA-256 **and** the agent/submission identity inside the file must match the manifest |
| `curated_observations` | a fact that exists only in prose, transcribed by hand | evidence file SHA-256, plus a verbatim `evidence_quote` |

Facts that are not recorded anywhere are `null`. They are never reconstructed from a
filename, a neighbouring row, or a later active row. What is missing is listed explicitly
in the manifest's `unresolved` block and printed by `preflight`.

Because the projection is a pure function of the manifest plus the pinned files, `build`
takes no wall-clock reading and `build --check` proves byte-identity.

## Category axes

One flat label must never conflate strategy, lifecycle and evidence quality, so five axes
are validated independently. Enums live in `cgauto/submission_history.py`.

- **strategy** (per source, may be several): `baseline_controller`,
  `economy_planting_harvest_conversion`, `denial_opponent_resource`,
  `movement_coordination_banking_deadlock`, `workforce_training`, `search_rollout`,
  `learned_policy_value`, `packaging_slimming_runtime_parity`, `composite_other`.
- **deployment purpose**: `stable_resident_or_fallback`, `same_source_capacity_control`,
  `frozen_protocol_qualified_candidate`, `owner_directed_live_experiment`, `incident_fix`,
  `safety_restore`, `packaging_parity_resubmission`, `unknown_historical`.
- **evidence maturity** (per observation, derived — see below): `cold_start`,
  `provisional`, `mature`, `later_confirmed`, `terminal`, `invalid`.
- **disposition**: `active`, `promoted`, `retained`, `restored`, `rejected`, `failed`,
  `displaced_superseded`, `pending_unknown`.
- **comparison basis**: `same_source_repeat`, `same_era_control`, `a_a`,
  `candidate_vs_control`, `cross_era_historical`, `incomparable`; and **authority**:
  `frozen_qualified`, `owner_directed_override`, `standing_restore_authority`,
  `emergency_action`, `unknown`.

Relations are explicit fields, not filename conventions: `derived_from_source_id` on a
source, `parent_submission_id` / `replaced_by_submission_id` on a submission. Source
families are keyed by **exact SHA-256**, so two deployments of one byte-identical artifact
are one family regardless of what they were called.

## Evidence maturity is derived, not asserted

```
faults (runtime signal, unexpected row, fetch failure, identity mismatch,
        or parsed_results != matching_finished)      -> invalid   [no override can lift this]
games_finished is None                               -> provisional
games_finished <  20                                 -> cold_start
games_finished < 100                                 -> provisional
games_finished >= 100                                -> mature (terminal if flagged as the closing audit)
```

Only `mature`, `later_confirmed` and `terminal` may be used for a selection comparison.
Two hard rules that no manifest entry can bypass:

1. a faulted observation is `invalid`, full stop;
2. a `public_leaderboard` read can never be mature-class — those endpoints report no game
   count, no catastrophe count and no identity audit.

A manifest may *override* maturity only when the observation is fault-free, is not a public
leaderboard read, and carries a written reason. The projection then records
`maturity_source: "manifest_override"` so the override is visible everywhere. Exactly one
override exists today: the 24.4 pre-reset resident room read, whose sample size was never
written down.

## Runs versus reads

A source redeployed five times has five **runs**. Five checkpoints of one deployment are
one run observed five times. `representative_runs` collapses each deployment to its
largest-sample mature observation before aggregating, so "four mature runs" means four
separate deployments — not four presses of refresh.

## Queries

```sh
python3 cgauto/submission_history.py build [--check]
python3 cgauto/submission_history.py validate
python3 cgauto/submission_history.py timeline
python3 cgauto/submission_history.py current
python3 cgauto/submission_history.py source --sha256 <sha|prefix|source_id>
python3 cgauto/submission_history.py submission --id <submission-id>
python3 cgauto/submission_history.py compare-source <token> [<token> ...]
python3 cgauto/submission_history.py best [--min-finished N] [--evidence mature|any] [--scope all|<category>]
python3 cgauto/submission_history.py preflight <candidate-source-path>
```

`best` is **source-level** and ranks by the **median** of repeated mature runs, then by the
worst run — never by a maximum. It prints median, worst, best, the latest observation of
any maturity, and the set of dispositions, so a source whose every deployment was rejected
cannot top the table without saying so.

`preflight <path>` hashes the file, reports prior deployments of that **exact** hash, and
then **always** prints the unfiltered all-history comparator plus every stronger source
family with its individual runs listed. Any scope filter is echoed in a banner that states
what it excludes; `preflight` itself never runs filtered.

### Warnings

| warning | fires when |
|---|---|
| `REJECTED_SOURCE` | every deployment of the hash was rejected or failed |
| `NO_MATURE_EVIDENCE` | no run reaches the minimum finished-game gate |
| `SINGLE_MATURE_RUN` | exactly one mature run — the shape of the 2026-08-02 error |
| `MAX_EXCEEDS_MEDIAN` | best exceeds median by more than the ±0.5 arena noise band |
| `LATEST_BELOW_MEDIAN` | the newest (immature) read sits below the mature median |
| `UNKNOWN_OR_SMALL_SAMPLE_EXCLUDED` | mature-class observations were kept out for sample reasons |
| `CROSS_ERA` | its evidence comes from a field size the live agent no longer plays in |

## Acceptance evidence

```sh
python3 cgauto/submission_history.py build --check   # byte-identical rebuild
python3 cgauto/submission_history.py validate        # identities, enums, references, ordering
uv run pytest tests/test_submission_history.py       # 38 tests
```

`build --check` and `validate` were run in this worktree and pass. `uv run pytest` could
**not** be run here — this machine has neither `uv` nor `pytest` nor `pip`, so the suite was
executed with a minimal harness that provides `pytest.fixture`, `pytest.raises`, `capsys`
and `tmp_path`: 38 passed, 0 failed. The tests are ordinary pytest tests and need no
adaptation; they simply have not yet been observed under pytest itself. Whoever has the
project virtualenv should run the canonical command once and record the result.

## Boundaries observed

Read-only repository inspection only. No Arena mutation, no platform call, no source edit,
no history rewrite, no sealed-range read, no external-storage migration, no formatter over
`cgauto/` or `rust/src/bin/`, and no broad filesystem scan — file discovery is limited to
the explicit manifest.
