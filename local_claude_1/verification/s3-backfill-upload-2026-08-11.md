# S3 backfill upload — execution and verification record

- Date (real UTC): 2026-08-11, upload window ~11:12–11:15Z
- Operator: `local_claude_1` (coordinator), on `project_host`
- Plan: `docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` Part A, task A4
- Task thread: `20260811-s3-collector-v2`
- Network gate: cleared by the owner's explicit word this session ("wifi is on") — the
  only accepted clearance under the metered-network rule (plan A4). No automated
  detection was used or trusted.

## What ran

```
.venv/bin/python3 data/scripts/upload_backfill.py \
  --staging ~/.cache/troll-farm/s3-backfill --bucket troll-farm-data
```

- Uploader: `data/scripts/upload_backfill.py` at trunk `0d02c8b6` (introduced `98ef7f17`).
- Credentials: `~/.config/yandex-cloud/keys/agent-s3.json` (admin SA `troll-farm-agent`;
  file mode 0600; contents never read into any log or artifact).
- Staging preflight (same session, before launch): `packs/` + `manifests/` +
  `summary.json`; `du` 672M; `summary.json` `total_games` 15291 across 16 packs
  (15×1000 + 291) — matches the 2026-08-11 handover inventory exactly.

## Uploader output, verbatim

```
uploaded 32 objects
remote: 16 packs (expect 16), 16 manifests (expect 16)
spot-check pack-000000.jsonl.gz: sha256 MATCH
spot-check pack-000005.jsonl.gz: sha256 MATCH
spot-check pack-000010.jsonl.gz: sha256 MATCH
manifest lines: 15291 (expect 15291)
VERIFY: PASS
```

Exit code: 0.

## What this establishes

- `s3://troll-farm-data/games/raw/backfill/pack-000000..000015.jsonl.gz` (16 objects)
  and `s3://troll-farm-data/games/manifest/backfill-*.jsonl` (16 objects) are complete.
- Verification was end-to-end, not upload-side bookkeeping: remote listing counts,
  three full pack re-downloads sha256-compared against the local summary, and manifest
  line totals compared to the packed game count.
- Staging remains untouched at `~/.cache/troll-farm/s3-backfill/` (nothing is deleted
  anywhere, per the plan's standing constraint).
- Given `claude_1`'s B1 retention finding (a replay is anonymously readable only while
  a participant's battle window still holds it, `H_CONSISTENT` 7/7; 5 of 8 sampled
  VM-cached ids already irretrievable), this corpus is partly irreplaceable — it is now
  durably off-host.
