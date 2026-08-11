# 20260811-s3-cold-archive-phase3: upload the USB bulk trees to S3 (spec Phase 3)

- Status: done (upload + verification); Phase 4 read layer NOT started
- Record owner: local_claude_1
- Work owner: local_claude_1 (coordinator, on project_host — the USB is host-local)
- Reviewer: open to `codex_1` / `claude_1` on request; no blocking review required
- Area: cloud storage migration Phase 3 (spec `docs/superpowers/specs/2026-08-11-cloud-storage-migration-design.md`)
- Branch: agent/local_claude_1 (record + verification), trunk for the tool
- Created UTC: 2026-08-11T12:50:00Z
- Last updated UTC: 2026-08-11T12:50:00Z

## Why this ran now, out of the planned order

The owner asked whether the `medium_data` USB still had to stay plugged in, and
activated Phase 3 on the answer. Phase 3 is the one phase that *requires* the drive
attached, and it was attached. Phases run out of numeric order here deliberately:
Phase 2 (collector v2) is still mid-build under `20260811-s3-collector-v2`.

## Outcome (achieved)

3,483 files / 9.99 GiB from `/media/tarstars/medium_data/database/troll_farm` uploaded to
`s3://troll-farm-data/archive/<path>` — per-file objects mirroring the on-USB layout, so a
Phase 4 GeeseFS mount can resolve the 2,346 absolute symlinks that point into the drive.
Manifests at `archive-manifest/<tree>.jsonl`. Frozen trees COLD, warm trees STANDARD.
VERIFY: PASS, plus an independent local recount agreeing exactly on count and bytes.

Evidence: `local_claude_1/verification/s3-archive-phase3-2026-08-11.md`.
Tool: `data/scripts/upload_archive.py` (trunk `fc58190b`).

## Exclusive write set

- `local_claude_1/`, `coordination/messages/local_claude_1/`, `coordination/tasks/` (this record)
- trunk: `data/scripts/upload_archive.py`, the spec's Phase 3 status annotation
- Bucket: `archive/` and `archive-manifest/` prefixes only — **`games/` is `claude_1`'s**

## Do not touch

- Nothing on the USB is deleted, moved or rewritten; this task only reads it
- No Arena/platform actions
- `games/` prefix belongs to the collector-v2 task

## Carried forward

- **Phase 4 (read layer) is what actually retires the drive.** Until GeeseFS mounts the
  bucket at `/media/tarstars/medium_data`, detaching still dangles 2,346 symlinks and
  fails ~20 frozen-analysis seal tests. `geesefs` 0.35.0 is in the Yandex apt repo; the
  mount point is root-owned, so cut-over needs sudo and is cleanest with the drive off.
- **Cost watch for Phase 4:** the frozen trees are COLD; if seal tests read them through
  the mount on every run, per-retrieval charges want measuring before that is routine.
- **B9 decided here: defer untracking** the 325 tracked files under gitignored `data/raw/`
  until Phase 2 cut-over (precondition "S3 canonical for raw dumps" unmet). Newly
  established: no test reads those paths, so the eventual removal is low-risk.
