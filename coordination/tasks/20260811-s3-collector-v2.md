# 20260811-s3-collector-v2: implement collector v2 against the S3 bucket

- Status: assigned
- Record owner: local_claude_1
- Work owner: claude_1 (model per owner designation)
- Reviewer: local_claude_1 (cross-review) + codex_1 (second reviewer)
- Integrator: read `coordination/roster.json` on `origin/main`
- Area: cloud storage migration Phase 1-2 (spec `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md`)
- Plan: `docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` **Part B, tasks B1-B6** — binding
- Base commit: read `git rev-parse origin/main` after fetch (plan committed at or before this assignment)
- Branch: agent/claude_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-11T13:30:00Z
- Last updated UTC: 2026-08-11T11:18:00Z (real UTC; the Created stamp above is
  self-declared and runs ahead of git time — F7 class, noted, not rewritten)

## Outcome

Collector v2 running on the VM as a systemd timer: fetch new public games, pack daily,
upload append-only to `s3://troll-farm-data/games/`, with manifests, atomic cursor state,
and a comparison tool proving parity with the project_host cron. B1's platform-access
report gates the rest.

## Facts the plan could not know at write time

- Bucket name: **`troll-farm-data`** (created; 50 GB cap; folder `troll-farm-auto`).
- Data-plane credentials: service account `troll-farm-vm-writer` with storage.uploader +
  storage.viewer ONLY (append-only by construction — design for no overwrites, never
  request broader rights). The static keys reach you via the owner pasting them into your
  session; save to `~/.config/troll-farm/s3-keys.json`, chmod 600, never log or commit.
  Key file format is `yc iam access-key create --format json`: key id at
  `.access_key.key_id`, secret at `.secret`.
- The backfill upload (existing 15,291 games) is the coordinator's job from project_host
  and may still be in flight when you start — B2's smoke test must not assume
  `games/raw/backfill/` is complete; use your own `games/probe/` prefix.
- 2026-08-11 (real UTC ~11:15Z): the backfill upload is COMPLETE and verified —
  VERIFY: PASS; 16 packs / 15,291 games at `games/raw/backfill/`, 16 manifests at
  `games/manifest/`. B2's probe-prefix instruction stands unchanged. Evidence:
  `local_claude_1/verification/s3-backfill-upload-2026-08-11.md`.

## Exclusive write set

- `claude_1/` (code, reports), `coordination/messages/claude_1/`, `coordination/status/claude_1.md`
- VM: `~/.config/troll-farm/`, `~/.local/state/troll-farm/`, systemd user/system units for collector-v2
- Bucket: `games/` prefix only

## Do not touch

- No trunk commits (work on `agent/claude_1`; handoff for integration)
- No Arena/platform mutations; platform READS only, and only as B1/B4 specify
- No compute instance creation (grant period nearly spent)
- The USB/cold-archive phase is PAUSED — nothing in this task concerns it
- project_host's 05:17 cron and `data/raw/` are untouchable and keep running

## Coordination requirement

Register this task in coordd and dual-track claim/heartbeat/release per
`coordination/coordd-shadow-runbook.md` step 3 — this is the first real shadow-mode
workload; its coordd trail is P2 evidence.

## Acceptance checks

Per plan B1-B6, including: B1 report states plainly whether platform reads work
cookieless; every upload path proven by sha256 round-trip; packer deterministic;
cursor writes atomic; systemd timer at 05:47 UTC with an `exit=N` end marker;
first-day comparison published in the handoff.

## Handoff

v2 message with artifact pins: B1 report, code + tests, units, comparison output,
deviations. Reviewers as listed above.
