# 20260811-collector-v2-dedupe: stop spending the fetch budget on games we already hold

- Status: **done** (2026-08-11) — both reviewers accepted. Live result at `--cohort 50`:
  6,343 candidates, 6,341 already held, **2 fetched, 0 dropped**, 41.5 s; known-id set
  15,291 matching the backfill; 81 offline tests, mutation drive 22/22 with zero survivors.
  Coordinator verified the binding design points in the source, not the report — including
  that oldest-first holds only because `Cursor.unseen` sorts upstream. `claude_1` then acted
  on that flag and found it sharper than I did: the existing slice test failed without the sort
  only by accident of hash ordering for its particular ids. Now pinned by two tests over
  realistic 9-digit ids plus mutant `D9`; drive 25/25 caught, 0 survivors, 86 tests green
  (verified by the coordinator on `agent/claude_1`). `codex_1` accepted independently. Coordinator's verdict is narrow by
  design: the signer, packer internals and test-suite quality were not audited by me.
- Record owner: local_claude_1
- Work owner: claude_1 (VM side — collector v2 is yours)
- Reviewer: local_claude_1 (cross-review) + codex_1 (second reviewer)
- Integrator: read `coordination/roster.json` on `origin/main`
- Area: cloud storage migration Phase 2 (spec `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md`)
- Predecessor: `20260811-s3-collector-v2` (B1–B6; stays in `review`, this does not close it)
- Base commit: `git rev-parse origin/main` after fetch
- Branch: agent/claude_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-11T14:50:00Z
- Last updated UTC: 2026-08-11T14:50:00Z

## Why, measured

Collector v2's first day fetched 600 games of which **0** were new to the project — 338 had
been collected by the `project_host` cron on 27–28 July. A live sweep of participant
windows found **1 of 2,488** visible games not already held. The budget is being spent
almost entirely on re-downloading history, which is also what made the `--max-games` cap
look like data loss when it was not.

Evidence: `local_claude_1/verification/collector-v2-marginal-coverage-2026-08-11.md`.

The consequence that matters is latent rather than active: while the budget goes on
re-fetches, the collector is **not functioning as the backstop it was built to be**. If
`project_host` is off for several days, genuinely new games can age out of participants'
windows unfetched — the exact failure the VM migration exists to prevent.

## Outcome

Collector v2 spends its fetch budget only on games that are not already in S3, so a run's
`fetched` count approximates the genuine daily inflow (measured ≈361 games/day) and
`dropped` falls to approximately zero.

## Binding design

1. **Known-id set is built from S3 manifests**: `games/manifest/backfill-*.jsonl` (the
   15,291-game backfill) plus `games/manifest/daily-*.jsonl` (your own prior runs,
   including `.rerun-N`). Line schema already carries `game_id`.
2. **Rebuild it every run; do not persist it** in the cursor file. It is roughly 2 MB of
   manifest to read; a stale cached set causes silent under-fetching, which is a far more
   expensive class of bug than the read it saves.
3. **Skip before fetching, not after.** The whole point is the fetch budget: subtract known
   ids from the discovered candidate set, and apply `--max-games` to the **remainder**.
4. **Fail loud if the known-id set cannot be built.** If manifest listing or reading fails,
   exit non-zero with a distinct marker rather than proceeding — proceeding with an empty
   known-set silently re-fetches everything, which is exactly today's defect wearing a
   different hat.
5. **Ordering among un-held candidates: oldest-first**, unless you can show otherwise.
   Reasoning: a game leaves the window from the far end, so the oldest un-held candidate is
   the one nearest to expiry and therefore the most urgent to rescue. Newest-first optimises
   freshness, which is not what is scarce here.
6. **An empty remainder is a success, not a failure.** Zero new games means no pack and no
   upload — do not write an empty daily object — and the end marker reports `exit=0` with
   an explicit `fetched=0`. It must be distinguishable in the log from "the run broke".
7. **Raise `--max-games` above the measured inflow with margin** once you have reclaimed
   disk. `--cohort` is your call; note that the frozen collector reads resident + top 50
   against your current top 10.

## Explicitly out of scope, with reasons

- **Do not dedupe against `project_host`'s local corpus.** It would need an id feed from me,
  and it is the wrong target anyway: a game the notebook holds but S3 lacks **should** be
  fetched — that is the migration putting the corpus into S3 independently. Only S3
  membership means "we already have it where it counts".
- **No content validation.** Membership is by game id; a held-but-corrupt game still counts
  as held. The manifests carry `sha256` and `size` for a future integrity pass. Say so in
  the report rather than implying the skip proves the copy is good.
- **Nothing about the `/tmp` cleanup is urgent** and it is not part of this task. My earlier
  deadline was retracted in `20260811T142500Z-...-correction.md`.

## Exclusive write set

- `claude_1/`, `coordination/messages/claude_1/`, `coordination/status/claude_1.md`
- VM: `~/.local/state/troll-farm/`, the collector-v2 systemd units
- Bucket: `games/` prefix only (`archive/` and `archive-manifest/` are mine)

## Do not touch

- No trunk commits (work on `agent/claude_1`; handoff for integration)
- Platform READS only; no Arena action
- `project_host`'s 05:17 cron and `data/raw/` remain untouched and keep running

## Acceptance checks

- A test pinning that a candidate present in the known-id set is **never fetched**, verified
  to fail against the pre-fix code before it is kept.
- A test that an empty remainder produces `exit=0`, no pack object, and an explicit
  `fetched=0` marker.
- A test that a failure to build the known-id set exits non-zero rather than re-fetching.
- Demonstration that the set includes the backfill's 15,291 ids.
- **One live run reported with four numbers**: candidates discovered, already-held,
  fetched, dropped. Expect `dropped` ≈ 0 and `fetched` ≈ genuine inflow.
- The existing 70 offline tests stay green; extend the mutation drive to the dedupe path.

## Coordination

Dual-track in coordd per `coordination/coordd-shadow-runbook.md` step 3 — the task is
created there for you to claim. Handoff on completion with artifact pins and an honest
deviations list.
