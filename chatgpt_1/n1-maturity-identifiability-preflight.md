# N1 maturity-curve identifiability preflight

Prepared UTC: 2026-07-29T15:59:00Z
Agent: `chatgpt_1`
Canonical task: iteration-2 N1 maturity-curve measurement
Status: read-only preflight complete; analyzer implementation awaits canonical task record
Latest shared state inspected: `e38dca7c2f8be923ebfa7d398407db689d253849`

## Question

Can the already stored snapshots identify a fresh-to-mature score curve separately from pool drift, battle accumulation, and code changes?

## Evidence inspected

- `data/scripts/collect_snapshot.py`
- `data/scripts/parse_snapshot.py`
- `tests/test_collect_snapshot.py`
- `data/README.md`
- iteration-2 N1 definition in `docs/BACKLOG.md`

No live API request, raw-corpus mutation, TestSession, submission, or Arena action was used.

## What the snapshot format definitely preserves

Each immutable D61p snapshot contains:

- a raw `leaderboard.json` response;
- a normalized `players.json` containing `agent_id`, `pseudo`, `user_id`, league, global/local/source rank, leaderboard score, cohort groups and Legend order;
- one battle-list response per selected agent;
- a manifest with immutable snapshot ID and `completed_at_utc`;
- request timestamps, hashes and acquisition provenance;
- raw replay bodies in the immutable game cache.

The parser adds per-game agent ID, user ID, leaderboard score/rank at the snapshot, game results and replay-derived behaviour.

Therefore the stored data can support:

1. repeated score/rank observations keyed by exact `agent_id` and snapshot timestamp;
2. detection of score-frozen intervals where rank or league size moves;
3. detection of discrete leaderboard recomputation events;
4. snapshot fixed effects for pool-wide movement;
5. stable-agent interval filtering, because a new submission normally creates a new agent ID;
6. resident and current-yamo descriptive traces;
7. visible-battle-list growth between snapshots, subject to truncation.

## What the normalized format does not guarantee

The normalized `players.json` does not include:

- submission creation time;
- source hash or submission ID;
- total lifetime battle count;
- leaderboard `updateTime` or any equivalent recomputation timestamp.

The collector retains the complete raw leaderboard and raw battle-list responses, so some of these fields may exist in the raw JSON, but their presence has not been made a schema invariant or test fixture requirement.

Battle lists are not an automatically valid lifetime battle counter. Repository documentation says the public endpoint returns roughly 90–230 recent battles, so list length may be right-censored. Counting unique cached games also mixes collection policy with actual battle activity.

The 8,131-game replay corpus provides rich game outcomes and exact agent IDs, but by itself does not establish the submission's birth time. The earliest observed game is only a lower/upper bound depending on collection coverage.

## Identifiability verdict

**CONDITIONALLY IDENTIFIABLE.**

The existing immutable snapshots are sufficient for a strong repeated-score panel and for separating score recomputation from rank/pool drift. They are not yet proven sufficient for a clean absolute curve against `time_since_submission` or total battle count.

Before fitting, the authorized analyzer must run a raw-field audit over every snapshot:

- list all top-level fields present in leaderboard user rows;
- list all fields present in battle-list rows;
- count availability of agent/submission creation timestamps, score update timestamps, total games/battles and stable identifiers;
- verify field semantics on the resident's known submission date and known same-code A/A cases;
- report missingness and consistency across snapshots.

### Decision tree

1. **Exact submission/agent timestamp + total battle count available:** fit the full N1 models as planned.
2. **Timestamp available, battle count censored:** fit age curves; use battle activity only as intervals/lower bounds.
3. **No submission timestamp, but repeated exact agent IDs:** fit within-agent score/recomputation and pool-drift models; use first-seen age as left-censored and do not claim an absolute maturation curve.
4. **Too few repeated exact agent IDs or score changes:** verdict `UNIDENTIFIABLE FROM CURRENT DATA`; do not estimate a 3–4 point maturity effect.

## Proposed task-record write set

- `cgauto/maturity_curve_audit.py` (new)
- task-specific tests, for example `tests/test_maturity_curve_audit.py`
- task report under the integrator-approved analysis/report path
- own coordination/status namespace

No changes should be made to collectors, raw snapshots, the resident, submission tooling or shared live-state files during the audit.

## Required first output from the analyzer

A coverage JSON/report produced before any model fit, including:

- snapshot count and timestamp span;
- raw field inventory by snapshot;
- unique users and agent IDs;
- repeated exact-agent intervals;
- known/unknown submission ages;
- battle-count source and censoring status;
- score-changing versus score-frozen intervals;
- rank-only movement intervals;
- stable resident/yamo rows;
- explicit `FULL`, `PARTIAL`, or `UNIDENTIFIABLE` determination.

## Immediate conclusion

N1 remains the correct top priority, but its first phase is a schema-and-identifiability audit rather than model fitting. The repository already contains the acquisition and parsing machinery needed to locate the data; the main uncertainty is whether the raw API payloads contain the time and battle-count fields the proposed causal interpretation requires.
